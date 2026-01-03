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

# --- 1件ずつ確実に記入し、反映を確認する関数 ---
async def write_and_verify_single_row(sheet, row_data, max_retry=3):
    sku_to_check = str(row_data[3]).upper().strip()
    
    for attempt in range(max_retry):
        try:
            sheet.append_row(row_data)
            await asyncio.sleep(5) # 書き込み後の反映待ち
            
            # 品番列(D列)の最新の値を数件取って確認
            all_skus = [str(s).upper().strip() for s in sheet.col_values(4)]
            if sku_to_check in all_skus:
                print(f"        [確実] 品番 {sku_to_check} の記入成功を確認しました。")
                return True
            print(f"        [!] 品番 {sku_to_check} が見つかりません。再送します({attempt+1})")
        except Exception as e:
            print(f"        [エラー] 書き込みエラー: {e}")
            await asyncio.sleep(10)
    return False

def extract_sku(url, name):
    match = re.search(r'H[A-Z0-9]{5,}', url)
    return match.group(0).upper().strip() if match else name.upper().strip()

async def scrape_hermes_robust(page, country_code, category_path, is_jp=False):
    url = f"https://www.hermes.com/{country_code}/category/{category_path}/#|"
    
    # 日本サイトの取得に失敗すると全て未入荷になるため、JPのみ執念深くリロード
    for attempt in range(5 if is_jp else 2):
        try:
            await page.goto(url, wait_until="load", timeout=90000)
            # 商品要素が出るまで待つ
            await page.wait_for_selector(".product-item", timeout=30000)
            
            # 日本サイトは特に念入りにスクロール
            scroll_count = 20 if is_jp else 10
            for _ in range(scroll_count):
                await page.mouse.wheel(0, 800)
                await asyncio.sleep(1)

            items = await page.query_selector_all(".product-item")
            if is_jp and len(items) == 0:
                print(f"    [!] 日本サイト商品0件。再読み込み中... ({attempt+1})")
                continue

            products = {}
            for item in items:
                # 画面内に入ってからデータを取得させる（Lazy Load対策）
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
            
            print(f"    -> {country_code}: {len(products)}個の商品を正確に検知")
            return products
        except Exception:
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
    
    # 既存データのロード
    master_data = sheet_master.get_all_values()
    existing_skus = {str(row[3]).upper().strip() for row in master_data if len(row) > 3}

    sheet_today.clear()
    sheet_today.append_row(["追加日", "ジャンル", "国", "品番", "商品名", "現地価格", "日本円目安", "URL"])

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0...", viewport={"width": 1920, "height": 1080})
        page = await context.new_page()
        try: await playwright_stealth.stealth_async(page)
        except: pass

        for cat_name, path_jp in CONFIG["JP"]["paths"].items():
            print(f"\n【{cat_name}】照合開始...")
            # 日本サイトを「絶対」に全件取得する
            jp_inv = await scrape_hermes_robust(page, "jp/ja", path_jp, is_jp=True)
            
            for country in ["FR", "HK", "US", "KR"]:
                print(f"  -> {country} 調査中...")
                os_inv = await scrape_hermes_robust(page, CONFIG[country]["code"], CONFIG[country]["paths"][cat_name])
                
                for sku, data in os_inv.items():
                    sku_upper = str(sku).upper().strip()
                    # 日本に存在せず、かつスプレッドシートの全履歴にもない場合
                    if sku_upper not in jp_inv and sku_upper not in existing_skus:
                        try:
                            num = float(re.sub(r'[^\d.]', '', data['price'].replace(',', '')))
                            jpy = int(num * EXCHANGE_RATES.get(country, 1.0))
                        except: jpy = 0
                        
                        row = [today_date, cat_name, country, sku_upper, data['name'], data['price'], f"¥{jpy:,}", data['url']]
                        
                        print(f"      [新着発見] {data['name']} を記入中...")
                        # マスターに記入・確認
                        if await write_and_verify_single_row(sheet_master, row):
                            # 今日のシートにも記入
                            await write_and_verify_single_row(sheet_today, row)
                            # 既存リストに追加（重複防止）
                            existing_skus.add(sku_upper)
                            
                        # API制限回避のための短い休憩
                        await asyncio.sleep(2)
                
                await asyncio.sleep(5)
            await asyncio.sleep(10)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
