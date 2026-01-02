import asyncio
import os
import json
import gspread
import re
from playwright.async_api import async_playwright
import playwright_stealth
from oauth2client.service_account import ServiceAccountCredentials

# 国ごとに異なるカテゴリーパスを設定（ここが重要です！）
# 1人運営の効率化のため、需要の高い「日本未入荷」が出やすいジャンルを厳選しています。
CONFIG = {
    "JP": {"code": "jp/ja", "paths": {
        "Jewelry": "jewelry/gold-jewelry",
        "Blankets": "home/blankets-and-pillows",
        "Baby": "baby",
        "Pets": "home/equestrian-and-dog",
        "PetitH": "petit-h/all-petit-h", # 日本にはほぼない
        "Bags": "bags-and-small-leather-goods/bags-and-clutches"
    }},
    "FR": {"code": "fr/fr", "paths": {
        "Jewelry": "bijouterie/bijoux-en-or",
        "Blankets": "maison/couvertures-et-oreillers",
        "Baby": "bebe",
        "Pets": "maison/equitation-et-chien",
        "PetitH": "petit-h",
        "Bags": "sacs-et-petite-maroquinerie/sacs-et-pochettes"
    }},
    "HK": {"code": "hk/en", "paths": {
        "Jewelry": "jewelry/gold-jewelry",
        "Blankets": "home/blankets-and-pillows",
        "Baby": "baby",
        "Pets": "home/equestrian-and-dog",
        "PetitH": "petit-h",
        "Bags": "bags-and-small-leather-goods/bags-and-clutches"
    }},
    "US": {"code": "us/en", "paths": {
        "Jewelry": "jewelry/gold-jewelry",
        "Blankets": "home/blankets-and-pillows",
        "Baby": "baby",
        "Pets": "home/equestrian-and-dog",
        "PetitH": "petit-h",
        "Bags": "bags-and-small-leather-goods/bags-and-clutches"
    }}
}

async def scrape_hermes(page, country_code, category_path):
    url = f"https://www.hermes.com/{country_code}/category/{category_path}/#|"
    products = {}
    try:
        await page.goto(url, wait_until="load", timeout=90000)
        await asyncio.sleep(5)
        
        # 確実に全商品を表示させるためのスクロール
        for _ in range(3):
            await page.mouse.wheel(0, 2000)
            await asyncio.sleep(2)

        items = await page.query_selector_all(".product-item")
        print(f"   [{country_code}] {len(items)}個の商品を検知")

        for item in items:
            name_el = await item.query_selector(".product-item-name")
            link_el = await item.query_selector("a")
            if name_el and link_el:
                name = (await name_el.inner_text()).strip()
                link = await link_el.get_attribute("href")
                sku_match = re.search(r'H[A-Z0-9]{5,}', link)
                sku = sku_match.group(0) if sku_match else name
                products[sku] = {"name": name, "url": f"https://www.hermes.com{link}"}
    except Exception as e:
        print(f"   × エラー ({country_code}): {e}")
    return products

async def run():
    creds_json = json.loads(os.environ["GOOGLE_CREDENTIALS"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive'])
    client = gspread.authorize(creds)
    sheet = client.open("Hermes_Check_List").sheet1
    
    sheet.clear()
    sheet.append_row(["ジャンル", "国", "品番", "商品名", "URL"])

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        page = await context.new_page()
        try: await playwright_stealth.stealth_async(page)
        except: pass

        # ジャンルごとに調査
        for cat_name in CONFIG["JP"]["paths"].keys():
            print(f"\n【カテゴリー調査中】: {cat_name}")
            
            # 1. 日本の在庫を確認
            jp_inventory = await scrape_hermes(page, CONFIG["JP"]["code"], CONFIG["JP"]["paths"][cat_name])
            
            # 2. 海外各国の在庫と比較
            for country_key in ["FR", "HK", "US"]:
                print(f" -> {country_key} をチェック中...")
                overseas_inventory = await scrape_hermes(page, CONFIG[country_key]["code"], CONFIG[country_key]["paths"][cat_name])
                
                new_items = []
                for sku, data in overseas_inventory.items():
                    if sku not in jp_inventory:
                        new_items.append([cat_name, country_key, sku, data['name'], data['url']])
                
                if new_items:
                    sheet.append_rows(new_items)
                    print(f"    ☆ {len(new_items)}件の日本未入荷品を保存しました")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
