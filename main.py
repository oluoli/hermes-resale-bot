import requests
import pandas as pd
import time
import os

# ご提示いただいたカテゴリー設定
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

class HermesScraper:
    def __init__(self):
        self.base_url = "https://b-api.hermes.com/products"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
        }

    def fetch_category_products(self, country_code, category_path):
        """指定された国とカテゴリーの全商品をAPIから取得"""
        products = []
        offset = 0
        limit = 40  # APIの1回あたりの取得上限

        while True:
            params = {
                "region": country_code.split('/')[0],
                "lang": country_code.split('/')[1],
                "category": category_path,
                "offset": offset,
                "pagesize": limit,
                "sort": "relevance"
            }
            try:
                response = requests.get(self.base_url, headers=self.headers, params=params, timeout=10)
                if response.status_code != 200:
                    break
                
                data = response.json()
                items = data.get("products", [])
                if not items:
                    break
                
                for item in items:
                    products.append({
                        "sku": item.get("sku"),
                        "name": item.get("name"),
                        "price": item.get("price"),
                        "url": "https://www.hermes.com/" + country_code + "/product/" + item.get("url", ""),
                    })
                
                offset += limit
                time.sleep(1) # サーバー負荷軽減
            except Exception as e:
                print(f"Error fetching {country_code} {category_path}: {e}")
                break
        return products

def main():
    scraper = HermesScraper()
    
    # 1. 日本の在庫SKUリストを作成
    print("--- 日本の在庫状況を取得中 ---")
    jp_inventory_skus = set()
    for cat_name, path in CONFIG["JP"]["paths"].items():
        print(f"取得中: {cat_name}...")
        items = scraper.fetch_category_products(CONFIG["JP"]["code"], path)
        for it in items:
            jp_inventory_skus.add(it["sku"])
    
    # 2. 他国の在庫をチェック
    results = []
    target_countries = ["FR", "HK", "US", "KR"]

    for country in target_countries:
        print(f"--- {country} の在庫状況を比較中 ---")
        code = CONFIG[country]["code"]
        paths = CONFIG[country]["paths"]

        for cat_name, path in paths.items():
            print(f"比較中: {cat_name}...")
            foreign_items = scraper.fetch_category_products(code, path)
            
            for item in foreign_items:
                # 日本のSKUリストに含まれていないものを抽出
                if item["sku"] not in jp_inventory_skus:
                    item["国"] = country
                    item["カテゴリー"] = cat_name
                    results.append(item)

    # 3. スプレッドシート（Excel）へ出力
    if results:
        df = pd.DataFrame(results)
        # 列の並び替え
        df = df[["国", "カテゴリー", "sku", "name", "price", "url"]]
        df.columns = ["対象国", "カテゴリー", "商品ID(SKU)", "商品名", "現地価格", "商品URL"]
        
        output_file = "hermes_not_in_jp.xlsx"
        df.to_excel(output_file, index=False)
        print(f"\n完了！ ファイルを保存しました: {output_file}")
    else:
        print("\n日本未販売の商品は見つかりませんでした。")

if __name__ == "__main__":
    main()
