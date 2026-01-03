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

# --- ヘルパー：書き込みを確認するまでループを止める関数 ---
async def block_until_written(sheet, rows, max_attempts=5):
    if not rows: return True
    verify_sku = str(rows[-1][3]).strip().upper() # 最後に書き込むSKUを確認
    
    for attempt in range(max_attempts):
        try:
            print(f"      [書き込み試行 {attempt+1}] {len(rows)}件を送信中...")
            sheet.append_rows(rows)
            # Google側の反映ラグを考慮して待機
            wait_time = 15 + (attempt * 10)
            await asyncio.sleep(wait_time)
            
            # 品番列(D列)の末尾30件だけを取得してチェック(API負荷を抑える)
            total_rows = len(sheet.col_values(1))
            check_start = max(1, total_rows - 30)
            recent_skus = [str(s).strip().upper() for s in sheet.col_values(4)[check_start-1:]]
            
            if verify_sku in recent_skus:
                print(f"      [確認完了] シートへの書き込みが反映されました。")
                return True
            print(f"      [!] 記入が未反映です。再試行します。")
        except Exception as e:
            print(f"      [!] APIエラー発生: {e}")
            await asyncio.sleep(20)
    return False

def extract_sku(url, name):
    match = re.search(r'H[A-Z0-9]{5,}', url)
    if match:
        return match.group(0).upper()
    return name.strip().upper()

async def scrape_hermes(page, country_code, category_path, is_jp=False):
    url = f"https://www.hermes.com/{country_code}/category/{category_path}/#|"
    
    # 日本サイト(is_jp=True)の場合は、読み込みを最大3回リトライする(絶対空にしない)
    max_retries = 3 if is_jp else 1
    
    for attempt in range(max_retries):
        try:
            await page.goto(url, wait_until="load", timeout=90000)
            await page.wait_for_selector(".product-item", timeout=30000)
            
            # スクロール回数を多めに設定
            scroll_count = 12 if is_jp else 8
            for _ in range(scroll_count):
                await page.mouse.wheel(0, 1500)
                await asyncio.sleep(1.5)
            
            items = await page.query_selector_all(".product-item")
            if len(items) == 0 and is_jp:
                print(f"    [!] 日本サイトで商品が0件です。リロードします({attempt+1}/3)")
                continue

            products = {}
            for item in items:
                name_el = await item.query_selector(".product-item-name")
                price_el = await item.query_selector(".product-item-price")
                link_el = await item.query_selector("a")
                if name_el and link_el:
                    name = (await name_el.inner_text()).strip()
                    price = (await price_el.inner_text()).strip() if price_el else "0"
                    link = await link_el.get_attribute("href")
                    sku = extract_sku(link, name)
                    products[sku] = {"name": name, "price": price, "url": f"https://www.hermes.com{link}"}
            
            print(f"    -> {country_code}: {len(products)}件検知")
            return products
        except Exception as e:
            if is_jp: print(f"    [!] 日本サイト読み込みエラー: {e}")
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

    # 既存履歴SKUのロード（大文字で統一）
    all_rows = sheet_master.get_all_values()
    if not all_rows:
        sheet_master.append_row(header)
        existing_skus = set()
    else: existing_skus = {str(row[3]).strip().upper() for row in all_rows if len(row) > 3}

    sheet_today.clear()
    sheet_today.append_row(header)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = await context.new_page()
        try: await playwright_stealth.stealth_async(page)
        except: pass

        for cat_name, path_jp in CONFIG["JP"]["paths"].items():
            print(f"\n【{cat_name}】調査開始...")
            # 日本サイトの在庫を確実に取得(is_jp=True)
            jp_inv = await scrape_hermes(page, CONFIG["JP"]["code"], path_jp, is_jp=True)
            
            for country in ["FR", "HK", "US", "KR"]:
                try:
                    print(f"  -> {country} を確認中...")
                    os_inv = await scrape_hermes(page, CONFIG[country]["code"], CONFIG[country]["paths"][cat_name])
                    
                    to_write = []
                    for sku, data in os_inv.items():
                        # 日本サイトのリスト、および既存履歴の両方に存在しない場合のみ
                        sku_upper = str(sku).strip().upper()
                        if sku_upper not in jp_inv and sku_upper not in existing_skus:
                            try:
                                num = float(re.sub(r'[^\d.]', '', data['price'].replace(',', '')))
                                jpy = int(num * EXCHANGE_RATES.get(country, 1.0))
                            except: jpy = 0
                            row = [today_date, cat_name, country, sku_upper, data['name'], data['price'], f"¥{jpy:,}", data['url']]
                            to_write.append(row)
                    
                    if to_write:
                        print(f"    ☆ {len(to_write)}件の日本未入荷品を発見。")
                        # 書き込みが物理的に確認できるまで、ループを止めて待機
                        if await block_until_written(sheet_master, to_write):
                            await block_until_written(sheet_today, to_write)
                            # 成功後に既存セットへ追加
                            for item in to_write: existing_skus.add(str(item[3]).upper())
                        await asyncio.sleep(10) # API休憩
                    else:
                        print(f"    [なし] {country} に新しい未入荷品はありません。")
                
                except Exception as e:
                    print(f"    [!] {country} の調査中にエラー(スキップ): {e}")
                
                await asyncio.sleep(5) # 国切り替え前のインターバル
            await asyncio.sleep(10) # カテゴリ切り替え前のインターバル
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
