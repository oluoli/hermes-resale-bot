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

# --- プロフェッショナル設定 ---
EXCHANGE_RATES = {"FR": 166.0, "HK": 20.5, "US": 156.0, "KR": 0.11}

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

# --- 職人の呼吸 ---
async def artisan_jitter_delay(min_s=4, max_s=8):
    await asyncio.sleep(random.uniform(min_s, max_s))

# --- [世界一の精度] 商品情報抽出エンジン ---
async def atomic_extract(item_el):
    """DOMの状態に依存せず、確実にデータを奪取する"""
    try:
        await item_el.scroll_into_view_if_needed()
        name_el = await item_el.query_selector(".product-item-name")
        price_el = await item_el.query_selector(".product-item-price")
        link_el = await item_el.query_selector("a")
        
        if not (name_el and link_el): return None
        
        name = (await name_el.inner_text()).strip()
        
        # 価格取得の粘り：描画遅延を物理的に克服
        price = "0"
        for _ in range(4):
            raw_p = await price_el.inner_text() if price_el else "0"
            price = re.sub(r'[^\d.]', '', raw_p.replace(',', ''))
            if price and price != "0": break
            await asyncio.sleep(2)

        link = await link_el.get_attribute("href")
        full_url = f"https://www.hermes.com{link}"
        sku_match = re.search(r'H[A-Z0-9]{5,}', link)
        sku = sku_match.group(0).upper().strip() if sku_match else name.upper().strip()
            
        return {"sku": sku, "name": name, "price": price, "url": full_url}
    except: return None

# --- [世界一の信頼] 記帳 ＆ 物理反映確認トランザクション ---
async def secure_transaction_write(sheets, row_data, today_unreleased_sheet):
    """
    1. Masterへ記帳
    2. Googleサーバーから物理的に読み戻して検証
    3. 合格したら本日の日本未発売シートへ即時同期
    """
    sku_target = str(row_data[3]).upper().strip()
    for attempt in range(3):
        try:
            await artisan_jitter_delay(2, 4)
            # A. 書き込み実行
            res = sheets["Master"].append_row(row_data)
            row_idx = re.search(r'A(\d+)', res.get('updates', {}).get('updatedRange', '')).group(1)
            
            # B. 物理反映を読み戻して確認（これが職人の検品）
            await asyncio.sleep(10)
            actual_val = sheets["Master"].cell(row_idx, 4).value
            
            if str(actual_val).upper().strip() == sku_target:
                # C. 完璧な同期：本日の日本未発売シートへも記録
                today_unreleased_sheet.append_row(row_data)
                return True
            else:
                print(f"        [!] 検証失敗。再試行中...")
        except Exception as e:
            print(f"        [!] API制限: {e}。1分休憩します。")
            await asyncio.sleep(60)
    return False

# --- 執念のスクロール (タイムアウト耐性) ---
async def robust_artisan_scroll(page):
    last_h = 0
    for _ in range(15):
        current_h = await page.evaluate("document.body.scrollHeight")
        if current_h == last_h: break
        last_h = current_h
        await page.mouse.wheel(0, 1200 + random.randint(0, 400))
        await asyncio.sleep(3)
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

