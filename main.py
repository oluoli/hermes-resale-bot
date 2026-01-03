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

# --- 設定：為替レート ---
EXCHANGE_RATES = {"FR": 165.0, "HK": 20.0, "US": 155.0, "KR": 0.11}

CONFIG = {
    "JP": {"code": "jp/ja", "paths": {
        "ゴールドジュエリー": "jewelry/gold-jewelry", "ブレスレット": "women/fashion-jewelry/bracelets",
        "ネックレス": "women/fashion-jewelry/necklaces-and-pendants", "耳飾り": "women/fashion-jewelry/earrings",
        "リング": "women/fashion-jewelry/rings", "ベルト": "women/belts",
        "スカーフ": "scarves-shawls-and-stoles/silk-scarves-and-accessories", "ブランケット": "home/textiles",
        "ベビーギフト": "gifts-and-petit-h/baby-gifts", "ペット": "home-outdoor-and-equestrian/equestrian-and-dogs/dog",
        "PetitH": "petit-h/all-petit-h", "バッグ": "women/bags-and-small-leather-goods/bags-and-clutches",
        "メンズバッグ": "men/bags-and-small-leather-goods/bags", "テーブルウェア": "home/tableware"
    }},
    "FR": {"code": "fr/fr", "paths": {
        "ゴールドジュエリー": "bijouterie/bijoux-en-or", "ブレスレット": "femme/accessoires-bijoux/bracelets",
        "ネックレス": "femme/accessoires-bijoux/colliers-et-pendentifs", "耳飾り": "femme/accessoires-bijoux/boucles-d-oreilles",
        "リング": "femme/accessoires-bijoux/bagues", "ベルト": "femme/ceintures",
        "スカーフ": "femme/carres-chales-et-echarpes/carres-et-accessoires-de-soie", "ブランケット": "maison/textiles",
        "ベビーギフト": "cadeaux-et-petit-h/cadeaux-de-naissance", "ペット": "maison-plein-air-et-equitation/equitation-et-chien/chien",
        "PetitH": "petit-h", "バッグ": "femme/sacs-et-petite-maroquinerie/sacs-et-pochettes",
        "メンズバッグ": "homme/sacs-et-petite-maroquinerie/sacs", "テーブルウェア": "maison/art-de-la-table"
    }},
    "HK": {"code": "hk/en", "paths": {
        "ゴールドジュエリー": "jewelry/gold-jewelry", "ブレスレット": "women/fashion-jewelry/bracelets",
        "ネックレス": "women/fashion-jewelry/necklaces-and-pendants", "耳飾り": "women/fashion-jewelry/earrings",
        "リング": "women/fashion-jewelry/rings", "ベルト": "women/belts",
        "スカーフ": "women/scarves-shawls-and-stoles/silk-scarves-and-accessories", "ブランケット": "home/textiles",
        "ベビーギフト": "gifts-and-petit-h/baby-gifts", "ペット": "home-outdoor-and-equestrian/equestrian-and-dogs/dog",
        "PetitH": "petit-h", "バッグ": "women/bags-and-small-leather-goods/bags-and-clutches",
        "メンズバッグ": "men/bags-and-small-leather-goods/bags", "テーブルウェア": "home/tableware"
    }},
    "US": {"code": "us/en", "paths": {
        "ゴールドジュエリー": "jewelry/gold-jewelry", "ブレスレット": "women/fashion-jewelry/bracelets",
        "ネックレス": "women/fashion-jewelry/necklaces-and-pendants", "耳飾り": "women/fashion-jewelry/earrings",
        "リング": "women/fashion-jewelry/rings", "ベルト": "women/belts",
        "スカーフ": "women/scarves-shawls-and-stoles/silk-scarves-and-accessories", "ブランケット": "home/textiles",
        "ベビーギフト": "gifts-and-petit-h/baby-gifts", "ペット": "home-outdoor-and-equestrian/equestrian-and-dogs/dog",
        "PetitH": "petit-h", "バッグ": "women/bags-and-small-leather-goods/bags-and-clutches",
        "メンズバッグ": "men/bags-and-small-leather-goods/bags", "テーブルウェア": "home/tableware"
    }},
    "KR": {"code": "kr/ko", "paths": {
        "ゴールドジュエリー": "jewelry/gold-jewelry", "ブレスレット": "women/fashion-jewelry/bracelets",
        "ネックレス": "women/fashion-jewelry/necklaces-and-pendants", "耳飾り": "women/fashion-jewelry/earrings",
        "リング": "women/fashion-jewelry/rings", "ベルト": "women/belts",
        "スカーフ": "women/scarves-shawls-and-stoles/silk-scarves-and-accessories", "ブランケット": "home/textiles",
        "ベビーギフト": "gifts-and-petit-h/baby-gifts", "ペット": "home-outdoor-and-equestrian/equestrian-and-dogs/dog",
        "PetitH": "petit-h", "バッグ": "women/bags-and-small-leather-goods/bags-and-clutches",
        "メンズバッグ": "men/bags-and-small-leather-goods/bags", "テーブルウェア": "home/tableware"
    }}
}

# --- 職人の呼吸（ランダム待機） ---
async def artisan_wait(min_sec=4, max_sec=10):
    await asyncio.sleep(random.uniform(min_sec, max_sec))

