import asyncio
import os
import json
import gspread
from playwright.async_api import async_playwright
# インポート方法を一番シンプルな形に戻します
import playwright_stealth
from oauth2client.service_account import ServiceAccountCredentials

# 競合が少ないジャンル
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
        # タイムアウト（待ち時間）を少し長めの60秒に設定
        await page.goto(url, wait_until="networkidle", timeout=60000)
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(5)
        
        items = await page.query_selector_all(".product-item")
        for item in items:
            name_el = await item.query_selector(".product-item-name")
            link_el = await item.query_selector("a")
            if name_el and link_el:
                name = (await name_el.inner_text()).strip()
                link = await link_el.get_attribute("href")
                # URLから品番を抜き出す
                sku = link.split('/')[-1].replace('.html', '')
                products[sku] = {"name": name, "url": f"https://www.hermes.com{link}"}
    except Exception as e:
        print(f"エラー発生 ({country_path}): {e}")
    return products

async def run():
    # Googleスプレッドシート認証
    creds_json = json.loads(os.environ["GOOGLE_CREDENTIALS"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive'])
    client = gspread.authorize(creds)
    
    # スプレッドシート名を確認してください
    sheet = client.open("Hermes_Check_List").sheet1
    
    sheet.clear()
    sheet.append_row(["ジャンル", "国", "品番", "商品名", "URL"])

    async with async_playwright() as p:
        # ブラウザを起動
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # 修正ポイント：関数名を stealth に変更
        # もしこれでもダメなら自動的にスキップして進むようにしています
        try:
            await playwright_stealth.stealth(page)
        except:
            print("Stealth設定をスキップしました")

        for cat, path in CATEGORIES.items():
            print(f"調査中: {cat}")
            jp_list = await scrape_hermes(page, "jp/ja", path)
            
            for country in ["fr/fr", "hk/en", "us/en"]:
                overseas_list = await scrape_hermes(page, country, path)
                for sku, data in overseas_list.items():
                    if sku not in jp_list:
                        sheet.append_row([cat, country[:2].upper(), sku, data['name'], data['url']])
                        print(f"日本未入荷を発見: {data['name']}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
