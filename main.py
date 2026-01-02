import asyncio
import os
import json
import gspread
import re
# 日本時間対応
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

# ユーザー様のCONFIG（そのまま維持）
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
            # ページ遷移と要素の出現を待つ
            await page.goto(url, wait_until="load", timeout=90000)
            
            # 商品要素が少なくとも1つ出現するまで最大30秒粘る
            try:
                await page.wait_for_selector(".product-item", timeout=30000)
            except:
                print(f"   [!] 商品要素が見つかりません (試行 {attempt + 1}): {url}")
                if attempt < retry:
                    await asyncio.sleep(5)
                    continue
                return {}

            # 徐々にスクロールしてLazy Load（遅延読み込み）を解消
            for i in range(7):
                await page.mouse.wheel(0, 1200)
                await asyncio.sleep(1.5)

            items = await page.query_selector_all(".product-item")
            if len(items) > 0:
                print(f"   -> {country_code}: {len(items)}個検知")
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
                return products # 成功したらループを抜ける
            
            elif attempt < retry:
                print(f"   [!] 0件のため再試行します...")
                await asyncio.sleep(5)
                
        except Exception as e:
            print(f"   × エラー発生 ({country_code} / {category_path}): {e}")
            if attempt < retry:
                await asyncio.sleep(5)
    
    return products

async def run():
    creds_json = json.loads(os.environ["GOOGLE_CREDENTIALS"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive'])
    client = gspread.authorize(creds)
    
    spreadsheet = client.open("Hermes_Check_List")
    sheet_master = spreadsheet.get_worksheet(0)
    
    try:
        sheet_today = spreadsheet.worksheet("Today_New")
    except gspread.WorksheetNotFound:
        sheet_today = spreadsheet.add_worksheet(title="Today_New", rows="100", cols="20")
    
    # 【重要】日本時間 (JST) での日付取得
    JST = timezone(timedelta(hours=+9), 'JST')
    today_date = datetime.now(JST).strftime("%Y/%m/%d")
    
    header = ["追加日", "ジャンル", "国", "品番", "商品名", "現地価格", "日本円目安", "URL"]
    
    all_data = sheet_master.get_all_values()
    if not all_data:
        sheet_master.append_row(header)
        existing_skus = set()
    else:
        existing_skus = {row[3] for row in all_data if len(row) > 3}

    sheet_today.clear()
    sheet_today.append_row(header)

    async with async_playwright() as p:
        # ヘッドレスモードを維持しつつ、より自然なブラウザ環境をエミュレート
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
                    sheet_master.append_rows(new_rows)
                    sheet_today.append_rows(new_rows)
                    print(f"    ☆ {len(new_rows)}件の新規アイテムを保存しました")
                
                await asyncio.sleep(5)
            await asyncio.sleep(7)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
