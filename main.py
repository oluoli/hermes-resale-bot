import asyncio
import os
import json
import gspread
import re
import time
import random
from datetime import datetime, timedelta, timezone
from playwright.async_api import async_playwright
# インポート方法を変更してエラーを回避
from playwright_stealth import stealth_async
from oauth2client.service_account import ServiceAccountCredentials

# --- 設定：最新の為替レート (2026年想定) ---
EXCHANGE_RATES = {
    "FR": 166.0,  # EUR
    "HK": 20.5,   # HKD
    "US": 156.0,  # USD
    "KR": 0.11    # KRW
}

# --- カテゴリー設定 (全パス省略なし) ---
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

# --- 職人の呼吸 (ランダムな待機でボット検知を回避) ---
async def artisan_wait(min_sec=4, max_sec=10):
    await asyncio.sleep(random.uniform(min_sec, max_sec))

# --- 商品詳細（画像URL、価格、品番）の抽出 ---
async def extract_item_details(item):
    try:
        name_el = await item.query_selector(".product-item-name")
        price_el = await item.query_selector(".product-item-price")
        link_el = await item.query_selector("a")
        img_el = await item.query_selector("img")
        
        if not (name_el and link_el): return None
        
        name = (await name_el.inner_text()).strip()
        price = (await price_el.inner_text()).strip() if price_el else "0"
        link = await link_el.get_attribute("href")
        full_url = f"https://www.hermes.com{link}"
        
        # 品番抽出: URL内の H で始まるコードを探す。なければ名前にする。
        sku_match = re.search(r'H[A-Z0-9]{5,}', link)
        sku = sku_match.group(0).upper().strip() if sku_match else name.upper().strip()
        
        # 画像URL取得 (遅延読み込み data-src にも対応)
        img_src = await img_el.get_attribute("src") or await img_el.get_attribute("data-src")
        if img_src and img_src.startswith("//"):
            img_src = "https:" + img_src
            
        return {"sku": sku, "name": name, "price": price, "url": full_url, "img": img_src}
    except:
        return None

# --- BUYMAでの実在確認（隠密リサーチ版） ---
async def check_buyma_unlisted(page, sku):
    """BUYMAで検索して、商品リストが存在しなければTrueを返す"""
    search_url = f"https://www.buyma.com/r/-F1/{sku}/"
    try:
        print(f"        [BUYMA照合] 品番 {sku} を鑑定中...")
        response = await page.goto(search_url, wait_until="networkidle", timeout=60000)
        
        # BUYMAからブロック(403等)された場合は安全のため「掲載あり」とみなしてスルー
        if response.status != 200:
            print(f"        [!] BUYMA混雑中(Status:{response.status})。判定を保留します。")
            return False

        await artisan_wait(3, 6)
        
        content = await page.content()
        product_count = await page.locator(".fab-product-img").count()
        no_result = "該当する商品が見つかりませんでした" in content

        if product_count == 0 or no_result:
            print(f"        [☆お宝] BUYMA未掲載を確認しました！")
            return True
        else:
            print(f"        [既出] BUYMAで {product_count} 件の出品があります。")
            return False
    except Exception as e:
        print(f"        [!] BUYMA確認エラー: {e}")
        return False

# --- 1件ずつ記帳し、物理的に確認する職人技 (API制限自動復帰付き) ---
async def artisan_write_and_verify(sheet, row_data, max_retry=5):
    sku_to_check = str(row_data[3]).upper().strip()
    for attempt in range(max_retry):
        try:
            await artisan_wait(3, 6)
            # 数式(IMAGE関数)を維持するために USER_ENTERED を指定
            sheet.append_row(row_data, value_input_option='USER_ENTERED')
            
            # Google側の同期をじっくり待つ
            await asyncio.sleep(15) 

            # API負荷を避け、最後から20行だけを取得して物理確認
            last_rows = sheet.get_all_values()[-20:]
            if any(sku_to_check == str(r[3]).upper().strip() for r in last_rows if len(r) > 3):
                return True
            print(f"        [!] 記入未反映。再送します({attempt+1})")
        except Exception as e:
            wait_time = (attempt + 1) * 60
            print(f"        [API制限] Googleが休憩を求めています。{wait_time}秒停止します... ({e})")
            await asyncio.sleep(wait_time)
    return False

# --- 職人のスクロール (商品が完全に出るまで粘る) ---
async def artisan_scroll(page):
    last_count = 0
    for _ in range(15):
        items = await page.query_selector_all(".product-item")
        current_count = len(items)
        if current_count > 0 and current_count == last_count:
            break
        last_count = current_count
        # 人間らしくランダムな量でスクロール
        await page.mouse.wheel(0, 800 + random.randint(0, 300))
        await asyncio.sleep(2)
        # 最下部まで一度飛ばしてLazy Loadを刺激
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(2)

