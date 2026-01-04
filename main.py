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

# --- 設定：最新の為替レート (2026年想定) ---
EXCHANGE_RATES = {"FR": 166.0, "HK": 20.5, "US": 156.0, "KR": 0.11}

# --- カテゴリー設定 (全5カ国・14カテゴリー・一切の省略なし) ---
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
        "PetitH": "petit-h/all-petit-h",
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

# --- 職人の待機 ---
async def artisan_wait(min_sec=4, max_sec=9):
    await asyncio.sleep(random.uniform(min_sec, max_sec))

# --- 商品詳細の精密抽出 (リトライ機能込) ---
async def extract_details_from_el(item_el):
    try:
        await item_el.scroll_into_view_if_needed()
        name_el = await item_el.query_selector(".product-item-name")
        price_el = await item_el.query_selector(".product-item-price")
        link_el = await item_el.query_selector("a")
        
        if not (name_el and link_el): return None
        
        name = (await name_el.inner_text()).strip()
        
        # 価格取得リトライ
        price = "0"
        for _ in range(3):
            price_text = await price_el.inner_text() if price_el else "0"
            price = re.sub(r'[^\d.]', '', price_text.replace(',', ''))
            if price and price != "0": break
            await asyncio.sleep(1.5)

        link = await link_el.get_attribute("href")
        full_url = f"https://www.hermes.com{link}"
        sku_match = re.search(r'H[A-Z0-9]{5,}', link)
        sku = sku_match.group(0).upper().strip() if sku_match else name.upper().strip()
            
        return {"sku": sku, "name": name, "price": price, "url": full_url}
    except: return None

# --- スプレッドシート記帳 ＆ 物理反映確認 ---
async def artisan_write_and_verify(sheets, row_data, max_retry=3):
    sku_to_check = str(row_data[3]).upper().strip()
    for attempt in range(max_retry):
        try:
            await artisan_wait(3, 6)
            # マスターへ記帳
            res = sheets["Master"].append_row(row_data)
            # 更新されたセルの行番号を取得
            updated_range = res.get('updates', {}).get('updatedRange', '')
            row_idx = re.search(r'A(\d+)', updated_range).group(1)
            
            # 反映待ち
            await asyncio.sleep(10)
            
            # 書き込まれた中身を読み戻して「検品」
            actual_sku = sheets["Master"].cell(row_idx, 4).value
            if str(actual_sku).upper().strip() == sku_to_check:
                # 合格なら Today_New にも記帳
                sheets["Today_New"].append_row(row_data)
                return True
            else:
                print(f"        [!] 検証不合格 (Row:{row_idx})。再送します...")
        except Exception as e:
            print(f"        [!] API制限または通信エラー: {e}。休息中...")
            await asyncio.sleep(40)
    return False

# --- 執念のスクロール ---
async def artisan_scroll(page):
    last_count = 0
    for _ in range(15):
        items = await page.query_selector_all(".product-item")
        current_count = len(items)
        if current_count > 0 and current_count == last_count: break
        last_count = current_count
        await page.mouse.wheel(0, 1000 + random.randint(0, 300))
        await asyncio.sleep(2.5)
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(2)

async def run():
    # --- Google認証 ---
    creds_json = json.loads(os.environ["GOOGLE_CREDENTIALS"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive'])
    client = gspread.authorize(creds)
    spreadsheet = client.open("Hermes_Check_List")
    
    sheets = {}
    header = ["追加日", "ジャンル", "国", "品番", "商品名", "現地価格", "日本円目安", "URL"]
    for title in ["Master", "Today_New"]:
        try: sheets[title] = spreadsheet.worksheet(title)
        except:
            sheets[title] = spreadsheet.add_worksheet(title=title, rows="4000", cols="20")
            sheets[title].append_row(header)

    JST = timezone(timedelta(hours=+9), 'JST')
    today_date = datetime.now(JST).strftime("%Y/%m/%d")
    
    # 重複回避リストのロード
    existing_skus = set([str(s).upper().strip() for s in sheets["Master"].col_values(4)])
    sheets["Today_New"].clear()
    sheets["Today_New"].append_row(header)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}, locale="ja-JP"
        )
        page = await context.new_page()
        
        # ステルス実装 (安定版呼び出し)
        try: await playwright_stealth.stealth_async(page)
        except: pass

        target_countries = ["FR", "HK", "US", "KR"]

        for cat_name, path_jp in CONFIG["JP"]["paths"].items():
            print(f"\n【最重要工程】カテゴリー: {cat_name}")
            
            # 1. 日本在庫網の構築
            await page.goto(f"https://www.hermes.com/jp/ja/category/{path_jp}/#|", wait_until="load", timeout=120000)
            await page.wait_for_selector(".product-item", timeout=30000)
            await artisan_scroll(page)
            jp_elements = await page.query_selector_all(".product-item")
            jp_skus = set()
            for el in jp_elements:
                d = await extract_details_from_el(el)
                if d: jp_skus.add(d["sku"])
            print(f"    -> 国内網構築完了 ({len(jp_skus)}件)")

            # 2. 国別に巡回 ＆ 一品完遂処理
            for country_key in target_countries:
                print(f"\n  --- [{country_key}] リサーチ開始 ---")
                target_path = CONFIG[country_key]["paths"].get(cat_name)
                if not target_path: continue
                
                await page.goto(f"https://www.hermes.com/{CONFIG[country_key]['code']}/category/{target_path}/#|", wait_until="load", timeout=120000)
                await page.wait_for_selector(".product-item", timeout=30000)
                await artisan_scroll(page)
                
                os_elements = await page.query_selector_all(".product-item")
                print(f"    -> 現場要素検知: {len(os_elements)}件。個別同期を開始します。")

                for i, el in enumerate(os_elements):
                    # 【核心】一品ごとに読み取り、書き込み、検証を完結させる
                    data = await extract_details_from_el(el)
                    if not data: continue
                    
                    sku_upper = str(data['sku']).upper().strip()
                    print(f"      ({i+1}/{len(os_elements)}) {data['name']} ({sku_upper})")
                    
                    # 国内在庫・台帳既出のチェック
                    if sku_upper in jp_skus:
                        print(f"        -> スキップ: 日本に存在します。")
                        continue
                    if sku_upper in existing_skus:
                        print(f"        -> スキップ: 既に記帳済みです。")
                        continue
                    
                    # 計算
                    try:
                        jpy = int(float(data['price']) * EXCHANGE_RATES.get(country_key, 1.0))
                    except: jpy = 0
                    row = [today_date, cat_name, country_key, sku_upper, data['name'], data['price'], f"¥{jpy:,}", data['url']]
                    
                    # 【同期】記帳 ＆ 検品 (成功するまでループを離さない)
                    print(f"        [記帳] スプレッドシート同期中...")
                    if await artisan_write_and_verify(sheets, row):
                        existing_skus.add(sku_upper)
                        print(f"        [完遂] 検品合格。次へ。")
                    else:
                        print(f"        [失敗] この商品の記帳を断念しました。")
                    
                    # 一品完遂後の待機
                    await artisan_wait(5, 10)

                print(f"  --- [{country_key}] 全商品の直列処理終了 ---")
                await artisan_wait(15, 30)
            
            print(f"--- カテゴリー[{cat_name}] 完走 ---")
            await asyncio.sleep(45)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
