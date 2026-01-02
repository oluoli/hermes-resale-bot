import asyncio
import os
import json
import gspread
import re
import time
from datetime import datetime, timedelta, timezone
from playwright.async_api import async_playwright
import playwright_stealth
from oauth2client.service_account import ServiceAccountCredentials

# --- 設定：為替レート（最新の数値に微調整してください） ---
EXCHANGE_RATES = {
    "FR": 165.0,
    "HK": 20.0,
    "US": 155.0,
    "KR": 0.11
}

# ユーザー様の調整済みCONFIG
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
        "PetitH": "petit-h",
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

# --- ヘルパー：検証付き書き込み ---
async def verify_and_append_rows(sheet, rows, max_attempts=5):
    if not rows: return True
    verify_sku = rows[-1][3] # 最後に書き込むSKUを確認用にする
    
    for attempt in range(max_attempts):
        try:
            sheet.append_rows(rows)
            await asyncio.sleep(5) # 反映待ち
            # 末尾15行を取得して検証
            total = len(sheet.get_all_values())
            check_range = f"D{max(1, total-20)}:D{total}"
            written_skus = [val for sublist in sheet.get_values(check_range) for val in sublist]
            
            if verify_sku in written_skus:
                print(f"      [Check OK] 書き込みを確認しました。")
                return True
            print(f"      [?] 書き込み未検知。再試行します...")
        except Exception as e:
            print(f"      [!] APIエラー: {e}")
        
        await asyncio.sleep((attempt + 1) * 7) # 徐々に待機を長くする
    return False

def convert_price_to_jpy(price_str, country_key):
    try:
        num_str = re.sub(r'[^\d.]', '', price_str.replace(',', ''))
        price_num = float(num_str)
        return int(price_num * EXCHANGE_RATES.get(country_key, 1.0))
    except: return 0

async def scrape_hermes(page, country_code, category_path, max_retry=2):
    url = f"https://www.hermes.com/{country_code}/category/{category_path}/#|"
    
    for attempt in range(max_retry + 1):
        try:
            await page.goto(url, wait_until="load", timeout=90000)
            await page.wait_for_selector(".product-item", timeout=30000)
            
            # Lazy load対策のスクロール
            for _ in range(8):
                await page.mouse.wheel(0, 1000)
                await asyncio.sleep(1.2)
            
            items = await page.query_selector_all(".product-item")
            if len(items) > 0:
                print(f"    -> {country_code}: {len(items)}個検知")
                products = {}
                for item in items:
                    name_el = await item.query_selector(".product-item-name")
                    price_el = await item.query_selector(".product-item-price")
                    link_el = await item.query_selector("a")
                    if name_el and link_el:
                        name = (await name_el.inner_text()).strip()
                        price = (await price_el.inner_text()).strip() if price_el else "0"
                        link = await link_el.get_attribute("href")
                        sku = (re.search(r'H[A-Z0-9]{5,}', link).group(0)) if re.search(r'H[A-Z0-9]{5,}', link) else name
                        products[sku] = {"name": name, "price": price, "url": f"https://www.hermes.com{link}"}
                return products
            
            print(f"    [!] {country_code} 商品0件。リロードして再試行...")
            await asyncio.sleep(5)
        except:
            if attempt == max_retry: print(f"    [×] {country_code} 読み込み失敗")
            await asyncio.sleep(5)
    return {}

async def run():
    creds_json = json.loads(os.environ["GOOGLE_CREDENTIALS"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive'])
    client = gspread.authorize(creds)
    
    spreadsheet = client.open("Hermes_Check_List")
    sheet_master = spreadsheet.get_worksheet(0)
    try: sheet_today = spreadsheet.worksheet("Today_New")
    except: sheet_today = spreadsheet.add_worksheet(title="Today_New", rows="100", cols="20")
    
    JST = timezone(timedelta(hours=+9), 'JST')
    today_date = datetime.now(JST).strftime("%Y/%m/%d")
    header = ["追加日", "ジャンル", "国", "品番", "商品名", "現地価格", "日本円目安", "URL"]
    
    # 既存SKUのロード
    all_rows = sheet_master.get_all_values()
    if not all_rows:
        sheet_master.append_row(header)
        existing_skus = set()
    else: existing_skus = {row[3] for row in all_rows if len(row) > 3}

    sheet_today.clear()
    sheet_today.append_row(header)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 1080},
            locale="ja-JP"
        )
        page = await context.new_page()
        try: await playwright_stealth.stealth_async(page)
        except: pass

        # 各カテゴリー × 各国 の総当たり調査
        for cat_name, path_jp in CONFIG["JP"]["paths"].items():
            print(f"\n--- 調査ジャンル: {cat_name} ---")
            jp_inv = await scrape_hermes(page, CONFIG["JP"]["code"], path_jp)
            
            for country in ["FR", "HK", "US", "KR"]:
                print(f"  [{country}] スキャン中...")
                path_os = CONFIG[country]["paths"].get(cat_name)
                if not path_os: continue
                
                os_inv = await scrape_hermes(page, CONFIG[country]["code"], path_os)
                
                to_append = []
                for sku, data in os_inv.items():
                    if sku not in jp_inv and sku not in existing_skus:
                        jpy = convert_price_to_jpy(data['price'], country)
                        to_append.append([today_date, cat_name, country, sku, data['name'], data['price'], f"¥{jpy:,}", data['url']])
                        existing_skus.add(sku)
                
                if to_append:
                    print(f"    ☆ {len(to_append)}件の新規発見。書き込みと検証を開始...")
                    await verify_and_append_rows(sheet_master, to_append)
                    await verify_and_append_rows(sheet_today, to_append)
                
                await asyncio.sleep(3) # API負荷軽減
            await asyncio.sleep(5)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
