import asyncio
import os
import json
import gspread
import re
import requests
from playwright.async_api import async_playwright
import playwright_stealth
from oauth2client.service_account import ServiceAccountCredentials

# --- 設定：為替レート（適宜更新してください） ---
EXCHANGE_RATES = {
    "FR": 165.0,  # EUR/JPY
    "HK": 20.0,   # HKD/JPY
    "US": 155.0,  # USD/JPY
    "KR": 0.11    # KRW/JPY
}

# カテゴリーパス設定（ユーザー様の調整済み版を反映）
CONFIG = {
    "JP": {"code": "jp/ja", "paths": {
        "Jewelry": "jewelry/gold-jewelry",
        "Blankets": "home/textiles",
        "Baby": "gifts-and-petit-h/baby-gifts",
        "Pets": "home-outdoor-and-equestrian/equestrian-and-dogs/dog",
        "PetitH": "petit-h/all-petit-h",
        "Bags": "women/bags-and-small-leather-goods/bags-and-clutches",
        "Men_bag": "men/bags-and-small-leather-goods/bags",
        "Tableware": "home/tableware"
    }},
    "FR": {"code": "fr/fr", "paths": {
        "Jewelry": "bijouterie/bijoux-en-or",
        "Blankets": "maison/textiles",
        "Baby": "cadeaux-et-petit-h/cadeaux-de-naissance",
        "Pets": "maison-plein-air-et-equitation/equitation-et-chien/chien",
        "PetitH": "petit-h",
        "Bags": "femme/sacs-et-petite-maroquinerie/sacs-et-pochettes",
        "Men_bag": "homme/sacs-et-petite-maroquinerie/sacs",
        "Tableware": "maison/art-de-la-table"
    }},
    "HK": {"code": "hk/en", "paths": {
        "Jewelry": "jewelry/gold-jewelry",
        "Blankets": "home/textiles",
        "Baby": "gifts-and-petit-h/baby-gifts",
        "Pets": "home-outdoor-and-equestrian/equestrian-and-dogs/dog",
        "PetitH": "petit-h",
        "Bags": "women/bags-and-small-leather-goods/bags-and-clutches",
        "Men_bag": "men/bags-and-small-leather-goods/bags",
        "Tableware": "home/tableware"
    }},
    "US": {"code": "us/en", "paths": {
        "Jewelry": "jewelry/gold-jewelry",
        "Blankets": "home/textiles",
        "Baby": "gifts-and-petit-h/baby-gifts",
        "Pets": "home-outdoor-and-equestrian/equestrian-and-dogs/dog",
        "PetitH": "petit-h",
        "Bags": "women/bags-and-small-leather-goods/bags-and-clutches",
        "Men_bag": "men/bags-and-small-leather-goods/bags",
        "Tableware": "home/tableware"
    }},
    "KR": {"code": "kr/ko", "paths": { # KRのコードをkr/koに修正
        "Jewelry": "jewelry/gold-jewelry",
        "Blankets": "home/textiles",
        "Baby": "gifts-and-petit-h/baby-gifts",
        "Pets": "home-outdoor-and-equestrian/equestrian-and-dogs/dog",
        "PetitH": "petit-h",
        "Bags": "women/bags-and-small-leather-goods/bags-and-clutches",
        "Men_bag": "men/bags-and-small-leather-goods/bags",
        "Tableware": "home/tableware"
    }}
}

def send_line_notify(message):
    line_token = os.environ.get("LINE_NOTIFY_TOKEN")
    if not line_token:
        return
    endpoint = "https://notify-api.line.me/api/notify"
    headers = {"Authorization": f"Bearer {line_token}"}
    requests.post(endpoint, headers=headers, data={"message": message})

def convert_price_to_jpy(price_str, country_key):
    try:
        # 数字とドット以外を削除
        num_str = re.sub(r'[^\d.]', '', price_str.replace(',', ''))
        price_num = float(num_str)
        rate = EXCHANGE_RATES.get(country_key, 1.0)
        return int(price_num * rate)
    except:
        return 0

