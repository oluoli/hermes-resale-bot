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
        "ゴールドジュエリー": "bijouterie/bijoux-en-or", "ブレスレット": "femme/accessoires-bijoux/bracelets",
        "ネックレス": "femme/accessoires-bijoux/colliers-et-pendentifs", "耳飾り": "femme/accessoires-bijoux/boucles-d-oreilles",
        "リング": "femme/accessoires-bijoux/bagues", "ベルト": "femme/ceintures",
        "スカーフ": "femme/carres-chales-et-echarpes/carres-et-accessoires-de-soie",
        "ブランケット": "maison/textiles", "ベビーギフト": "cadeaux-et-petit-h/cadeaux-de-naissance",
        "ペット": "maison-plein-air-et-equitation/equitation-et-chien/chien",
        "PetitH": "petit-h", "バッグ": "femme/sacs-et-petite-maroquinerie/sacs-et-pochettes",
        "メンズバッグ": "homme/sacs-et-petite-maroquinerie/sacs", "テーブルウェア": "maison/art-de-la-table"
    }},
    "HK": {"code": "hk/en", "paths": {
        "ゴールドジュエリー": "jewelry/gold-jewelry", "ブレスレット": "women/fashion-jewelry/bracelets",
        "ネックレス": "women/fashion-jewelry/necklaces-and-pendants", "耳飾り": "women/fashion-jewelry/earrings",
        "リング": "women/fashion-jewelry/rings", "ベルト": "women/belts",
        "スカーフ": "women/scarves-shawls-and-stoles/silk-scarves-and-accessories",
        "ブランケット": "home/textiles", "ベビーギフト": "gifts-and-petit-h/baby-gifts",
        "ペット": "home-outdoor-and-equestrian/equestrian-and-dogs/dog",
        "PetitH": "petit-h", "バッグ": "women/bags-and-small-leather-goods/bags-and-clutches",
        "メンズバッグ": "men/bags-and-small-leather-goods/bags", "テーブルウェア": "home/tableware"
    }},
    "US": {"code": "us/en", "paths": {
        "ゴールドジュエリー": "jewelry/gold-jewelry", "ブレスレット": "women/fashion-jewelry/bracelets",
        "ネックレス": "women/fashion-jewelry/necklaces-and-pendants", "耳飾り": "women/fashion-jewelry/earrings",
        "リング": "women/fashion-jewelry/rings", "ベルト": "women/belts",
        "スカーフ": "women/scarves-shawls-and-stoles/silk-scarves-and-accessories",
        "ブランケット": "home/textiles", "ベビーギフト": "gifts-and-petit-h/baby-gifts",
        "ペット": "home-outdoor-and-equestrian/equestrian-and-dogs/dog",
        "PetitH": "petit-h", "バッグ": "women/bags-and-small-leather-goods/bags-and-clutches",
        "メンズバッグ": "men/bags-and-small-leather-goods/bags", "テーブルウェア": "home/tableware"
    }},
    "KR": {"code": "kr/ko", "paths": {
        "ゴールドジュエリー": "jewelry/gold-jewelry", "ブレスレット": "women/fashion-jewelry/bracelets",
        "ネックレス": "women/fashion-jewelry/necklaces-and-pendants", "耳飾り": "women/fashion-jewelry/earrings",
        "リング": "women/fashion-jewelry/rings", "ベルト": "women/belts",
        "スカーフ": "women/scarves-shawls-and-stoles/silk-scarves-and-accessories",
        "ブランケット": "home/textiles", "ベビーギフト": "gifts-and-petit-h/baby-gifts",
        "ペット": "home-outdoor-and-equestrian/equestrian-and-dogs/dog",
        "PetitH": "petit-h", "バッグ": "women/bags-and-small-leather-goods/bags-and-clutches",
        "メンズバッグ": "men/bags-and-small-leather-goods/bags", "テーブルウェア": "home/tableware"
    }}
}

async def scrape_hermes(page, country_code, category_path):
    url = f"https://www.hermes.com/{country_code}/category/{category_path}/#|"
    try:
        await page.goto(url, wait_until="load", timeout=90000)
        await page.wait_for_selector(".product-item", timeout=30000)
        for _ in range(8):
            await page.mouse.wheel(0, 1000)
            await asyncio.sleep(1)
        items = await page.query_selector_all(".product-item")
        products = {}
        for item in items:
            name_el = await item.query_selector(".product-item-name")
            price_el = await item.query_selector(".product-item-price")
            link_el = await item.query_selector("a")
            if name_el and link_el:
                name = (await name_el.inner_text()).strip()
                price = (await price_el.inner_text()).strip() if price_el else "0"
                link = await link_el.get_attribute("href")
                sku = re.search(r'H[A-Z0-9]{5,}', link).group(0) if re.search(r'H[A-Z0-9]{5,}', link) else name
                products[sku] = {"name": name, "price": price, "url": f"https://www.hermes.com{link}"}
        print(f"    -> {country_code}: {len(products)}個検知")
        return products
    except:
        print(f"    [!] {country_code} スキップ (読み込み失敗)")
        return {}

async def run():
    # --- 1. 認証とシート準備 ---
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

    # 既存データの読み込み（1回だけ）
    master_all_values = sheet_master.get_all_values()
    if not master_all_values:
        sheet_master.append_row(header)
        existing_skus = set()
    else:
        existing_skus = {row[3] for row in master_all_values if len(row) > 3}

    # --- 2. スクレイピング（全データをリストに溜める） ---
    final_append_list = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0...", viewport={"width": 1280, "height": 1080})
        page = await context.new_page()
        await playwright_stealth.stealth_async(page)

        for cat_name, path_jp in CONFIG["JP"]["paths"].items():
            print(f"\n調査開始: {cat_name}")
            jp_inv = await scrape_hermes(page, CONFIG["JP"]["code"], path_jp)
            
            for country in ["FR", "HK", "US", "KR"]:
                os_inv = await scrape_hermes(page, CONFIG[country]["code"], CONFIG[country]["paths"][cat_name])
                
                for sku, data in os_inv.items():
                    if sku not in jp_inv and sku not in existing_skus:
                        # 価格換算
                        p_num = float(re.sub(r'[^\d.]', '', data['price'].replace(',', ''))) if data['price'] != "0" else 0
                        jpy = int(p_num * EXCHANGE_RATES.get(country, 1.0))
                        
                        row = [today_date, cat_name, country, sku, data['name'], data['price'], f"¥{jpy:,}", data['url']]
                        final_append_list.append(row)
                        existing_skus.add(sku) # 同じ実行内での重複防止
                await asyncio.sleep(2)
        await browser.close()

    # --- 3. 最後に一括書き込み（ここが改善の肝） ---
    if final_append_list:
        print(f"\n--- 書き込みフェーズ ---")
        print(f"合計 {len(final_append_list)} 件の新規アイテムを書き込みます...")
        
        # 今日の新着シートをリセット
        sheet_today.clear()
        sheet_today.append_row(header)

        # 失敗してもやり直すループ
        for target_sheet in [sheet_master, sheet_today]:
            for attempt in range(5):
                try:
                    target_sheet.append_rows(final_append_list)
                    print(f"  [OK] {target_sheet.title} への書き込み完了")
                    break
                except Exception as e:
                    print(f"  [!] {target_sheet.title} 失敗 (リトライ {attempt+1}): {e}")
                    await asyncio.sleep(20) # 長めに待つ
    else:
        print("\n新着アイテムはありませんでした。")

if __name__ == "__main__":
    asyncio.run(run())
