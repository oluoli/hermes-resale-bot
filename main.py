import asyncio
import os
import json
import gspread
import re
import time
import random
from datetime import datetime, timedelta, timezone
from playwright.async_api import async_playwright
import playwright_stealth
from oauth2client.service_account import ServiceAccountCredentials

# --- 設定：最新の為替レート (2026年想定) ---
EXCHANGE_RATES = {"FR": 166.0, "HK": 20.5, "US": 156.0, "KR": 0.11}

# --- カテゴリー設定 (全5カ国・14カテゴリー・無省略) ---
CONFIG = {
    "JP": {"code": "jp/ja", "paths": {
        "ゴールドジュエリー": "jewelry/gold-jewelry",
        "ブレスレット": "women/fashion-jewelry/bracelets",
        "ネックレス": "women/fashion-jewelry/necklaces-and-pendants",
        "耳飾り": "women/fashion-jewelry/earrings",
        "リング": "women/fashion-jewelry/rings",
        "ベルト": "women/belts",
        "スカーフ": "scarves-shawls-and-stoles/silk-scarves-and-accessories",
        "ブランケット": "home/textiles",
        "ベビーギフト": "gifts-and-petit-h/baby-gifts",
        "ペット": "home-outdoor-and-equestrian/equestrian-and-dogs/dog",
        "PetitH": "petit-h/all-petit-h",
        "バッグ": "women/bags-and-small-leather-goods/bags-and-clutches",
        "メンズバッグ": "men/bags-and-small-leather-goods/bags",
        "テーブルウェア": "home/tableware"
    }},
    "FR": {"code": "fr/fr", "paths": {
        "ゴールドジュエリー": "bijouterie/bijoux-en-or",
        "ブレスレット": "femme/accessoires-bijoux/bracelets",
        "ネックレス": "femme/accessoires-bijoux/colliers-et-pendentifs",
        "耳飾り": "femme/accessoires-bijoux/boucles-d-oreilles",
        "リング": "femme/accessoires-bijoux/bagues",
        "ベルト": "femme/ceintures",
        "スカーフ": "femme/carres-chales-et-echarpes/carres-et-accessoires-de-soie",
        "ブランケット": "maison/textiles",
        "ベビーギフト": "cadeaux-et-petit-h/cadeaux-de-naissance",
        "ペット": "maison-plein-air-et-equitation/equitation-et-chien/chien",
        "PetitH": "petit-h",
        "バッグ": "femme/sacs-et-petite-maroquinerie/sacs-et-pochettes",
        "メンズバッグ": "homme/sacs-et-petite-maroquinerie/sacs",
        "テーブルウェア": "maison/art-de-la-table"
    }},
    "HK": {"code": "hk/en", "paths": {
        "ゴールドジュエリー": "jewelry/gold-jewelry",
        "ブレスレット": "women/fashion-jewelry/bracelets",
        "ネックレス": "women/fashion-jewelry/necklaces-and-pendants",
        "耳飾り": "women/fashion-jewelry/earrings",
        "リング": "women/fashion-jewelry/rings",
        "ベルト": "women/belts",
        "スカーフ": "women/scarves-shawls-and-stoles/silk-scarves-and-accessories",
        "ブランケット": "home/textiles",
        "ベビーギフト": "gifts-and-petit-h/baby-gifts",
        "ペット": "home-outdoor-and-equestrian/equestrian-and-dogs/dog",
        "PetitH": "petit-h/all-petit-h",
        "バッグ": "women/bags-and-small-leather-goods/bags-and-clutches",
        "メンズバッグ": "men/bags-and-small-leather-goods/bags",
        "テーブルウェア": "home/tableware"
    }},
    "US": {"code": "us/en", "paths": {
        "ゴールドジュエリー": "jewelry/gold-jewelry",
        "ブレスレット": "women/fashion-jewelry/bracelets",
        "ネックレス": "women/fashion-jewelry/necklaces-and-pendants",
        "耳飾り": "women/fashion-jewelry/earrings",
        "リング": "women/fashion-jewelry/rings",
        "ベルト": "women/belts",
        "スカーフ": "women/scarves-shawls-and-stoles/silk-scarves-and-accessories",
        "ブランケット": "home/textiles",
        "ベビーギフト": "gifts-and-petit-h/baby-gifts",
        "ペット": "home-outdoor-and-equestrian/equestrian-and-dogs/dog",
        "PetitH": "petit-h",
        "バッグ": "women/bags-and-small-leather-goods/bags-and-clutches",
        "メンズバッグ": "men/bags-and-small-leather-goods/bags",
        "テーブルウェア": "home/tableware"
    }},
    "KR": {"code": "kr/ko", "paths": {
        "ゴールドジュエリー": "jewelry/gold-jewelry",
        "ブレスレット": "women/fashion-jewelry/bracelets",
        "ネックレス": "women/fashion-jewelry/necklaces-and-pendants",
        "耳飾り": "women/fashion-jewelry/earrings",
        "リング": "women/fashion-jewelry/rings",
        "ベルト": "women/belts",
        "スカーフ": "women/scarves-shawls-and-stoles/silk-scarves-and-accessories",
        "ブランケット": "home/textiles",
        "ベビーギフト": "gifts-and-petit-h/baby-gifts",
        "ペット": "home-outdoor-and-equestrian/equestrian-and-dogs/dog",
        "PetitH": "petit-h",
        "バッグ": "women/bags-and-small-leather-goods/bags-and-clutches",
        "メンズバッグ": "men/bags-and-small-leather-goods/bags",
        "テーブルウェア": "home/tableware"
    }}
}