async def scrape_hermes(page, country_code, category_path):
    url = f"https://www.hermes.com/{country_code}/category/{category_path}/#|"
    products = {}
    try:
        await page.goto(url, wait_until="networkidle", timeout=120000)
        await asyncio.sleep(5)
        for _ in range(5):
            await page.mouse.wheel(0, 1500)
            await asyncio.sleep(2)

        items = await page.query_selector_all(".product-item")
        for item in items:
            name_el = await item.query_selector(".product-item-name")
            price_el = await item.query_selector(".product-item-price") # 価格要素取得追加
            link_el = await item.query_selector("a")
            if name_el and link_el:
                name = (await name_el.inner_text()).strip()
                price_text = (await price_el.inner_text()).strip() if price_el else "0"
                link = await link_el.get_attribute("href")
                sku_match = re.search(r'H[A-Z0-9]{5,}', link)
                sku = sku_match.group(0) if sku_match else name
                products[sku] = {"name": name, "price": price_text, "url": f"https://www.hermes.com{link}"}
    except Exception as e:
        print(f"   × エラー ({country_code} / {category_path}): {e}")
    return products

async def run():
    creds_json = json.loads(os.environ["GOOGLE_CREDENTIALS"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive'])
    client = gspread.authorize(creds)
    sheet = client.open("Hermes_Check_List").sheet1
    
    # --- 新機能：既存の品番(SKU)を取得 ---
    all_data = sheet.get_all_values()
    if not all_data:
        sheet.append_row(["ジャンル", "国", "品番", "商品名", "現地価格", "日本円目安", "URL"])
        existing_skus = set()
    else:
        # 3列目(インデックス2)が品番
        existing_skus = {row[2] for row in all_data}

    new_items_to_notify = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = await context.new_page()
        try: await playwright_stealth.stealth_async(page)
        except: pass

        for cat_name in CONFIG["JP"]["paths"].keys():
            print(f"\n【調査中】: {cat_name}")
            jp_inventory = await scrape_hermes(page, CONFIG["JP"]["code"], CONFIG["JP"]["paths"][cat_name])
            
            for country_key in ["FR", "HK", "US", "KR"]:
                print(f" -> {country_key} をスキャン...")
                path = CONFIG[country_key]["paths"].get(cat_name)
                if not path: continue
                
                overseas_inventory = await scrape_hermes(page, CONFIG[country_key]["code"], path)
                
                rows_to_append = []
                for sku, data in overseas_inventory.items():
                    # 日本になく、かつシートにまだ登録されていないもの
                    if sku not in jp_inventory and sku not in existing_skus:
                        jpy_price = convert_price_to_jpy(data['price'], country_key)
                        row = [cat_name, country_key, sku, data['name'], data['price'], f"¥{jpy_price:,}", data['url']]
                        rows_to_append.append(row)
                        new_items_to_notify.append(f"【{cat_name}】{data['name']} ({country_key}) ¥{jpy_price:,}")
                        existing_skus.add(sku) # 同じ実行内での重複回避
                
                if rows_to_append:
                    sheet.append_rows(rows_to_append)
                    print(f"    ☆ {len(rows_to_append)}件の新規アイテムを追加")
                
                await asyncio.sleep(5)
            await asyncio.sleep(8)
        
        await browser.close()

    # --- 新機能：LINE通知 ---
    if new_items_to_notify:
        msg = "\n🌟エルメス新着未入荷情報🌟\n" + "\n".join(new_items_to_notify[:15]) # 通知が長すぎないよう制限
        if len(new_items_to_notify) > 15:
            msg += f"\n他 {len(new_items_to_notify)-15} 件の新着あり"
        send_line_notify(msg)

if __name__ == "__main__":
    asyncio.run(run())
