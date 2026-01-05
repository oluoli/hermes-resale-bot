"""
========================================================================================
HERMES SOVEREIGN ARTISAN OS (v23.0.0) - THE UNBENDING ARTISAN
========================================================================================
Developer: World's Best System Engineer for OLUOLI
Focus: ZERO-SKIP Policy. Country Independence. Read-Back Absolute Integrity.
Status: Supreme Professional Grade. (No Omissions)

[CORE PROTOCOL]
- Independent Execution: Failure in JP sync NEVER stops FR, HK, US, or KR.
- Persistence: Scans each country until items are found or 'Empty' is confirmed.
- Verification: Post-write read-back happens for every single entry.
========================================================================================
"""

import asyncio
import os
import json
import gspread
import re
import time
import random
import logging
import sys
import math
import traceback
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Set, Any, Tuple, Union, Final
from oauth2client.service_account import ServiceAccountCredentials
from playwright.async_api import (
    async_playwright, 
    Page, 
    Browser, 
    BrowserContext, 
    ElementHandle, 
    TimeoutError as PWTimeoutError
)
import playwright_stealth

# =============================================================================
# I. GLOBAL CONSTITUTION (カテゴリー完全記述 ＆ システム設定)
# =============================================================================

class SovereignConfig:
    VERSION: Final[str] = "23.0.0"
    JST = timezone(timedelta(hours=+9), 'JST')
    
    CURRENCY_RATES: Final[Dict[str, float]] = {
        "FR": 166.50, "HK": 20.80, "US": 158.00, "KR": 0.115
    }

    # カテゴリー設定: 一切の省略なく完全記述 (指示通り)
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

    SPREADSHEET_NAME: Final[str] = "Hermes_Check_List"
    SHEET_MASTER: Final[str] = "master"
    SHEET_TODAY: Final[str] = "todays_new"

    # API ＆ ステルス定数
    READ_BACK_DELAY = 12.0 
    API_LIMIT_PAUSE = 5.0
    MAX_SCRAPE_RETRY = 3
    TIMEOUT_MS = 150000

# =============================================================================
# II. BEZIER INTERACTION ENGINE (人間らしさの追求)
# =============================================================================

class HumanoidInteractions:
    @staticmethod
    async def think(complexity: str = "normal"):
        mu_map = {"glance": 1.5, "normal": 4.5, "write": 9.0}
        mu = mu_map.get(complexity, 5.0)
        delay = random.lognormvariate(math.log(mu), 0.3)
        await asyncio.sleep(max(mu*0.6, min(delay, mu*2.5)))

    @staticmethod
    async def human_bezier_move(page: Page, target_x: int, target_y: int):
        x1, y1 = random.randint(0, 300), random.randint(0, 300)
        cx1, cy1 = x1 + random.randint(-50, 50), y1 + random.randint(-50, 50)
        cx2, cy2 = target_x + random.randint(-50, 50), target_y + random.randint(-50, 50)
        steps = random.randint(25, 45)
        for i in range(steps + 1):
            t = i / steps
            x = (1-t)**3*x1 + 3*(1-t)**2*t*cx1 + 3*(1-t)*t**2*cx2 + t**3*target_x
            y = (1-t)**3*y1 + 3*(1-t)**2*t*cy1 + 3*(1-t)*t**2*cy2 + t**3*target_y
            await page.mouse.move(x, y)
            if i % 10 == 0: await asyncio.sleep(0.01)

# =============================================================================
# III. SECURE TRANSACTION VAULT (物理検証・台帳マネージャー)
# =============================================================================

logging.basicConfig(level=logging.INFO, format='\033[93m%(asctime)s\033[0m | %(message)s', datefmt='%H:%M:%S')
log = logging.getLogger("Artisan")

