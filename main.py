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

# --- カテゴリー設定 (全5カ国・14カテゴリー・一切の省略なし) ---
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

# --- 職人の待機 ---
async def artisan_wait(min_sec=5, max_sec=10):
    await asyncio.sleep(random.uniform(min_sec, max_sec))

# --- 商品詳細の抽出ロジック (その場の要素から直接読み取る) ---
async def extract_item_details_from_element(item_el):
    try:
        name_el = await item_el.query_selector(".product-item-name")
        price_el = await item_el.query_selector(".product-item-price")
        link_el = await item_el.query_selector("a")
        
        if not (name_el and link_el): return None
        
        name = (await name_el.inner_text()).strip()
        
        # 価格取得の粘り
        price = "0"
        for _ in range(3):
            price_text = await price_el.inner_text() if price_el else "0"
            price = re.sub(r'[^\d.]', '', price_text.replace(',', ''))
            if price and price != "0": break
            await asyncio.sleep(1.5)

        link = await link_el.get_attribute("href")
        full_url = f"https://www.hermes.com{link}"
        sku_match = re.search(r'H[A-Z0-9]{5,}', link)
        sku = sku_match.group(0).upper().strip() if sku_match else name.upper().strip()
            
        return {"sku": sku, "name": name, "price": price, "url": full_url}
    except: return None

# --- BUYMAでの実在確認 (超精密判定) ---
async def check_buyma_unlisted_strict(page, sku):
    search_url = f"https://www.buyma.com/r/-F1/{sku}/"
    try:
        print(f"        [バイマ鑑定] 品番 {sku} を現場照合中...")
        await page.mouse.move(random.randint(0, 500), random.randint(0, 500))
        response = await page.goto(search_url, wait_until="networkidle", timeout=60000)
        
        if response.status != 200:
            print(f"        [!] BUYMA混雑中。掲載ありとしてスキップ。")
            return False

        await artisan_wait(4, 7)
        content = await page.content()
        titles = await page.locator(".fab-product-name").all_inner_texts()
        sku_hit = any(sku in t.upper().replace(" ", "") for t in titles)

        if "該当する商品が見つかりませんでした" in content or not sku_hit:
            print(f"        [☆未掲載確定] BUYMAにお宝発見！")
            return True
        else:
            print(f"        [既出] すでに出品されています。")
            return False
    except: return False

# --- 1件ずつ記帳し、物理的に確認する関数 ---
async def artisan_write_and_verify_single(sheet, row_data, max_retry=3):
    sku_to_check = str(row_data[3]).upper().strip()
    for attempt in range(max_retry):
        try:
            await artisan_wait(3, 6)
            res = sheet.append_row(row_data)
            row_idx = res['updates']['updatedRange'].split('!A')[-1].split(':')[0]
            await asyncio.sleep(8) 
            val = sheet.cell(row_idx, 4).value
            if str(val).upper().strip() == sku_to_check:
                return True
            print(f"        [!] 物理反映未確認。再試行({attempt+1})")
        except: 
            await asyncio.sleep(30)
    return False

# --- 執念のスクロール ---
async def artisan_scroll(page):
    last_count = 0
    for _ in range(15):
        items = await page.query_selector_all(".product-item")
        current_count = len(items)
        if current_count > 0 and current_count == last_count: break
        last_count = current_count
        await page.mouse.wheel(0, 1000 + random.randint(0, 300))
        await asyncio.sleep(2.5)
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(2.5)

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
            sheets[title] = spreadsheet.add_worksheet(title=title, rows="3000", cols="20")
            sheets[title].append_row(header)

    JST = timezone(timedelta(hours=+9), 'JST')
    today_date = datetime.now(JST).strftime("%Y/%m/%d")
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
        
        # エラー修正版のステルス呼び出し
        try: await playwright_stealth.stealth_async(h_page)
        except: pass
        try: await playwright_stealth.stealth_async(b_page)
        except: pass

        for cat_name, path_jp in CONFIG["JP"]["paths"].items():
            print(f"\n【重要工程】カテゴリー: {cat_name}")
            
            # 1. 日本サイトの「除外フィルター」を完璧に構築
            await h_page.goto(f"https://www.hermes.com/jp/ja/category/{path_jp}/#|", wait_until="load", timeout=120000)
            await h_page.wait_for_selector(".product-item", timeout=30000)
            await artisan_scroll(h_page)
            jp_elements = await h_page.query_selector_all(".product-item")
            jp_skus = set()
            for el in jp_elements:
                d = await extract_item_details_from_element(el)
                if d: jp_skus.add(d["sku"])
            print(f"    [日本フィルタ完了] {len(jp_skus)}件の商品を把握。")

            # 2. 海外4カ国を巡回 (FR -> HK -> US -> KR)
            for country_key in ["FR", "HK", "US", "KR"]:
                print(f"\n  ### [{country_key}] 調査開始 ###")
                target_path = CONFIG[country_key]["paths"].get(cat_name)
                if not target_path: continue
                
                await h_page.goto(f"https://www.hermes.com/{CONFIG[country_key]['code']}/category/{target_path}/#|", wait_until="load", timeout=120000)
                await h_page.wait_for_selector(".product-item", timeout=30000)
                await artisan_scroll(h_page)
                
                # ここで商品要素の一覧を取得
                os_elements = await h_page.query_selector_all(".product-item")
                print(f"    [情報] {len(os_elements)} 個の要素を検知。一品ずつ処理を開始します。")

                # --- 【核心】一品ずつ読み取り・照合・記帳を完結させてから次へ行くループ ---
                for i, el in enumerate(os_elements):
                    # 1. その場の要素から情報を「読み取る」
                    await el.scroll_into_view_if_needed()
                    data = await extract_item_details_from_element(el)
                    if not data: continue
                    
                    sku_upper = str(data['sku']).upper().strip()
                    print(f"      ({i+1}/{len(os_elements)}) 精査中: {data['name']} ({sku_upper})")
                    
                    # 2. 日本照合 ＆ 台帳照合
                    if sku_upper in jp_skus:
                        print(f"        -> 日本に既出のためスキップ")
                        continue
                    if sku_upper in existing_skus:
                        print(f"        -> 台帳に既出のためスキップ")
                        continue
                    
                    # 3. バイマ鑑定 (その場で現場確認)
                    is_unlisted = await check_buyma_unlisted_strict(b_page, sku_upper)
                    
                    # 4. 記帳・同期工程 (スプレッドシートへの物理反映まで完遂)
                    try:
                        jpy = int(float(data['price']) * EXCHANGE_RATES.get(country_key, 1.0))
                    except: jpy = 0
                    row = [today_date, cat_name, country_key, sku_upper, data['name'], data['price'], f"¥{jpy:,}", data['url']]
                    
                    print(f"        [同期中] スプレッドシートに書き込み中...")
                    if await artisan_write_and_verify_single(sheets["Master"], row):
                        sheets["Today_New"].append_row(row)
                        if is_unlisted:
                            print(f"        [お宝確定] BUYMA_Unlistedにも記帳します。")
                            await artisan_write_and_verify_single(sheets["BUYMA_Unlisted"], row)
                        
                        existing_skus.add(sku_upper)
                        print(f"        [完遂] この一品の処理がすべて終了しました。")
                    
                    # 5. 次の商品の読み取り前に「職人の間合い」
                    await artisan_wait(6, 12)

                print(f"  ### [{country_key}] すべての個別処理を終了 ###")
                await artisan_wait(15, 30)
            
            print(f"--- {cat_name} 全カ国完走。APIリセット休憩 ---")
            await asyncio.sleep(45)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
