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

# --- ヘルパー：APIリミットを考慮した堅牢な書き込み関数 ---
async def persistent_write(sheet, rows, max_attempts=5):
    if not rows: return True
    verify_sku = str(rows[-1][3]).upper().strip() # 最後の品番で確認
    
    for attempt in range(max_attempts):
        try:
            print(f"      [書き込み試行 {attempt+1}] API送信中...")
            sheet.append_rows(rows)
            # 反映待ち（重要：リトライごとに長くする）
            await asyncio.sleep(20 + (attempt * 10))
            
            # API節約：全データ読み込みではなく、末尾のセルのみ確認
            last_row_index = len(sheet.col_values(1))
            check_range = f"D{max(1, last_row_index - 10)}:D{last_row_index}"
            recent_skus = [str(val).upper().strip() for sublist in sheet.get_values(check_range) for val in sublist]
            
            if verify_sku in recent_skus:
                print(f"      [成功確認] シートへの物理的な反映を確認しました。")
                await asyncio.sleep(5) # 成功後もAPIを休ませる
                return True
            print(f"      [!] 書き込み未反映。再試行します...")
        except Exception as e:
            print(f"      [!] エラー: {e}")
            await asyncio.sleep(30) # API制限時は長めに休む
    return False

def extract_sku(url, name):
    match = re.search(r'H[A-Z0-9]{5,}', url)
    return match.group(0).upper() if match else name.strip().upper()

async def scrape_hermes(page, country_code, category_path, is_jp=False):
    url = f"https://www.hermes.com/{country_code}/category/{category_path}/#|"
    # 日本サイトの在庫取得に失敗すると全て未入荷になるため、JPのみ最大5回リトライ
    retry_limit = 5 if is_jp else 2
    
    for attempt in range(retry_limit):
        try:
            await page.goto(url, wait_until="load", timeout=90000)
            await page.wait_for_selector(".product-item", timeout=30000)
            
            # JPはより確実に、海外も丁寧にスクロール
            scrolls = 15 if is_jp else 8
            for _ in range(scrolls):
                await page.mouse.wheel(0, 1200)
                await asyncio.sleep(1.5)
            
            items = await page.query_selector_all(".product-item")
            if is_jp and len(items) == 0:
                print(f"    [!] 日本サイト商品0件。再読み込みします({attempt+1}/{retry_limit})")
                continue

            products = {}
            for item in items:
                name_el = await item.query_selector(".product-item-name")
                link_el = await item.query_selector("a")
                price_el = await item.query_selector(".product-item-price")
                if name_el and link_el:
                    name = (await name_el.inner_text()).strip()
                    price = (await price_el.inner_text()).strip() if price_el else "0"
                    link = await link_el.get_attribute("href")
                    sku = extract_sku(link, name)
                    products[sku] = {"name": name, "price": price, "url": f"https://www.hermes.com{link}"}
            
            print(f"    -> {country_code}: {len(products)}個の商品を検知")
            return products
        except:
            await asyncio.sleep(10)
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

    # 既存データの読み込み（大文字統一）
    all_rows = sheet_master.get_all_values()
    if not all_rows:
        sheet_master.append_row(header)
        existing_skus = set()
    else: existing_skus = {str(row[3]).upper().strip() for row in all_rows if len(row) > 3}

    sheet_today.clear()
    sheet_today.append_row(header)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0...", viewport={"width": 1920, "height": 1080})
        page = await context.new_page()
        try: await playwright_stealth.stealth_async(page)
        except: pass

        for cat_name, path_jp in CONFIG["JP"]["paths"].items():
            print(f"\n【カテゴリー: {cat_name}】調査中...")
            # 日本サイトを最優先で確実にスキャン
            jp_inv = await scrape_hermes(page, CONFIG["JP"]["code"], path_jp, is_jp=True)
            
            for country in ["FR", "HK", "US", "KR"]:
                print(f"  -> {country} 確認開始")
                os_inv = await scrape_hermes(page, CONFIG[country]["code"], CONFIG[country]["paths"][cat_name])
                
                to_write = []
                for sku, data in os_inv.items():
                    # 日本に存在せず、マスター履歴にもない商品だけを厳選
                    if sku not in jp_inv and sku not in existing_skus:
                        try:
                            num = float(re.sub(r'[^\d.]', '', data['price'].replace(',', '')))
                            jpy = int(num * EXCHANGE_RATES.get(country, 1.0))
                        except: jpy = 0
                        row = [today_date, cat_name, country, sku, data['name'], data['price'], f"¥{jpy:,}", data['url']]
                        to_write.append(row)
                
                if to_write:
                    print(f"    ☆ {len(to_write)}件の日本未入荷品を発見。")
                    # マスター・今日、それぞれの書き込みを「成功するまで監視」
                    if await persistent_write(sheet_master, to_write):
                        await persistent_write(sheet_today, to_write)
                        # 成功後にローカルリストも更新
                        for item in to_write: existing_skus.add(str(item[3]).upper())
                    
                    # APIリミットを回避するため、書き込み後に必ず長い休憩を入れる
                    print("    [待機] API制限回避のため20秒休憩します...")
                    await asyncio.sleep(20)
                
                await asyncio.sleep(5) # 国ごとのクールダウン
            await asyncio.sleep(10) # カテゴリーごとのクールダウン
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