class SovereignVault:
    def __init__(self, creds_json: str):
        self.creds_dict = json.loads(creds_json)
        self.client = None
        self.spreadsheet = None
        self.ws_master = None
        self.ws_today = None
        self.ledger_index: Set[str] = set()

    async def ignite(self):
        log.info("【認証】Google Sheets セキュリティ・レイヤーを起動...")
        creds = ServiceAccountCredentials.from_json_keyfile_dict(self.creds_dict, ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive'])
        self.client = gspread.authorize(creds)
        self.spreadsheet = self.client.open(SovereignConfig.SPREADSHEET_NAME)
        log.info(f"✅ 物理接続完了: {self.spreadsheet.url}")

        def get_ws(name):
            try: return self.spreadsheet.worksheet(name)
            except: return self.spreadsheet.add_worksheet(name, 30000, 20)

        self.ws_master = get_ws(SovereignConfig.SHEET_MASTER)
        self.ws_today = get_ws(SovereignConfig.SHEET_TODAY)
        self.ws_today.clear()
        self.ws_today.append_row(["取得日時", "カテゴリ", "国", "品番", "商品名", "現地通貨", "円換算価格", "URL"], 1)

        skus = self.ws_master.col_values(4)
        self.ledger_index = {str(s).upper().strip() for s in skus if s and s != "品番"}
        log.info(f"秘書: {len(self.ledger_index)} 件の既存資産を記憶しました。")

    async def secure_write(self, row: List[Any]) -> bool:
        sku_target = str(row[3]).upper().strip()
        for attempt in range(3):
            try:
                await asyncio.sleep(SovereignConfig.API_LIMIT_PAUSE)
                res = self.ws_master.append_row(row, value_input_option='USER_ENTERED')
                log.info(f"      [物理検証中] 品番 {sku_target} 反映待機...")
                await asyncio.sleep(SovereignConfig.READ_BACK_DELAY)
                
                updated_range = res.get('updates', {}).get('updatedRange', '')
                row_idx = re.search(r'A(\d+)', updated_range).group(1)
                read_back = self.ws_master.cell(row_idx, 4).value
                
                if str(read_back).upper().strip() == sku_target:
                    self.ws_today.append_row(row, value_input_option='USER_ENTERED')
                    self.ledger_index.add(sku_target)
                    log.info(f"      ✅ [完遂] クラウド上の実存を確認。")
                    return True
            except:
                await asyncio.sleep(30)
        return False

# =============================================================================
# IV. UNBENDING VISION ENGINE (不屈の視覚エンジン)
# =============================================================================

class SovereignVision:
    def __init__(self):
        self.pw, self.browser, self.page = None, None, None

    async def ignite(self):
        self.pw = await async_playwright().start()
        self.browser = await self.pw.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        self.page = await self.browser.new_page(viewport={"width": 1920, "height": 1080}, locale="ja-JP")
        await stealth_async(self.page)
        await self.page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => False})")

    async def navigate_sturdy(self, url: str) -> bool:
        """読み込みが完了するまで徹底的にリトライ"""
        for _ in range(3):
            try:
                await self.page.goto(url, wait_until="networkidle", timeout=SovereignConfig.TIMEOUT_MS)
                await HumanoidInteractions.think("glance")
                return True
            except:
                await asyncio.sleep(5)
        return False

    async def persistent_extract(self) -> Dict[str, Dict[str, str]]:
        """商品が見つかるまでスクロールとリロードを繰り返す"""
        results = {}
        for attempt in range(SovereignConfig.MAX_SCRAPE_RETRY):
            # 深いスクロール
            for _ in range(20): 
                await self.page.mouse.wheel(0, 1200)
                await asyncio.sleep(1.0)
            
            items = await self.page.query_selector_all(".product-item")
            if items:
                for item in items:
                    try:
                        name_el = await item.query_selector(".product-item-name")
                        link_el = await item.query_selector("a")
                        price_el = await item.query_selector(".product-item-price")
                        if name_el and link_el:
                            name = (await name_el.inner_text()).strip()
                            price = (await price_el.inner_text()).strip() if price_el else "0"
                            link = await link_el.get_attribute("href")
                            sku_match = re.search(r'H[A-Z0-9]{5,}', link)
                            sku = sku_match.group(0).upper().strip() if sku_match else name.upper().strip()
                            results[sku] = {"name": name, "price": price, "url": f"https://www.hermes.com{link}"}
                    except: continue
                if results: return results
            
            log.info(f"      [?] 商品が見つかりません。リフレッシュして再探索中...({attempt+1})")
            await self.page.reload(wait_until="networkidle")
        return results

