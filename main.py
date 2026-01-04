import asyncio
import os
import json
import gspread
import re
import time
import random
import logging
import sys
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Set, Any
from oauth2client.service_account import ServiceAccountCredentials
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

# --- 設定：為替レート ＆ カテゴリー ---
EXCHANGE_RATES = {"FR": 166.5, "HK": 20.8, "US": 158.0, "KR": 0.115}

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
        "PetitH": "petit-h/all-petit-h", "バッグ": "women/bags-and-small-leather-goods/bags-and-clutches",
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

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(message)s')
log = logging.getLogger("Artisan")

async def write_and_confirm(sheet, row_data, max_retry=3):
    """【昨日成功したロジック】記入後に最新5行を確認する"""
    sku_target = str(row_data[3]).upper().strip()
    for attempt in range(max_retry):
        try:
            await asyncio.sleep(2)
            sheet.append_row(row_data)
            log.info(f"      [待機] 品番 {sku_target} の反映を待っています(12秒)...")
            await asyncio.sleep(12)
            
            last_rows = sheet.get_all_values()[-5:]
            for r in last_rows:
                if len(r) > 3 and str(r[3]).upper().strip() == sku_target:
                    log.info(f"      ✅ [確認] 品番 {sku_target} をシートに刻みました。")
                    return True
            log.warning(f"      [!] 反映が確認できません。リトライ中 ({attempt+1})")
        except Exception as e:
            log.error(f"      [API制限] 60秒休息します... ({e})")
            await asyncio.sleep(60)
    return False

async def scrape_site(page, country_code, category_path, is_jp=False):
    """【昨日成功したロジック】シンプルで力強い巡回"""
    url = f"https://www.hermes.com/{country_code}/category/{category_path}/#|"
    
    for attempt in range(5 if is_jp else 2):
        try:
            log.info(f"   -> {country_code} を調査中... ({attempt+1})")
            await page.goto(url, wait_until="load", timeout=120000)
            
            try:
                await page.wait_for_selector(".product-item", timeout=30000)
            except:
                log.info(f"      [報告] 在庫なし。")
                return {}

            # スクロール
            for _ in range(15 if is_jp else 8):
                await page.mouse.wheel(0, 800)
                await asyncio.sleep(1.5)
            
            items = await page.query_selector_all(".product-item")
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
                    
                    sku_match = re.search(r'H[A-Z0-9]{5,}', link)
                    sku = sku_match.group(0).upper().strip() if sku_match else name.upper().strip()
                    products[sku] = {"name": name, "price": price, "url": f"https://www.hermes.com{link}"}
            
            if is_jp and len(products) == 0:
                log.warning("      [!] 日本サイトが0件です。リロードします。")
                continue
                
            log.info(f"   ✅ {country_code}: {len(products)}個を補足")
            return products
        except Exception as e:
            log.error(f"      [失敗] ページ読み込みエラー: {e}")
            await asyncio.sleep(10)
    return None if is_jp else {}

async def run():
    # --- スプレッドシート準備 ---
    creds_json = json.loads(os.environ["GOOGLE_CREDENTIALS"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive'])
    client = gspread.authorize(creds)
    
    # 物理的な実在確認
    spreadsheet = client.open("Hermes_Check_List")
    sheet_master = spreadsheet.get_worksheet(0)
    try: sheet_today = spreadsheet.worksheet("todays_new")
    except: sheet_today = spreadsheet.add_worksheet(title="todays_new", rows="5000", cols="20")

    log.info(f"💡 物理接続完了: {spreadsheet.url}")

    JST = timezone(timedelta(hours=+9), 'JST')
    today_date = datetime.now(JST).strftime("%Y/%m/%d")
    
    # 既存データの記憶
    master_all = sheet_master.get_all_values()
    existing_skus = {str(row[3]).upper().strip() for row in master_all if len(row) > 3}
    sheet_today.clear()
    sheet_today.append_row(["追加日", "ジャンル", "国", "品番", "商品名", "現地価格", "日本円目安", "URL"])

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 2560, "height": 1440})
        page = await context.new_page()
        await stealth_async(page)

        for cat_name, path_jp in CONFIG["JP"]["paths"].items():
            log.info(f"\n{'='*60}\n【職人リサーチ】カテゴリー: {cat_name}\n{'='*60}")
            
            # 日本サイトのキャッシュ構築
            jp_inv = await scrape_site(page, "jp/ja", path_jp, is_jp=True)
            if jp_inv is None:
                log.critical(f"❌ 日本サイト『{cat_name}』の取得に失敗。仕事を拒否します。")
                continue # 次のカテゴリーへ
            
            for country in ["FR", "HK", "US", "KR"]:
                log.info(f"   [{country}] 調査中...")
                os_inv = await scrape_site(page, CONFIG[country]["code"], CONFIG[country]["paths"][cat_name])
                
                if not os_inv: continue

                for sku, data in os_inv.items():
                    sku_upper = str(sku).upper().strip()
                    
                    if sku_upper not in jp_inv and sku_upper not in existing_skus:
                        log.info(f"      [発見] 日本未入荷: {data['name']} ({sku_upper})")
                        
                        try:
                            num = float(re.sub(r'[^\d.]', '', data['price'].replace(',', '')))
                            jpy = int(num * EXCHANGE_RATES.get(country, 1.0))
                        except: jpy = 0
                        
                        row = [today_date, cat_name, country, sku_upper, data['name'], data['price'], f"¥{jpy:,}", data['url']]
                        
                        # 記入 ＆ 検証
                        if await write_and_confirm(sheet_master, row):
                            await write_and_confirm(sheet_today, row)
                            existing_skus.add(sku_upper)
                        
                        await asyncio.sleep(random.uniform(5, 10))

                await asyncio.sleep(15)
            
            log.info(f"--- {cat_name} 完了。休憩します。 ---")
            await asyncio.sleep(45)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
