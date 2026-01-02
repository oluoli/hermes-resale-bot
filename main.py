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

# --- 設定：為替レート ---
EXCHANGE_RATES = {
    "FR": 165.0,
    "HK": 20.0,
    "US": 155.0,
    "KR": 0.11
}

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

# --- ヘルパー関数：リトライ機能付き書き込み ---
async def safe_append_rows(sheet, rows, max_retries=3):
    if not rows:
        return True
    
    for attempt in range(max_retries):
        try:
            sheet.append_rows(rows)
            print(f"      [OK] {len(rows)}件の書き込みに成功しました。")
            await asyncio.sleep(2) # API制限回避のための短い待機
            return True
        except Exception as e:
            wait_time = (attempt + 1) * 5
            print(f"      [!] 書き込み失敗 (試行 {attempt + 1}): {e}")
            print(f"      [!] {wait_time}秒後に再試行します...")
            await asyncio.sleep(wait_time)
    
    print(f"      [ERROR] {max_retries}回試行しましたが書き込みに失敗しました。")
    return False

def convert_price_to_jpy(price_str, country_key):
    try:
        num_str = re.sub(r'[^\d.]', '', price_str.replace(',', ''))
        price_num = float(num_str)
        rate = EXCHANGE_RATES.get(country_key, 1.0)
        return int(price_num * rate)
    except:
        return 0

async def scrape_hermes(page, country_code, category_path, retry=1):
    url = f"https://www.hermes.com/{country_code}/category/{category_path}/#|"
    products = {}
    
    for attempt in range(retry + 1):
        try:
            await page.goto(url, wait_until="load", timeout=90000)
            try:
                await page.wait_for_selector(".product-item", timeout=30000)
            except:
                print(f"    [!] 商品が見つかりません (試行 {attempt + 1}): {url}")
                if attempt < retry:
                    await asyncio.sleep(5)
                    continue
                return {}

            for i in range(7):
                await page.mouse.wheel(0, 1200)
                await asyncio.sleep(1.5)

            items = await page.query_selector_all(".product-item")
            if len(items) > 0:
                print(f"    -> {country_code}: {len(items)}個検知")
                for item in items:
                    name_el = await item.query_selector(".product-item-name")
                    price_el = await item.query_selector(".product-item-price")
                    link_el = await item.query_selector("a")
                    if name_el and link_el:
                        name = (await name_el.inner_text()).strip()
                        price_text = (await price_el.inner_text()).strip() if price_el else "0"
                        link = await link_el.get_attribute("href")
                        sku_match = re.search(r'H[A-Z0-9]{5,}', link)
                        sku = sku_match.group(0) if sku_match else name
                        products[sku] = {"name": name, "price": price_text, "url": f"https://www.hermes.com{link}"}
                return products
            
            elif attempt < retry:
                print(f"    [!] 0件のため再試行します...")
                await asyncio.sleep(5)
                
        except Exception as e:
            print(f"    × エラー発生 ({country_code} / {category_path}): {e}")
            if attempt < retry:
                await asyncio.sleep(5)
    
    return products

async def run():
    # 認証
    creds_json = json.loads(os.environ["GOOGLE_CREDENTIALS"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive'])
    client = gspread.authorize(creds)
    
    # シート取得
    spreadsheet = client.open("Hermes_Check_List")
    sheet_master = spreadsheet.get_worksheet(0)
    
    try:
        sheet_today = spreadsheet.worksheet("Today_New")
    except gspread.WorksheetNotFound:
        sheet_today = spreadsheet.add_worksheet(title="Today_New", rows="100", cols="20")
    
    JST = timezone(timedelta(hours=+9), 'JST')
    today_date = datetime.now(JST).strftime("%Y/%m/%d")
    header = ["追加日", "ジャンル", "国", "品番", "商品名", "現地価格", "日本円目安", "URL"]
    
    all_data = sheet_master.get_all_values()
    if not all_data:
        sheet_master.append_row(header)
        existing_skus = set()
    else:
        existing_skus = {row[5] for row in all_data if len(row) > 5}

    # 今日の新着をリセット
    sheet_today.clear()
    sheet_today.append_row(header)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="ja-JP"
        )
        page = await context.new_page()
        try: await playwright_stealth.stealth_async(page)
        except: pass

        for cat_name, path_jp in CONFIG["JP"]["paths"].items():
            print(f"\n【調査開始】: {cat_name}")
            jp_inventory = await scrape_hermes(page, CONFIG["JP"]["code"], path_jp)
            
            for country_key in ["FR", "HK", "US", "KR"]:
                print(f" -> {country_key} スキャン中...")
                path_overseas = CONFIG[country_key]["paths"].get(cat_name)
                if not path_overseas: continue
                
                overseas_inventory = await scrape_hermes(page, CONFIG[country_key]["code"], path_overseas)
                
                new_rows = []
                for sku, data in overseas_inventory.items():
                    if sku not in jp_inventory and sku not in existing_skus:
                        jpy_price = convert_price_to_jpy(data['price'], country_key)
                        row = [today_date, cat_name, country_key, sku, data['name'], data['price'], f"¥{jpy_price:,}", data['url']]
                        new_rows.append(row)
                        existing_skus.add(sku)
                
                if new_rows:
                    print(f"    ☆ 新規 {len(new_rows)}件。シートへ書き込み中...")
                    # マスターと今日、両方にリトライ機能付きで書き込み
                    success_master = await safe_append_rows(sheet_master, new_rows)
                    success_today = await safe_append_rows(sheet_today, new_rows)
                    
                    if not success_master or not success_today:
                        print(f"    [!] 一部の書き込みに最終的に失敗しました。ログを確認してください。")
                
                await asyncio.sleep(5)
            await asyncio.sleep(7)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