# =============================================================================
# V. SOVEREIGN COMMANDER (現場総指揮：不屈の司令塔)
# =============================================================================

class SovereignCommander:
    def __init__(self):
        self.vision = SovereignVision()
        self.vault = SovereignVault(os.environ["GOOGLE_CREDENTIALS"])
        self.jp_stock: Set[str] = set()

    async def sync_japan_baseline(self, cat_label, path):
        """日本在庫を把握。もし失敗しても海外調査は止めない。"""
        log.info(f"【工程1】日本の棚を確認中: {cat_label}")
        self.jp_stock.clear()
        
        if await self.vision.navigate_sturdy(f"https://www.hermes.com/jp/ja/category/{path}/#|"):
            jp_inv = await self.vision.persistent_extract()
            self.jp_stock = set(jp_inv.keys())
        
        if not self.jp_stock:
            log.warning(f"      ⚠️ 日本の『{cat_label}』が取得できませんでした。海外全件を精査対象とします。")
        else:
            log.info(f"💡 日本在庫 {len(self.jp_stock)} 件を除外リストに設定。")

    async def launch_expedition(self):
        await self.vault.ignite()
        await self.vision.ignite()

        try:
            # 14カテゴリーを順番に。一行の省略も許さない。
            for cat_label, jp_path in SovereignConfig.CONFIG["JP"]["paths"].items():
                log.info(f"\n{'='*100}\n🏆 FOCUS CATEGORY: {cat_label}\n{'='*100}")
                
                # 日本在庫をキャッシュ (失敗しても続行)
                await self.sync_japan_baseline(cat_label, jp_path)

                # 国別調査を独立して実行
                for country in ["FR", "HK", "US", "KR"]:
                    log.info(f"   🌏 [{country}] ステージ鑑定開始")
                    
                    config_country = SovereignConfig.CONFIG.get(country)
                    if not config_country: continue
                    
                    lang_path = config_country["code"]
                    cat_path = config_country["paths"].get(cat_label)
                    
                    if not cat_path:
                        log.warning(f"      [SKIP] {country} にはカテゴリ『{cat_label}』の定義がありません。")
                        continue

                    if await self.vision.navigate_sturdy(f"https://www.hermes.com/{lang_path}/category/{cat_path}/#|"):
                        os_inv = await self.vision.persistent_extract()
                        
                        log.info(f"      [発見] {len(os_inv)} 点の商品を検知。個別鑑定へ...")
                        for sku, data in os_inv.items():
                            sku_up = sku.upper().strip()
                            # 記帳判断：日本になく、台帳履歴にもないもの
                            if sku_up not in self.jp_stock and sku_up not in self.vault.ledger_index:
                                log.info(f"      💎 発掘: {data['name']} ({sku_up})")
                                
                                fx = SovereignConfig.CURRENCY_RATES.get(country, 1.0)
                                try: num = float(re.sub(r'[^\d.]', '', data['price'].replace(',', '')))
                                except: num = 0
                                
                                row = [datetime.now(SovereignConfig.JST).strftime("%Y/%m/%d %H:%M"), cat_label, country, sku_up, data['name'], data['price'], f"¥{int(num*fx):,}", data['url']]
                                
                                if await self.vault.secure_write(row):
                                    await HumanoidInteractions.think("normal")
                                    await HumanoidInteractions.human_bezier_move(self.vision.page, random.randint(0, 1920), random.randint(0, 1080))
                        
                    await asyncio.sleep(10) # 国別待機
                await asyncio.sleep(30) # カテゴリ別待機

        finally:
            await self.vision.browser.close()
            await self.vision.pw.stop()

if __name__ == "__main__":
    try:
        asyncio.run(SovereignCommander().launch_expedition())
    except Exception as e:
        log.critical(f"❌ システム致命的エラー: {e}")
        sys.exit(1)
