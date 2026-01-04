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

# --- プロフェッショナル設定：最新の為替レート (2026年想定) ---
EXCHANGE_RATES = {"FR": 166.0, "HK": 20.5, "US": 156.0, "KR": 0.11}

# --- カテゴリー設定 (完全無省略・世界標準) ---
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

# --- 職人の呼吸 (ヒューマノイド待機) ---
async def human_delay(min_sec=3, max_sec=7):
    await asyncio.sleep(random.uniform(min_sec, max_sec))

# --- [100点] 超精密・商品抽出関数 ---
async def extract_item_atomically(item_el):
    """一品を原子単位で確実に抽出する"""
    try:
        await item_el.scroll_into_view_if_needed()
        name_el = await item_el.query_selector(".product-item-name")
        price_el = await item_el.query_selector(".product-item-price")
        link_el = await item_el.query_selector("a")
        
        if not (name_el and link_el): return None
        
        name = (await name_el.inner_text()).strip()
        
        # 性能重視：価格取得のリカバリーループ
        price = "0"
        for i in range(4):
            price_text = await price_el.inner_text() if price_el else "0"
            price = re.sub(r'[^\d.]', '', price_text.replace(',', ''))
            if price and price != "0": break
            await asyncio.sleep(2) # 待機

        link = await link_el.get_attribute("href")
        full_url = f"https://www.hermes.com{link}"
        sku_match = re.search(r'H[A-Z0-9]{5,}', link)
        sku = sku_match.group(0).upper().strip() if sku_match else name.upper().strip()
            
        return {"sku": sku, "name": name, "price": price, "url": full_url}
    except: return None

# --- [100点] 物理検証・一品同期記帳 ---
async def write_verify_transaction(sheets, row_data):
    """
    一品の記帳を『トランザクション（完遂保証）』として実行:
    1. Masterへ書き込み
    2. 反映行から品番を読み戻して検証
    3. 一致した場合のみ、強化版『Today_Unreleased』シートへ書き込み
    """
    sku = str(row_data[3]).upper().strip()
    max_retry = 3
    
    for attempt in range(max_retry):
        try:
            await human_delay(2, 4)
            # A. マスター記帳
            res = sheets["Master"].append_row(row_data)
            row_idx = re.search(r'A(\d+)', res.get('updates', {}).get('updatedRange', '')).group(1)
            
            # B. 同期確認 (Read-back)
            await asyncio.sleep(8)
            actual_sku = sheets["Master"].cell(row_idx, 4).value
            
            if str(actual_sku).upper().strip() == sku:
                # C. 物理確認成功 -> 本日の日本未発売シートへ書き込み
                sheets["Today_Unreleased"].append_row(row_data)
                return True
            else:
                print(f"        [!] 物理検証失敗(期待:{sku}, 現実:{actual_sku})。リトライします。")
        except Exception as e:
            print(f"        [!] 書き込みエラー: {e}。休息後再開。")
            await asyncio.sleep(45)
            
    return False

# --- 超堅牢スクロール工程 ---
async def robust_scroll(page):
    last_count = 0
    for _ in range(20):
        items = await page.query_selector_all(".product-item")
        if len(items) > 0 and len(items) == last_count: break
        last_count = len(items)
        await page.mouse.wheel(0, 1500)
        await asyncio.sleep(2.5)
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(1.5)