# --- BUYMAでの実在確認ロジック ---
async def is_not_on_buyma(page, sku):
    """BUYMAで検索して、商品が1件もなければTrueを返す"""
    search_url = f"https://www.buyma.com/r/-F1/{sku}/"
    try:
        print(f"        [BUYMA確認] 品番 {sku} を検索中...")
        await page.goto(search_url, wait_until="networkidle", timeout=60000)
        await artisan_wait(3, 6) # 人間が検索結果を目視する時間

        # 「該当する商品が見つかりませんでした」という文字があるかチェック
        content = await page.content()
        if "該当する商品が見つかりませんでした" in content:
            print(f"        [発見!] BUYMAに未掲載の商品です。")
            return True
        else:
            print(f"        [情報] BUYMAに既に掲載されています。")
            return False
    except:
        return False

# --- 1件ずつ記帳し、物理的に確認する関数 ---
async def artisan_write_and_confirm(sheet, row_data, max_retry=3):
    sku_to_check = str(row_data[3]).upper().strip()
    for attempt in range(max_retry):
        try:
            await artisan_wait(5, 8)
            sheet.append_row(row_data)
            await asyncio.sleep(12) 
            last_rows = sheet.get_all_values()[-10:]
            if any(str(r[3]).upper().strip() == sku_to_check for r in last_rows if len(r) > 3):
                return True
        except Exception as e:
            await asyncio.sleep(60)
    return False

def extract_sku(url, name):
    match = re.search(r'H[A-Z0-9]{5,}', url)
    return match.group(0).upper().strip() if match else name.upper().strip()

async def scrape_hermes_artisan(page, country_code, category_path, is_jp=False):
    url = f"https://www.hermes.com/{country_code}/category/{category_path}/#|"
    for attempt in range(5 if is_jp else 2):
        try:
            await page.goto(url, wait_until="load", timeout=120000)
            await page.wait_for_selector(".product-item", timeout=30000)
            for _ in range(15 if is_jp else 8):
                await page.mouse.wheel(0, 800)
                await asyncio.sleep(1.5)
            items = await page.query_selector_all(".product-item")
            if is_jp and len(items) == 0: continue
            products = {}
            for item in items:
                await item.scroll_into_view_if_needed()
                name_el = await item.query_selector(".product-item-name")
                link_el = await item.query_selector("a")
                price_el = await item.query_selector(".product-item-price")
                if name_el and link_el:
                    name = (await name_el.inner_text()).strip()
                    price = (await price_el.inner_text()).strip() if price_el else "0"
                    link = await link_el.get_attribute("href")
                    sku = extract_sku(link, name)
                    products[sku] = {"name": name, "price": price, "url": f"https://www.hermes.com{link}"}
            return products
        except: await asyncio.sleep(10)
    return None if is_jp else {}

async def run():
    creds_json = json.loads(os.environ["GOOGLE_CREDENTIALS"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive'])
    client = gspread.authorize(creds)
    spreadsheet = client.open("Hermes_Check_List")
    sheet_master = spreadsheet.get_worksheet(0)
    try: sheet_today = spreadsheet.worksheet("Today_New")
    except: sheet_today = spreadsheet.add_worksheet(title="Today_New", rows="100", cols="20")
    
    # 【新設】BUYMA未掲載シートの準備
    try: sheet_buyma = spreadsheet.worksheet("BUYMA_Unlisted")
    except: 
        sheet_buyma = spreadsheet.add_worksheet(title="BUYMA_Unlisted", rows="100", cols="20")
        sheet_buyma.append_row(["追加日", "ジャンル", "国", "品番", "商品名", "現地価格", "日本円目安", "URL"])

    JST = timezone(timedelta(hours=+9), 'JST')
    today_date = datetime.now(JST).strftime("%Y/%m/%d")
    
    master_all = sheet_master.get_all_values()
    existing_skus = {str(row[3]).upper().strip() for row in master_all if len(row) > 3}

    sheet_today.clear()
    sheet_today.append_row(["追加日", "ジャンル", "国", "品番", "商品名", "現地価格", "日本円目安", "URL"])

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36", viewport={"width": 1920, "height": 1080})
        page = await context.new_page()
        # BUYMAチェック用の別ページも用意
        buyma_page = await context.new_page()
        try: await playwright_stealth.stealth_async(page)
        except: pass

        for cat_name, path_jp in CONFIG["JP"]["paths"].items():
            print(f"\n--- 【職人リサーチ】カテゴリー: {cat_name} ---")
            jp_inv = await scrape_hermes_artisan(page, "jp/ja", path_jp, is_jp=True)
            if jp_inv is None: continue
            
            for country in ["FR", "HK", "US", "KR"]:
                print(f"  -> {country} 調査中...")
                os_inv = await scrape_hermes_artisan(page, CONFIG[country]["code"], CONFIG[country]["paths"][cat_name])
                if not os_inv: continue

                for sku, data in os_inv.items():
                    sku_upper = str(sku).upper().strip()
                    
                    if sku_upper not in jp_inv and sku_upper not in existing_skus:
                        # BUYMAに存在するか確認（ここが追加ステップ）
                        is_unlisted = await is_not_on_buyma(buyma_page, sku_upper)
                        
                        try:
                            num = float(re.sub(r'[^\d.]', '', data['price'].replace(',', '')))
                            jpy = int(num * EXCHANGE_RATES.get(country, 1.0))
                        except: jpy = 0
                        
                        row = [today_date, cat_name, country, sku_upper, data['name'], data['price'], f"¥{jpy:,}", data['url']]
                        
                        print(f"      [記帳] {data['name']} を記録中...")
                        if await artisan_write_and_confirm(sheet_master, row):
                            await artisan_write_and_confirm(sheet_today, row)
                            # BUYMAに未掲載なら専用シートにも書く
                            if is_unlisted:
                                await artisan_write_and_confirm(sheet_buyma, row)
                            
                            existing_skus.add(sku_upper)
                        await artisan_wait(5, 10)
                
                await artisan_wait(15, 30)
            await asyncio.sleep(40)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