async def scrape_hermes_artisan(page, country_code, category_path, is_jp=False):
    url = f"https://www.hermes.com/{country_code}/category/{category_path}/#|"
    for attempt in range(5 if is_jp else 2):
        try:
            print(f"    -> {country_code} を視察中... ({attempt+1})")
            await page.goto(url, wait_until="load", timeout=120000)
            await page.wait_for_selector(".product-item", timeout=30000)
            await artisan_scroll(page)

            items = await page.query_selector_all(".product-item")
            if is_jp and len(items) == 0:
                print(f"    [!] 日本サイト商品0件のため再読み込み...")
                continue

            products = {}
            for item in items:
                await item.scroll_into_view_if_needed()
                details = await extract_item_details(item)
                if details:
                    products[details["sku"]] = details
            
            print(f"    [完了] {country_code}: {len(products)}個の商品を正確に把握")
            return products
        except:
            await asyncio.sleep(10)
    return None if is_jp else {}

async def run():
    # --- 認証とシート準備 ---
    creds_json = json.loads(os.environ["GOOGLE_CREDENTIALS"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive'])
    client = gspread.authorize(creds)
    spreadsheet = client.open("Hermes_Check_List")
    
    # 各種シートの取得・生成
    sheets = {}
    for title in ["Master", "Today_New", "BUYMA_Unlisted"]:
        try: sheets[title] = spreadsheet.worksheet(title)
        except:
            sheets[title] = spreadsheet.add_worksheet(title=title, rows="2000", cols="20")
            sheets[title].append_row(["追加日", "ジャンル", "国", "品番", "商品名", "現地価格", "円目安", "画像", "URL"])

    JST = timezone(timedelta(hours=+9), 'JST')
    today_date = datetime.now(JST).strftime("%Y/%m/%d")
    
    # 既存データのロード
    master_all = sheets["Master"].get_all_values()
    existing_skus = {str(row[3]).upper().strip() for row in master_all if len(row) > 3}

    # 今日の新着シートをリセット
    sheets["Today_New"].clear()
    sheets["Today_New"].append_row(["追加日", "ジャンル", "国", "品番", "商品名", "現地価格", "円目安", "画像", "URL"])

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            viewport={"width": 2560, "height": 1440}
        )
        
        h_page = await context.new_page()
        b_page = await context.new_page()
        
        # エラー修正：stealth_async を正しく呼び出す
        await stealth_async(h_page)
        await stealth_async(b_page)

        for cat_name, path_jp in CONFIG["JP"]["paths"].items():
            print(f"\n--- 【職人リサーチ】カテゴリー: {cat_name} ---")
            
            # 1. 日本サイトを完璧にスキャン（フィルター網の構築）
            jp_inv = await scrape_hermes_artisan(h_page, "jp/ja", path_jp, is_jp=True)
            if jp_inv is None:
                print(f"    [中断] 日本サイト読み込み不可。スキップします。")
                continue
            
            # 2. 海外4カ国を巡回
            for country_key in ["FR", "HK", "US", "KR"]:
                print(f"  [{country_key}] 調査開始...")
                target_path = CONFIG[country_key]["paths"].get(cat_name)
                if not target_path: continue
                
                os_inv = await scrape_hermes_artisan(h_page, CONFIG[country_key]["code"], target_path)
                if not os_inv: continue

                for sku, data in os_inv.items():
                    sku_upper = str(sku).upper().strip()
                    
                    # 日本に存在せず、かつマスター台帳にも未記載の場合のみ
                    if sku_upper not in jp_inv and sku_upper not in existing_skus:
                        # 3. BUYMA実在確認
                        is_buyma_exclusive = await check_buyma_unlisted(b_page, sku_upper)
                        
                        try:
                            num_str = re.sub(r'[^\d.]', '', data['price'].replace(',', ''))
                            jpy = int(float(num_str) * EXCHANGE_RATES.get(country_key, 1.0))
                        except: jpy = 0
                        
                        # 画像表示用の数式
                        img_formula = f'=IMAGE("{data["img"]}")' if data["img"] else "No Image"
                        
                        row = [today_date, cat_name, country_key, sku_upper, data['name'], data['price'], f"¥{jpy:,}", img_formula, data['url']]
                        
                        print(f"      [記帳中] {data['name']}")
                        # マスターに記帳し、物理確認
                        if await artisan_write_and_verify(sheets["Master"], row):
                            # 今日の新着にも記帳
                            sheets["Today_New"].append_row(row, value_input_option='USER_ENTERED')
                            
                            # BUYMA未掲載なら「ブルーオーシャンシート」にも記帳
                            if is_buyma_exclusive:
                                await artisan_write_and_verify(sheets["BUYMA_Unlisted"], row)
                            
                            existing_skus.add(sku_upper)
                        
                        await artisan_wait(6, 12)
                
                await artisan_wait(15, 30)
            
            print(f"--- {cat_name} 完了。APIリセットのために大休憩します。 ---")
            await asyncio.sleep(45)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
