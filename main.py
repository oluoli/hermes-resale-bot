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

# --- 職人の呼吸 (ランダムな待機) ---
async def artisan_wait(min_sec=4, max_sec=10):
    await asyncio.sleep(random.uniform(min_sec, max_sec))

# --- 商品詳細の抽出工程 (価格リトライロジック込) ---
async def extract_item_details(item):
    try:
        name_el = await item.query_selector(".product-item-name")
        price_el = await item.query_selector(".product-item-price")
        link_el = await item.query_selector("a")
        
        if not (name_el and link_el): return None
        
        name = (await name_el.inner_text()).strip()
        
        # 価格取得の粘り
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

# --- BUYMAでの実在確認 (超精密・タイトルマッチング版) ---
async def check_buyma_unlisted_strict(page, sku):
    """一品ごとにバイマへ飛び、おすすめを排除して最新状況を鑑定する"""
    search_url = f"https://www.buyma.com/r/-F1/{sku}/"
    try:
        print(f"        [バイマ鑑定] 品番 {sku} を現場照合中...")
        await page.mouse.move(random.randint(0, 500), random.randint(0, 500))
        response = await page.goto(search_url, wait_until="networkidle", timeout=60000)
        
        if response.status != 200:
            print(f"        [!] BUYMA混雑中。安全のため掲載ありと判定。")
            return False

        await artisan_wait(4, 7)
        
        content = await page.content()
        # 判定1: ヒットなしメッセージ
        no_result_msg = "該当する商品が見つかりませんでした" in content

        # 判定2: タイトルマッチング (おすすめ商品を弾く)
        titles = await page.locator(".fab-product-name").all_inner_texts()
        sku_hit = any(sku in t.upper().replace(" ", "") for t in titles)

        if no_result_msg or (not sku_hit):
            print(f"        [☆未掲載確定] BUYMAにお宝発見！")
            return True
        else:
            print(f"        [既出] バイマに類似・該当商品を検知しました。")
            return False
    except: return False

# --- 1件ずつ記帳し、物理的に確認する職人技 (API負荷軽減版) ---
async def artisan_write_and_verify_single(sheet, row_data, max_retry=3):
    """書き込んだ直後の1行をピンポイントで読み戻し確認する"""
    sku_to_check = str(row_data[3]).upper().strip()
    for attempt in range(max_retry):
        try:
            await artisan_wait(3, 6)
            res = sheet.append_row(row_data)
            # D列(品番)だけを読み取って確認
            row_idx = res['updates']['updatedRange'].split('!A')[-1].split(':')[0]
            await asyncio.sleep(8) 
            val = sheet.cell(row_idx, 4).value
            if str(val).upper().strip() == sku_to_check:
                return True
            print(f"        [!] 物理反映が確認できません。再試行({attempt+1})")
        except: 
            print(f"        [API制限待機] 30秒休止...")
            await asyncio.sleep(30)
    return False

# --- 執念のスクロール ---
async def artisan_scroll(page):
    last_count = 0
    for _ in range(15):
        items = await page.query_selector_all(".product-item")
        current_count = len(items)
        if current_count > 0 and current_count == last_count: break
        last_count = current_count
        await page.mouse.wheel(0, 900 + random.randint(0, 300))
        await asyncio.sleep(2)
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(2)

# --- 一覧取得工程 ---
async def scrape_hermes_listing(page, country_code, category_path, is_jp=False):
    url = f"https://www.hermes.com/{country_code}/category/{category_path}/#|"
    try:
        print(f"    -> {country_code} ページ展開中...")
        await page.goto(url, wait_until="load", timeout=120000)
        await page.wait_for_selector(".product-item", timeout=30000)
        await artisan_scroll(page)
        return await page.query_selector_all(".product-item")
    except:
        return None if is_jp else []

