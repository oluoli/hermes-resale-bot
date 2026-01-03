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

# --- 職人の呼吸（ランダムな待機） ---
async def artisan_wait(min_sec=3, max_sec=7):
    wait = random.uniform(min_sec, max_sec)
    await asyncio.sleep(wait)

# --- 1件ずつ記帳し、ピンポイントで反映を確認する職人技 ---
async def artisan_write_and_confirm(sheet, row_data, max_retry=3):
    sku_to_check = str(row_data[3]).upper().strip()
    for attempt in range(max_retry):
        try:
            # 記帳前に少し待つ（人間が入力する間隔）
            await artisan_wait(4, 8)
            sheet.append_row(row_data)
            
            # Googleの同期をじっくり待つ
            await asyncio.sleep(12) 

            # API負荷を避けるため、最後の数行だけを取得して確認
            # (全件取得col_valuesは制限に引っかかりやすいため)
            last_rows = sheet.get_all_values()[-5:] # 最新の5行
            for r in last_rows:
                if len(r) > 3 and str(r[3]).upper().strip() == sku_to_check:
                    print(f"        [確実] 品番 {sku_to_check} をシートに刻みました。")
                    return True
            
            print(f"        [!] 反映が確認できません。リトライします({attempt+1})")
        except Exception as e:
            print(f"        [API制限待機] Googleが混み合っています。60秒深呼吸します... ({e})")
            await asyncio.sleep(60)
    return False

def extract_sku(url, name):
    match = re.search(r'H[A-Z0-9]{5,}', url)
    return match.group(0).upper().strip() if match else name.upper().strip()

async def scrape_hermes_artisan(page, country_code, category_path, is_jp=False):
    url = f"https://www.hermes.com/{country_code}/category/{category_path}/#|"
    
    # 日本サイトの取得失敗はbotにとって致命傷なため、最大5回リトライ
    for attempt in range(5 if is_jp else 2):
        try:
            print(f"    -> {country_code} を丁寧に見聞中... ({attempt+1})")
            await page.goto(url, wait_until="load", timeout=120000)
            await page.wait_for_selector(".product-item", timeout=30000)
            
            # 職人による丁寧なスクロール（ゆっくり全件を出し切る）
            for _ in range(15 if is_jp else 8):
                await page.mouse.wheel(0, 700)
                await asyncio.sleep(1.5)
            
            items = await page.query_selector_all(".product-item")
            if is_jp and len(items) == 0:
                print(f"    [!] 日本サイトに商品がありません。リロードします。")
                continue

            products = {}
            for item in items:
                # 確実に表示させてから読み取る
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
            
            print(f"    [成功] {country_code}: {len(products)}個を正確に把握")
            return products
        except Exception:
            await asyncio.sleep(10)
    return None if is_jp else {}

async def run():
    # --- シート準備 ---
    creds_json = json.loads(os.environ["GOOGLE_CREDENTIALS"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive'])
    client = gspread.authorize(creds)
    spreadsheet = client.open("Hermes_Check_List")
    sheet_master = spreadsheet.get_worksheet(0)
    try: sheet_today = spreadsheet.worksheet("Today_New")
    except: sheet_today = spreadsheet.add_worksheet(title="Today_New", rows="100", cols="20")

    JST = timezone(timedelta(hours=+9), 'JST')
    today_date = datetime.now(JST).strftime("%Y/%m/%d")
    
    # 既存履歴の読み込み（大文字統一）
    master_all = sheet_master.get_all_values()
    existing_skus = {str(row[3]).upper().strip() for row in master_all if len(row) > 3}

    sheet_today.clear()
    sheet_today.append_row(["追加日", "ジャンル", "国", "品番", "商品名", "現地価格", "日本円目安", "URL"])

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # 高解像度モニターをシミュレートして一度に多くを検知
        context = await browser.new_context(user_agent="Mozilla/5.0...", viewport={"width": 2560, "height": 1440})
        page = await context.new_page()
        try: await playwright_stealth.stealth_async(page)
        except: pass

        for cat_name, path_jp in CONFIG["JP"]["paths"].items():
            print(f"\n--- 【職人リサーチ開始】カテゴリー: {cat_name} ---")
            
            # 日本サイトを「完璧に」読み込むまで次に行かない
            jp_inv = await scrape_hermes_artisan(page, "jp/ja", path_jp, is_jp=True)
            if jp_inv is None:
                print(f"    [中断] 日本サイトが読み込めないため、このカテゴリーの調査は飛ばします。")
                continue
            
            for country in ["FR", "HK", "US", "KR"]:
                print(f"  [{country}] 調査開始...")
                os_inv = await scrape_hermes_artisan(page, CONFIG[country]["code"], CONFIG[country]["paths"][cat_name])
                
                if not os_inv:
                    print(f"    [通知] {country} に在庫がない、または読み込みをスキップしました。")
                    continue

                for sku, data in os_inv.items():
                    sku_upper = str(sku).upper().strip()
                    
                    # 【照合工程】日本にあるか？ 既にリストにあるか？
                    if sku_upper not in jp_inv and sku_upper not in existing_skus:
                        # 【計算工程】
                        try:
                            num = float(re.sub(r'[^\d.]', '', data['price'].replace(',', '')))
                            jpy = int(num * EXCHANGE_RATES.get(country, 1.0))
                        except: jpy = 0
                        
                        row = [today_date, cat_name, country, sku_upper, data['name'], data['price'], f"¥{jpy:,}", data['url']]
                        
                        print(f"      [発見] 日本未入荷: {data['name']} を精査中...")
                        
                        # 【記入工程】マスターと本日に1件ずつ、確実に記入
                        if await artisan_write_and_confirm(sheet_master, row):
                            await artisan_write_and_confirm(sheet_today, row)
                            # 成功したらリストに追加（重複防止）
                            existing_skus.add(sku_upper)
                            
                        # 次の商品へ行く前に少し休む（リサーチの間隔）
                        await artisan_wait(5, 10)
                
                # 国ごとの間隔を長めにとる
                await artisan_wait(10, 20)
            
            # カテゴリーが切り替わる時はAPI制限のリセットを兼ねて大休憩
            print(f"--- {cat_name} 完了。APIの休憩をとります。 ---")
            await asyncio.sleep(30)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
