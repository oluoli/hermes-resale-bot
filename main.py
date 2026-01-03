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

# --- カテゴリー設定 (一切の省略なし) ---
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

# --- 職人の呼吸 (ランダム待機) ---
async def artisan_wait(min_sec=5, max_sec=10):
    await asyncio.sleep(random.uniform(min_sec, max_sec))

# --- 商品詳細の超精密抽出 (不屈のリトライ機能付) ---
async def extract_item_details_strict(item_el):
    try:
        # 要素が画面に入るまで待つ
        await item_el.scroll_into_view_if_needed()
        await asyncio.sleep(1)
        
        name_el = await item_el.query_selector(".product-item-name")
        price_el = await item_el.query_selector(".product-item-price")
        link_el = await item_el.query_selector("a")
        
        if not (name_el and link_el): return None
        
        name = (await name_el.inner_text()).strip()
        
        # 価格取得の執念 (読み込み遅延対策)
        price = "0"
        for attempt in range(4):
            price_text = await price_el.inner_text() if price_el else "0"
            price = re.sub(r'[^\d.]', '', price_text.replace(',', ''))
            if price and price != "0": break
            await asyncio.sleep(2) # 待機時間を段階的に伸ばす

        link = await link_el.get_attribute("href")
        full_url = f"https://www.hermes.com{link}"
        sku_match = re.search(r'H[A-Z0-9]{5,}', link)
        sku = sku_match.group(0).upper().strip() if sku_match else name.upper().strip()
            
        return {"sku": sku, "name": name, "price": price, "url": full_url}
    except: return None

# --- BUYMA生鑑定 (正規化照合・ボット対策強化版) ---
async def check_buyma_unlisted_live(page, sku):
    search_url = f"https://www.buyma.com/r/-F1/{sku}/"
    try:
        print(f"        [バイマ現場鑑定] 品番 {sku} を照合中...")
        # 人間らしいマウスの動き
        await page.mouse.move(random.randint(100, 600), random.randint(100, 600))
        response = await page.goto(search_url, wait_until="networkidle", timeout=60000)
        
        if response.status != 200:
            print(f"        [!] BUYMA通信制限の疑い。安全のため既出とみなします。")
            return False

        await artisan_wait(4, 8)
        
        content = await page.content()
        no_result_msg = "該当する商品が見つかりませんでした" in content

        # おすすめ商品を弾くためのタイトル正規化照合
        # 品番とタイトルの両方からスペースや記号を消して純粋比較
        clean_sku = re.sub(r'[^A-Z0-9]', '', sku.upper())
        titles = await page.locator(".fab-product-name").all_inner_texts()
        sku_found = False
        for t in titles:
            clean_title = re.sub(r'[^A-Z0-9]', '', t.upper())
            if clean_sku in clean_title:
                sku_found = True
                break

        if no_result_msg or not sku_found:
            print(f"        [☆未掲載確定] バイマにお宝発見！")
            return True
        else:
            print(f"        [既出] 類似出品を確認。次へ進みます。")
            return False
    except: return False

# --- 記帳・物理反映確認 (究極の正確性保証) ---
async def artisan_write_and_verify_sequential(sheets, row_data, is_unlisted):
    sku_to_check = str(row_data[3]).upper().strip()
    try:
        await artisan_wait(3, 6)
        # 1. マスター台帳に記帳
        res = sheets["Master"].append_row(row_data)
        # 物理行番号の取得
        row_idx = res['updates']['updatedRange'].split('!A')[-1].split(':')[0]
        
        print(f"        [確認中] スプレッドシートへの物理反映を検証しています...")
        await asyncio.sleep(10) # Google APIの反映待ち
        
        # 2. 実際に書かれた中身を読み戻して検証
        actual_val = sheets["Master"].cell(row_idx, 4).value
        if str(actual_val).upper().strip() != sku_to_check:
            print(f"        [!] 検証失敗: データのズレを検知。リトライします。")
            return False

        # 3. 成功したら Today_New にも同期
        sheets["Today_New"].append_row(row_data)
        
        # 4. お宝判定なら BUYMA_Unlisted にも同期
        if is_unlisted:
            print(f"        [お宝記帳] BUYMA_Unlistedに記録。")
            sheets["BUYMA_Unlisted"].append_row(row_data)
            
        return True
    except Exception as e:
        print(f"        [!] APIエラー: {e}。60秒休止してリセット。")
        await asyncio.sleep(60)
        return False

# --- 職人のスクロール (全表示を保証) ---
async def artisan_scroll_full(page):
    last_count = 0
    for _ in range(15):
        items = await page.query_selector_all(".product-item")
        current_count = len(items)
        if current_count > 0 and current_count == last_count: break
        last_count = current_count
        # 大きく動かして読み込みを誘発
        await page.mouse.wheel(0, 1200 + random.randint(0, 400))
        await asyncio.sleep(3)
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(2)

