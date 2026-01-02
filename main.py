import asyncio
import os
import json
import gspread
import re
from playwright.async_api import async_playwright
import playwright_stealth
from oauth2client.service_account import ServiceAccountCredentials

# カテゴリー設定
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
        # 人間が操作しているように見せるための待機
        await page.goto(url, wait_until="load", timeout=90000)
        await asyncio.sleep(5)
        
        # 画面を少しずつスクロールして商品を読み込ませる
        for _ in range(3):
            await page.mouse.wheel(0, 2000)
            await asyncio.sleep(2)

        items = await page.query_selector_all(".product-item")
        print(f"--- {country_path} で {len(items)} 個の商品を発見 ---")

        for item in items:
            name_el = await item.query_selector(".product-item-name")
            link_el = await item.query_selector("a")
            if name_el and link_el:
                name = (await name_el.inner_text()).strip()
                link = await link_el.get_attribute("href")
                
                # 品番（Hで始まる英数字）を抽出するより確実な方法
                sku_match = re.search(r'H[A-Z0-9]{5,}', link)
                sku = sku_match.group(0) if sku_match else name
                
                products[sku] = {"name": name, "url": f"https://www.hermes.com{link}"}
    except Exception as e:
        print(f"エラー発生 ({country_path}): {e}")
    return products

async def run():
    # Google認証
    creds_json = json.loads(os.environ["GOOGLE_CREDENTIALS"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive'])
    client = gspread.authorize(creds)
    sheet = client.open("Hermes_Check_List").sheet1
    
    sheet.clear()
    sheet.append_row(["ジャンル", "国", "品番", "商品名", "URL"])

    async with async_playwright() as p:
        # ユーザーエージェント（ブラウザの種類）を普通のパソコンに見せかける
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        try:
            await playwright_stealth.stealth_async(page)
        except:
            print("Stealthスキップ")

        for cat, path in CATEGORIES.items():
            print(f"\n【調査開始】ジャンル: {cat}")
            jp_list = await scrape_hermes(page, "jp/ja", path)
            
            for country_code in ["fr/fr", "hk/en", "us/en"]:
                overseas_list = await scrape_hermes(page, country_code, path)
                diff_count = 0
                for sku, data in overseas_list.items():
                    if sku not in jp_list:
                        sheet.append_row([cat, country_code[:2].upper(), sku, data['name'], data['url']])
                        diff_count += 1
                print(f" -> {country_code.upper()}: 日本未入荷を {diff_count} 件保存しました")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
