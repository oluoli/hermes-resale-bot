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
    # 確認用のSKU（今回追加する最後の品番）
    verify_sku = rows[-1][3]
    
    for attempt in range(max_attempts):
        try:
            print(f"      [書き込み試行 {attempt+1}] データ送信中...")
            sheet.append_rows(rows)
            # Google側の反映ラグを考慮して、待機時間を徐々に延ばす
            wait_time = 15 + (attempt * 10)
            print(f"      [反映待ち] {wait_time}秒間、Googleの同期を待ちます...")
            await asyncio.sleep(wait_time)
            
            # 末尾30行を読み取って物理的に存在するかチェック
            all_vals = sheet.get_all_values()
            recent_skus = [r[3] for r in all_vals[max(0, len(all_vals)-40):] if len(r) > 3]
            
            if verify_sku in recent_skus:
                print(f"      [確認完了] シートへの書き込みが物理的に成功しました。")
                return True
            print(f"      [!] 記入が確認できませんでした。再試行します。")
        except Exception as e:
            print(f"      [!] APIエラー: {e}")
            await asyncio.sleep(20)
    return False

async def scrape_hermes(page, country_code, category_path):
    url = f"https://www.hermes.com/{country_code}/category/{category_path}/#|"
    try:
        await page.goto(url, wait_until="load", timeout=90000)
        await page.wait_for_selector(".product-item", timeout=30000)
        for _ in range(7):
            await page.mouse.wheel(0, 1500)
            await asyncio.sleep(2)
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
        return products
    except: return {}

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
        context = await browser.new_context(user_agent="Mozilla/5.0...", viewport={"width": 1920, "height": 1080})
        page = await context.new_page()
        try: await playwright_stealth.stealth_async(page)
        except: pass

        for cat_name, path_jp in CONFIG["JP"]["paths"].items():
            print(f"\n【{cat_name}】調査中...")
            jp_inv = await scrape_hermes(page, CONFIG["JP"]["code"], path_jp)
            
            for country in ["FR", "HK", "US", "KR"]:
                print(f"  -> {country} スキャン中...")
                os_inv = await scrape_hermes(page, CONFIG[country]["code"], CONFIG[country]["paths"][cat_name])
                
                to_write = []
                for sku, data in os_inv.items():
                    if sku not in jp_inv and sku not in existing_skus:
                        try:
                            num = float(re.sub(r'[^\d.]', '', data['price'].replace(',', '')))
                            jpy = int(num * EXCHANGE_RATES.get(country, 1.0))
                        except: jpy = 0
                        row = [today_date, cat_name, country, sku, data['name'], data['price'], f"¥{jpy:,}", data['url']]
                        to_write.append(row)
                
                if to_write:
                    print(f"    ☆ {len(to_write)}件の未入荷品を発見。記入を開始します...")
                    # マスターに記入が成功するまで次の国へ行かせない
                    success = await block_until_written(sheet_master, to_write)
                    if success:
                        await block_until_written(sheet_today, to_write)
                        # 成功したものだけを既存リストに加える
                        for item in to_write: existing_skus.add(item[3])
                    
                    await asyncio.sleep(10) # API休憩
                else:
                    print(f"    [情報] 日本未入荷品はありませんでした。")
                
                await asyncio.sleep(5)
            await asyncio.sleep(10)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