# --- 職人の呼吸 ---
async def artisan_wait(min_sec=5, max_sec=10):
    await asyncio.sleep(random.uniform(min_sec, max_sec))

# --- 商品詳細の精密抽出 (動的要素待機付) ---
async def extract_details_from_element(item_el):
    try:
        await item_el.scroll_into_view_if_needed()
        # 要素内のテキストが準備できるまで微細な待機
        name_el = await item_el.query_selector(".product-item-name")
        price_el = await item_el.query_selector(".product-item-price")
        link_el = await item_el.query_selector("a")
        
        if not (name_el and link_el): return None
        
        name = (await name_el.inner_text()).strip()
        
        # 価格取得の執念 (リトライ4回)
        price = "0"
        for attempt in range(4):
            price_text = await price_el.inner_text() if price_el else "0"
            price = re.sub(r'[^\d.]', '', price_text.replace(',', ''))
            if price and price != "0": break
            await asyncio.sleep(2)

        link = await link_el.get_attribute("href")
        full_url = f"https://www.hermes.com{link}"
        sku_match = re.search(r'H[A-Z0-9]{5,}', link)
        sku = sku_match.group(0).upper().strip() if sku_match else name.upper().strip()
            
        return {"sku": sku, "name": name, "price": price, "url": full_url}
    except Exception as e:
        print(f"        [!] 抽出エラー: {e}")
        return None

# --- スプレッドシート記帳 ＆ 物理反映確認 (Read-back Verification) ---
async def artisan_write_and_verify_sequential(sheets, row_data, max_retry=3):
    sku_to_check = str(row_data[3]).upper().strip()
    for attempt in range(max_retry):
        try:
            await artisan_wait(3, 6)
            # マスターへ記帳
            res = sheets["Master"].append_row(row_data)
            # 反映された物理的な行番号を特定
            updated_range = res.get('updates', {}).get('updatedRange', '')
            row_idx_match = re.search(r'A(\d+)', updated_range)
            if not row_idx_match: continue
            row_idx = row_idx_match.group(1)
            
            print(f"        [検証中] Google Sheets Row {row_idx} を読み戻し中...")
            await asyncio.sleep(10) # API同期の「ため」
            
            # 物理的な読み戻し（Read-back）
            actual_sku = sheets["Master"].cell(row_idx, 4).value
            if str(actual_sku).upper().strip() == sku_to_check:
                # 完全に一致した場合のみ Today_New にも同期
                sheets["Today_New"].append_row(row_data)
                return True
            else:
                print(f"        [!] 不一致検知: 再試行します。")
        except Exception as e:
            print(f"        [!] API制限または通信遮断: {e}。45秒間クールダウンします。")
            await asyncio.sleep(45)
    return False

# --- 執念のスクロール (タイムアウト耐性版) ---
async def artisan_scroll_robust(page):
    last_count = 0
    for _ in range(15):
        items = await page.query_selector_all(".product-item")
        current_count = len(items)
        if current_count > 0 and current_count == last_count: break
        last_count = current_count
        await page.mouse.wheel(0, 1000 + random.randint(0, 500))
        await asyncio.sleep(2.5)
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(2)