async def run():
    creds_json = json.loads(os.environ["GOOGLE_CREDENTIALS"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive'])
    client = gspread.authorize(creds)
    spreadsheet = client.open("Hermes_Check_List")
    
    sheets = {}
    header = ["取得日", "ジャンル", "国", "品番", "商品名", "価格", "円換算目安", "URL"]
    
    # 100点満点のシート構成
    for title in ["Master", "Today_Unreleased"]:
        try: sheets[title] = spreadsheet.worksheet(title)
        except:
            sheets[title] = spreadsheet.add_worksheet(title=title, rows="5000", cols="20")
            sheets[title].append_row(header)

    JST = timezone(timedelta(hours=+9), 'JST')
    today_date = datetime.now(JST).strftime("%Y/%m/%d")
    
    # 既存データをロード（重複排除用）
    existing_skus = set([str(s).upper().strip() for s in sheets["Master"].col_values(4)])
    
    # 本日の日本未発売シートをリフレッシュ
    sheets["Today_Unreleased"].clear()
    sheets["Today_Unreleased"].append_row(header)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}, locale="ja-JP"
        )
        page = await context.new_page()
        try: await playwright_stealth.stealth_async(page)
        except: pass

        target_countries = ["FR", "HK", "US", "KR"]

        for cat_name, path_jp in CONFIG["JP"]["paths"].items():
            print(f"\n【最高峰リサーチ】カテゴリー: {cat_name}")
            
            # 1. 日本在庫を完璧にキャッシュ (除外用)
            jp_skus = set()
            try:
                await page.goto(f"https://www.hermes.com/jp/ja/category/{path_jp}/#|", wait_until="load", timeout=90000)
                await asyncio.sleep(5)
                await robust_artisan_scroll(page)
                jp_elements = await page.query_selector_all(".product-item")
                for el in jp_elements:
                    d = await atomic_extract(el)
                    if d: jp_skus.add(d["sku"])
                print(f"    -> 日本在庫網を同期しました ({len(jp_skus)}件)")
            except:
                print(f"    [!] 日本サイト応答なし。このカテゴリを回避します。")
                continue

            # 2. 国別巡回 (FR -> HK -> US -> KR)
            for country_key in target_countries:
                print(f"\n  --- [{country_key}] 現場精査中 ---")
                target_path = CONFIG[country_key]["paths"].get(cat_name)
                if not target_path: continue
                
                try:
                    await page.goto(f"https://www.hermes.com/{CONFIG[country_key]['code']}/category/{target_path}/#|", wait_until="load", timeout=90000)
                    try:
                        await page.wait_for_selector(".product-item", timeout=15000)
                    except:
                        print(f"    [情報] この国には現在在庫がありません。")
                        continue

                    await robust_artisan_scroll(page)
                    
                    # 要素を捕捉
                    item_count = await page.locator(".product-item").count()
                    print(f"    -> {item_count}件を検知。一品ずつの完遂シーケンスを開始。")

                    for i in range(item_count):
                        # 【重要】毎回要素を再取得（Stale Element対策）
                        items = await page.query_selector_all(".product-item")
                        if i >= len(items): break
                        el = items[i]
                        
                        data = await atomic_extract(el)
                        if not data: continue
                        
                        sku_upper = str(data['sku']).upper().strip()
                        print(f"      ({i+1}/{item_count}) {data['name']} ({sku_upper})")
                        
                        # 照合1: 日本に既にあるか
                        if sku_upper in jp_skus:
                            print(f"        -> 回避: 日本で販売中")
                            continue
                        # 照合2: 過去の台帳に既にあるか
                        if sku_upper in existing_skus:
                            print(f"        -> 回避: 台帳記載済み")
                            continue
                        
                        # 計算
                        rate = EXCHANGE_RATES.get(country_key, 1.0)
                        try: jpy = int(float(data['price']) * rate)
                        except: jpy = 0
                        
                        row = [today_date, cat_name, country_key, sku_upper, data['name'], data['price'], f"¥{jpy:,}", data['url']]
                        
                        # 【一品完遂】記帳 ＆ 検品 ＆ 同期
                        print(f"        [同期] Master ＆ Today_Unreleased への刻印を実行中...")
                        if await secure_transaction_write(sheets, row, sheets["Today_Unreleased"]):
                            existing_skus.add(sku_upper)
                            print(f"        [完遂] 検品合格。台帳への物理反映を確認。")
                        else:
                            print(f"        [警告] この商品の記帳に失敗しました。次へ。")
                        
                        # ボット検知回避の「間」
                        await artisan_jitter_delay(5, 10)

                except Exception as e:
                    print(f"    [!] 国別巡回エラー: {e}。復旧中...")
                    await asyncio.sleep(20)
                    continue

            print(f"--- カテゴリ完了。APIクールダウン ---")
            await asyncio.sleep(45)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
