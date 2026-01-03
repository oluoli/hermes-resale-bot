import asyncio
import os
import json
import gspread
import re
from datetime import datetime, timedelta, timezone
from playwright.async_api import async_playwright
import playwright_stealth
from oauth2client.service_account import ServiceAccountCredentials

# --- 設定：為替レート ---
EXCHANGE_RATES = {
    "FR": 165.0,  # EUR
    "HK": 20.0,   # HKD
    "US": 155.0,  # USD
    "KR": 0.11    # KRW
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

async def scrape_hermes(page, country_code, category_path):
    url = f"https://www.hermes.com/{country_code}/category/{category_path}/#|"
    products = {}
    try:
        await page.goto(url, wait_until="load", timeout=90000)
        await page.wait_for_selector(".product-item", timeout=30000)
        
        for _ in range(6):
            await page.mouse.wheel(0, 1500)
            await asyncio.sleep(2)

        items = await page.query_selector_all(".product-item")
        print(f"    -> {country_code}: {len(items)}個の商品を検知しました")

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
    except Exception as e:
        print(f"    [!] {country_code} でエラーが発生しました（在庫なしの可能性）: {e}")
    return products

async def run():
    creds_json = json.loads(os.environ["GOOGLE_CREDENTIALS"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive'])
    client = gspread.authorize(creds)
    spreadsheet = client.open("Hermes_Check_List")
    sheet_master = spreadsheet.get_worksheet(0)
    
    try:
        sheet_today = spreadsheet.worksheet("Today_New")
    except:
        sheet_today = spreadsheet.add_worksheet(title="Today_New", rows="100", cols="20")
    
    JST = timezone(timedelta(hours=+9), 'JST')
    today_date = datetime.now(JST).strftime("%Y/%m/%d")
    header = ["追加日", "ジャンル", "国", "品番", "商品名", "現地価格", "日本円目安", "URL"]
    
    all_data = sheet_master.get_all_values()
    if not all_data:
        sheet_master.append_row(header)
        existing_skus = set()
    else:
        existing_skus = {row[3] for row in all_data if len(row) > 3}

    # 一括書き込み用のリスト
    final_rows = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = await context.new_page()
        
        # エラーが出やすい箇所の修正
        try:
            playwright_stealth.stealth_sync(page)
        except:
            print("Stealth設定をスキップします")

        for cat_name, path_jp in CONFIG["JP"]["paths"].items():
            print(f"\n【調査開始】: {cat_name}")
            jp_inventory = await scrape_hermes(page, CONFIG["JP"]["code"], path_jp)
            
            for country_key in ["FR", "HK", "US", "KR"]:
                print(f"  -> {country_key} スキャン中...")
                path_overseas = CONFIG[country_key]["paths"].get(cat_name)
                if not path_overseas: continue
                
                overseas_inventory = await scrape_hermes(page, CONFIG[country_key]["code"], path_overseas)
                
                for sku, data in overseas_inventory.items():
                    if sku not in jp_inventory and sku not in existing_skus:
                        # 通貨から数字を抽出
                        try:
                            num_str = re.sub(r'[^\d.]', '', data['price'].replace(',', ''))
                            price_num = float(num_str)
                            jpy_price = int(price_num * EXCHANGE_RATES.get(country_key, 1.0))
                        except:
                            jpy_price = 0
                            
                        row = [today_date, cat_name, country_key, sku, data['name'], data['price'], f"¥{jpy_price:,}", data['url']]
                        final_rows.append(row)
                        existing_skus.add(sku) # 同じ実行内での重複を防ぐ
                
                await asyncio.sleep(5)
            await asyncio.sleep(10)
        
        await browser.close()

    # --- 最後に一括で書き込む（これが最も確実です） ---
    if final_rows:
        print(f"\n合計 {len(final_rows)} 件の新規アイテムを一括書き込みします...")
        sheet_today.clear()
        sheet_today.append_row(header)
        
        # マスターと本日の新着へ書き込み（失敗したら5回リトライ）
        for target_sheet in [sheet_master, sheet_today]:
            for attempt in range(5):
                try:
                    target_sheet.append_rows(final_rows)
                    print(f"  [OK] {target_sheet.title} への書き込みが完了しました")
                    break
                except Exception as e:
                    print(f"  [!] 書き込み失敗 (リトライ {attempt+1}/5): {e}")
                    await asyncio.sleep(20)
    else:
        print("\n本日の新着アイテムはありませんでした。")

if __name__ == "__main__":
    asyncio.run(run())