async def run():
    # --- 認証とシート準備 ---
    creds_json = json.loads(os.environ["GOOGLE_CREDENTIALS"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive'])
    client = gspread.authorize(creds)
    spreadsheet = client.open("Hermes_Check_List")
    
    sheets = {}
    header = ["追加日", "ジャンル", "国", "品番", "商品名", "現地価格", "日本円目安", "URL"]
    for title in ["Master", "Today_New", "BUYMA_Unlisted"]:
        try: sheets[title] = spreadsheet.worksheet(title)
        except:
            sheets[title] = spreadsheet.add_worksheet(title=title, rows="4000", cols="20")
            sheets[title].append_row(header)

    JST = timezone(timedelta(hours=+9), 'JST')
    today_date = datetime.now(JST).strftime("%Y/%m/%d")
    
    # 既存データのロード（効率化のため品番列のみ）
    existing_skus = set([str(s).upper().strip() for s in sheets["Master"].col_values(4)])
    sheets["Today_New"].clear()
    sheets["Today_New"].append_row(header)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}, locale="ja-JP"
        )
        
        h_page = await context.new_page()
        b_page = await context.new_page()
        
        # ステルス呼び出し (最も安定した形式)
        try: await playwright_stealth.stealth_async(h_page)
        except: pass
        try: await playwright_stealth.stealth_async(b_page)
        except: pass

        # 巡回順序：FR -> HK -> US -> KR を鉄の掟とする
        target_countries = ["FR", "HK", "US", "KR"]

        for cat_name, path_jp in CONFIG["JP"]["paths"].items():
            print(f"\n【重要工程】カテゴリー: {cat_name}")
            
            # 1. 国内フィルターを最新化
            await h_page.goto(f"https://www.hermes.com/jp/ja/category/{path_jp}/#|", wait_until="load", timeout=120000)
            await h_page.wait_for_selector(".product-item", timeout=30000)
            await artisan_scroll_full(h_page)
            jp_elements = await h_page.query_selector_all(".product-item")
            jp_skus = set()
            for el in jp_elements:
                d = await extract_item_details_strict(el)
                if d: jp_skus.add(d["sku"])
            print(f"    [国内網完了] {len(jp_skus)}件の商品を把握。")

            # 2. 国ごとに一品ずつ「完遂」しながら進む
            for country_key in target_countries:
                print(f"\n  ### [{country_key}] 巡回開始 ###")
                target_path = CONFIG[country_key]["paths"].get(cat_name)
                if not target_path: continue
                
                await h_page.goto(f"https://www.hermes.com/{CONFIG[country_key]['code']}/category/{target_path}/#|", wait_until="load", timeout=120000)
                await h_page.wait_for_selector(".product-item", timeout=30000)
                await artisan_scroll_full(h_page)
                
                # 海外の商品要素を特定
                os_elements = await h_page.query_selector_all(".product-item")
                print(f"    [情報] {len(os_elements)} 個の要素を検知。一品ずつの完遂処理を開始します。")

                for i, el in enumerate(os_elements):
                    # --- ここから一品完遂ループ ---
                    data = await extract_item_details_strict(el)
                    if not data: continue
                    
                    sku_upper = str(data['sku']).upper().strip()
                    print(f"      ({i+1}/{len(os_elements)}) 精査中: {data['name']} ({sku_upper})")
                    
                    # 照合1: 国内に既にあるか
                    if sku_upper in jp_skus:
                        print(f"        -> 国内既出のためスキップ。")
                        continue
                    
                    # 照合2: 過去に記帳済みか
                    if sku_upper in existing_skus:
                        print(f"        -> 過去記帳済みの重複品。スキップ。")
                        continue
                    
                    # 照合3: 今この瞬間のバイマ状況
                    is_unlisted = await check_buyma_unlisted_live(b_page, sku_upper)
                    
                    # データ計算
                    try:
                        jpy = int(float(data['price']) * EXCHANGE_RATES.get(country_key, 1.0))
                    except: jpy = 0
                    row = [today_date, cat_name, country_key, sku_upper, data['name'], data['price'], f"¥{jpy:,}", data['url']]
                    
                    # 記帳・同期・検証 (成功を確認するまで次へ行かない)
                    print(f"        [同期開始] 記帳と物理反映検証を完遂させます...")
                    if await artisan_write_and_verify_sequential(sheets, row, is_unlisted):
                        existing_skus.add(sku_upper)
                        print(f"        [成功] 完遂。次へ。")
                    else:
                        print(f"        [失敗] 記帳に失敗。この一品をやり直すかスキップします。")
                    
                    # 次の抽出前に「職人の余韻」
                    await artisan_wait(6, 12)
                    # --- 一品完遂ここまで ---

                print(f"  ### [{country_key}] 全商品の直列処理を終了 ###")
                await artisan_wait(20, 40)
            
            print(f"--- {cat_name} 全カ国完走。APIリセットのため大休憩します。 ---")
            await asyncio.sleep(60)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