async def run():
    # --- 認証とシート準備 ---
    creds_json = json.loads(os.environ["GOOGLE_CREDENTIALS"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive'])
    client = gspread.authorize(creds)
    spreadsheet = client.open("Hermes_Check_List")
    
    sheets = {}
    header = ["追加日", "ジャンル", "国", "品番", "商品名", "現地価格", "日本円目安", "URL"]
    for title in ["Master", "Today_New", "BUYMA_Unlisted"]:
        try: sheets[title] = spreadsheet.worksheet(title)
        except:
            sheets[title] = spreadsheet.add_worksheet(title=title, rows="3000", cols="20")
            sheets[title].append_row(header)

    JST = timezone(timedelta(hours=+9), 'JST')
    today_date = datetime.now(JST).strftime("%Y/%m/%d")
    
    # 重複チェック用既存リスト (Masterの品番列を取得)
    existing_skus = set([str(s).upper().strip() for s in sheets["Master"].col_values(4)])
    sheets["Today_New"].clear()
    sheets["Today_New"].append_row(header)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}, locale="ja-JP"
        )
        
        h_page = await context.new_page()
        b_page = await context.new_page()
        
        # エラーを回避する呼び出し方：await playwright_stealth.stealth_async(page)
        try: await playwright_stealth.stealth_async(h_page)
        except: pass
        try: await playwright_stealth.stealth_async(b_page)
        except: pass

        for cat_name, path_jp in CONFIG["JP"]["paths"].items():
            print(f"\n【重要工程】カテゴリー: {cat_name}")
            
            # 1. 日本サイトをスキャンし、最新の国内在庫フィルターを構築
            jp_items = await scrape_hermes_listing(h_page, "jp/ja", path_jp, is_jp=True)
            if jp_items is None:
                print(f"    [注意] 日本サイト読み取り不可。スキップ。")
                continue
            
            jp_skus = set()
            for item in jp_items:
                details = await extract_item_details(item)
                if details: jp_skus.add(details["sku"])
            print(f"    [日本フィルタ完了] {len(jp_skus)}件の国内商品を把握。")

            # 2. 海外4カ国を巡回
            for country_key in ["FR", "HK", "US", "KR"]:
                print(f"  [{country_key}] 巡回開始...")
                target_path = CONFIG[country_key]["paths"].get(cat_name)
                if not target_path: continue
                
                os_items = await scrape_hermes_listing(h_page, CONFIG[country_key]["code"], target_path)
                if not os_items: continue

                # --- 一品ずつ「検知・照合・鑑定・記帳・物理確認」を完結させるループ ---
                for item in os_items:
                    # 確実に表示させてから詳細を抽出
                    await item.scroll_into_view_if_needed()
                    data = await extract_item_details(item)
                    if not data: continue
                    
                    sku_upper = str(data['sku']).upper().strip()
                    
                    # 照合1: 日本に存在するか？ 台帳に既にあるか？
                    if sku_upper in jp_skus or sku_upper in existing_skus:
                        continue
                    
                    print(f"      [一品精査中] {data['name']} ...")

                    # 照合2: バイマで本当に未掲載か？ (現場鑑定)
                    is_unlisted = await check_buyma_unlisted_strict(b_page, sku_upper)
                    
                    # 計算
                    try:
                        jpy = int(float(data['price']) * EXCHANGE_RATES.get(country_key, 1.0))
                    except: jpy = 0
                    row = [today_date, cat_name, country_key, sku_upper, data['name'], data['price'], f"¥{jpy:,}", data['url']]
                    
                    # 照合3: 記帳・同期工程 (成功を確認するまで次へ行かない)
                    print(f"        [同期中] 全台帳への記帳と物理反映を確認中...")
                    if await artisan_write_and_verify_single(sheets["Master"], row):
                        # 他のシートへ同期
                        sheets["Today_New"].append_row(row)
                        if is_unlisted:
                            print(f"        [お宝発見] BUYMA_Unlistedに記帳。")
                            await artisan_write_and_verify_single(sheets["BUYMA_Unlisted"], row)
                        
                        # ローカルメモリを更新して重複を防ぐ
                        existing_skus.add(sku_upper)
                        print(f"        [完遂] 成功。次の一品へ。")
                    
                    # 一品終わるごとの「職人の余韻（インターバル）」
                    await artisan_wait(6, 12)

                await artisan_wait(15, 30)
            
            print(f"--- {cat_name} 完了。APIリセット休憩中 ---")
            await asyncio.sleep(45)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