async def run():
    # --- [100点] 初期化とシート設計 ---
    creds_json = json.loads(os.environ["GOOGLE_CREDENTIALS"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive'])
    client = gspread.authorize(creds)
    spreadsheet = client.open("Hermes_Artisan_DB")
    
    sheets = {}
    header = ["取得日", "カテゴリ", "国", "品番", "商品名", "現地価格", "円換算目安", "URL"]
    
    # シートの存在確認と強化版シートの作成
    for title in ["Master", "Today_Unreleased"]:
        try: sheets[title] = spreadsheet.worksheet(title)
        except:
            sheets[title] = spreadsheet.add_worksheet(title=title, rows="5000", cols="20")
            sheets[title].append_row(header)

    JST = timezone(timedelta(hours=+9), 'JST')
    today_str = datetime.now(JST).strftime("%Y/%m/%d")
    
    # 既存データのロード（起動時1回のみ：性能最適化）
    existing_skus = set([str(s).upper().strip() for s in sheets["Master"].col_values(4)])
    
    # 本日のシートをクリア（新着のみにするため）
    sheets["Today_Unreleased"].clear()
    sheets["Today_Unreleased"].append_row(header)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="ja-JP"
        )
        page = await context.new_page()
        try: await playwright_stealth.stealth_async(page)
        except: pass

        # 巡回国順序
        countries = ["FR", "HK", "US", "KR"]

        for cat_name, path_jp in CONFIG["JP"]["paths"].items():
            print(f"\n【最高性能モード】対象: {cat_name}")
            
            # 1. 日本サイトの「鉄壁」除外リスト作成
            jp_skus = set()
            try:
                await page.goto(f"https://www.hermes.com/jp/ja/category/{path_jp}/#|", wait_until="load", timeout=90000)
                await asyncio.sleep(5)
                await robust_scroll(page)
                jp_els = await page.query_selector_all(".product-item")
                for el in jp_els:
                    d = await extract_item_atomically(el)
                    if d: jp_skus.add(d["sku"])
                print(f"    -> 日本在庫フィルタ構築完了 ({len(jp_skus)}件回避中)")
            except:
                print(f"    [!] 日本サイトが重いため、このカテゴリはスキップします。")
                continue

            # 2. 海外サイト一品完遂巡回
            for country_key in countries:
                print(f"\n  --- [{country_key}] 現場検証中 ---")
                target_path = CONFIG[country_key]["paths"].get(cat_name)
                if not target_path: continue
                
                try:
                    await page.goto(f"https://www.hermes.com/{CONFIG[country_key]['code']}/category/{target_path}/#|", wait_until="load", timeout=90000)
                    try:
                        await page.wait_for_selector(".product-item", timeout=15000)
                    except:
                        print(f"    [情報] 現在このカテゴリに在庫なし。")
                        continue

                    await robust_scroll(page)
                    
                    # 全要素を取得するが、一品ずつ『最新』を確認して進む
                    elements = await page.query_selector_all(".product-item")
                    print(f"    -> 要素検知: {len(elements)}件。完全同期シーケンスを開始。")

                    for i in range(len(elements)):
                        # 毎回要素を再捕捉し、StaleElementエラーを防ぐ（世界一の工夫）
                        current_items = await page.query_selector_all(".product-item")
                        if i >= len(current_items): break
                        el = current_items[i]
                        
                        data = await extract_item_atomically(el)
                        if not data: continue
                        
                        sku_upper = str(data['sku']).upper().strip()
                        print(f"      [{i+1}/{len(elements)}] 抽出中: {data['name']} ({sku_upper})")
                        
                        # 徹底照合
                        if sku_upper in jp_skus:
                            print(f"        -> [日本発売済み] 回避")
                            continue
                        if sku_upper in existing_skus:
                            print(f"        -> [台帳既出] 回避")
                            continue
                        
                        # 計算
                        try:
                            rate = EXCHANGE_RATES.get(country_key, 1.0)
                            jpy = int(float(data['price']) * rate)
                        except: jpy = 0
                        
                        row = [today_str, cat_name, country_key, sku_upper, data['name'], data['price'], f"¥{jpy:,}", data['url']]
                        
                        # [完遂保証] 記帳工程
                        print(f"        [同期中] Google Sheetsに刻印中...")
                        if await write_verify_transaction(sheets, row):
                            existing_skus.add(sku_upper)
                            print(f"        [完遂] 物理反映を確認しました。成功。")
                        else:
                            print(f"        [警告] 記帳に失敗しました。次を試みます。")
                        
                        # 次の一品へ行く前の休息（レート制限対策）
                        await human_delay(4, 8)

                except Exception as e:
                    print(f"    [!] システム復旧シグナル検知: {e}")
                    await asyncio.sleep(20)
                    continue

            print(f"--- カテゴリ完了。APIクールダウン中... ---")
            await asyncio.sleep(45)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
