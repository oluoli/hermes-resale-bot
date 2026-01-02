import asyncio
import os
import json
import gspread
from playwright.async_api import async_playwright
# ここを修正：stealth_async ではなく stealth にしました
from playwright_stealth import stealth
from oauth2client.service_account import ServiceAccountCredentials

# 競合が少ないジャンルを狙い撃ち
CATEGORIES = {
    "Blankets": "home/blankets-and-pillows",
    "Baby": "baby",
    "Pets": "home/equestrian-and-dog",
    "Women_Jewelry": "jewelry/gold-jewelry",
    "Men_Accessories": "men/accessories"
}

async def scrape_hermes(page, country_path, category_path):
    url = f"https://www.hermes.com/{country_path}/category/{category_path}/#|"
    products = {}
    try:
        await page.goto(url, wait_until="networkidle")
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(4)
        
        items = await page.query_selector_all(".product-item")
        for item in items:
            name_el = await item.query_selector(".product-item-name")
            link_el = await item.query_selector("a")
            if name_el and link_el:
                name = (await name_el.inner_text()).strip()
                link = await link_el.get_attribute("href")
                sku = link.split('/')[-1].replace('.html', '')
                products[sku] = {"name": name, "url": f"https://www.hermes.com{link}"}
    except:
        pass
    return products

async def run():
    # Googleスプレッドシートにログイン
    creds_json = json.loads(os.environ["GOOGLE_CREDENTIALS"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive'])
    client = gspread.authorize(creds)
    sheet = client.open("Hermes_Check_List").sheet1
    
    sheet.clear()
    sheet.append_row(["ジャンル", "国", "品番", "商品名", "URL"])

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        # ここも修正：await stealth(page) に変更しました
        await stealth(page)

        for cat, path in CATEGORIES.items():
            print(f"調査中: {cat}")
            jp_list = await scrape_hermes(page, "jp/ja", path)
            
            for country in ["fr/fr", "hk/en", "us/en"]:
                overseas_list = await scrape_hermes(page, country, path)
                for sku, data in overseas_list.items():
                    if sku not in jp_list:
                        sheet.append_row([cat, country[:2].upper(), sku, data['name'], data['url']])
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