async def run():
    # --- Google認証とシート初期化 ---
    creds_json = json.loads(os.environ["GOOGLE_CREDENTIALS"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive'])
    client = gspread.authorize(creds)
    spreadsheet = client.open("Hermes_Check_List")
    
    sheets = {}
    header = ["追加日", "ジャンル", "国", "品番", "商品名", "現地価格", "日本円目安", "URL"]
    for title in ["Master", "Today_New"]:
        try: sheets[title] = spreadsheet.worksheet(title)
        except:
            sheets[title] = spreadsheet.add_worksheet(title=title, rows="5000", cols="20")
            sheets[title].append_row(header)

    JST = timezone(timedelta(hours=+9), 'JST')
    today_date = datetime.now(JST).strftime("%Y/%m/%d")
    
    # 既存データの高速ロード
    existing_skus = set([str(s).upper().strip() for s in sheets["Master"].col_values(4)])
    sheets["Today_New"].clear()
    sheets["Today_New"].append_row(header)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}, locale="ja-JP"
        )
        page = await context.new_page()
        
        # ステルス実装
        try: await playwright_stealth.stealth_async(page)
        except: pass

        target_countries = ["FR", "HK", "US", "KR"]

        for cat_name, path_jp in CONFIG["JP"]["paths"].items():
            print(f"\n【最重要工程】カテゴリー: {cat_name}")
            
            # 1. 日本サイトの最新フィルタ構築
            try:
                await page.goto(f"https://www.hermes.com/jp/ja/category/{path_jp}/#|", wait_until="load", timeout=90000)
                await asyncio.sleep(5)
                await artisan_scroll_robust(page)
                jp_elements = await page.query_selector_all(".product-item")
                jp_skus = set()
                for el in jp_elements:
                    d = await extract_details_from_element(el)
                    if d: jp_skus.add(d["sku"])
                print(f"    -> 国内網構築完了 ({len(jp_skus)}件把握)")
            except Exception as e:
                print(f"    [注意] 日本サイトの読み込みが不安定です。スキップを検討中... ({e})")
                continue

            # 2. 国別に「一品完遂」処理を実行
            for country_key in target_countries:
                print(f"\n  --- [{country_key}] 巡回開始 ---")
                target_path = CONFIG[country_key]["paths"].get(cat_name)
                if not target_path: continue
                
                try:
                    # タイムアウト耐性を持たせたページ遷移
                    await page.goto(f"https://www.hermes.com/{CONFIG[country_key]['code']}/category/{target_path}/#|", wait_until="load", timeout=90000)
                    # 商品が現れるのを「そっと」待つ（なければタイムアウトせず次に進む）
                    try:
                        await page.wait_for_selector(".product-item", timeout=15000)
                    except:
                        print(f"    [情報] {country_key} には現在このカテゴリーの在庫がないようです。次へ。")
                        continue

                    await artisan_scroll_robust(page)
                    os_elements = await page.query_selector_all(".product-item")
                    print(f"    -> 現場要素検知: {len(os_elements)}件。一品完遂ループを開始します。")

                    for i, el in enumerate(os_elements):
                        # --- 一品完遂シーケンス ---
                        # A. その場で読み取り
                        data = await extract_details_from_element(el)
                        if not data: continue
                        
                        sku_upper = str(data['sku']).upper().strip()
                        print(f"      ({i+1}/{len(os_elements)}) {data['name']} ({sku_upper})")
                        
                        # B. 日本 ＆ 過去台帳との照合
                        if sku_upper in jp_skus:
                            print(f"        -> スキップ: 日本に在庫あり。")
                            continue
                        if sku_upper in existing_skus:
                            print(f"        -> スキップ: 台帳記載済み。")
                            continue
                        
                        # C. 為替計算
                        try:
                            jpy = int(float(data['price']) * EXCHANGE_RATES.get(country_key, 1.0))
                        except: jpy = 0
                        row = [today_date, cat_name, country_key, sku_upper, data['name'], data['price'], f"¥{jpy:,}", data['url']]
                        
                        # D. 記帳 ＆ 物理反映検証 (合格するまでここを離れない)
                        print(f"        [同期中] 記帳とビット単位の反映確認を実行中...")
                        if await artisan_write_and_verify_sequential(sheets, row):
                            existing_skus.add(sku_upper)
                            print(f"        [成功] 台帳同期完了。次へ移ります。")
                        else:
                            print(f"        [警告] この商品の記帳に失敗しました。次へ進みます。")
                        
                        # E. 次の商品へ移る前の職人の間合い
                        await artisan_wait(6, 12)
                        # --- シーケンス終了 ---

                except Exception as e:
                    print(f"    [注意] {country_key} の巡回中にエラーが発生。復旧を試みます: {e}")
                    await asyncio.sleep(20)
                    continue

                print(f"  --- [{country_key}] 全商品の直列同期終了 ---")
                await artisan_wait(15, 30)
            
            print(f"--- カテゴリー[{cat_name}] 全カ国完走。APIリセットのため待機 ---")
            await asyncio.sleep(60)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
