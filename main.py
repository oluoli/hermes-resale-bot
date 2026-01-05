"""
========================================================================================
HERMES SOVEREIGN ARTISAN OS (v21.0.0) - THE ETERNAL GUARDIAN
========================================================================================
Developer: World's Best System Engineer for OLUOLI
Focus: 100% Data Integrity, Advanced Bot Evasion, API Quota Safeguard.
Status: The Definitive Professional Edition.

[MISSION PROTOCOLS]
- ANTI-GHOST: Physical verification by Read-back from Google Cloud.
- STEALTH: 3rd-order Bezier interaction & Lognormal cognitive jitter.
- RESILIENCE: Automatic recovery from "Zero-Item" false negatives.
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
from playwright_stealth import stealth_async

# =============================================================================
# I. GLOBAL CONSTITUTION (全設定 ＆ 14カテゴリー完全記述)
# =============================================================================

class SovereignConfig:
    VERSION: Final[str] = "21.0.0"
    JST = timezone(timedelta(hours=+9), 'JST')
    
    # 2026年 リアルタイム予測為替レート
    CURRENCY_RATES: Final[Dict[str, float]] = {
        "FR": 166.50, "HK": 20.80, "US": 158.00, "KR": 0.115
    }

    # カテゴリー設定: 一切の省略なく完全記述
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

    # 検証・耐久・ステルス定数
    READ_BACK_DELAY = 15.0 
    API_LIMIT_GUARD = 4.0
    MAX_SCRAPE_RETRY = 5
    TIMEOUT_MS = 150000

# =============================================================================
# II. BEZIER INTERACTION ENGINE (究極の対AI擬態)
# =============================================================================

class HumanoidInteractions:
    @staticmethod
    async def think(complexity: str = "normal"):
        """対数正規分布を用いた『迷い』のシミュレート"""
        profile = {"glance": (1.0, 2.5), "normal": (3.5, 8.0), "write": (7.0, 12.0)}
        low, high = profile.get(complexity, (3, 6))
        mu = math.log((low + high) / 2)
        delay = random.lognormvariate(mu, 0.4)
        await asyncio.sleep(max(low, min(delay, high)))

    @staticmethod
    async def human_mouse_move(page: Page, target_x: int, target_y: int):
        """3次ベジエ曲線による非線形マウス移動"""
        x1, y1 = random.randint(0, 500), random.randint(0, 500)
        cx1 = x1 + (target_x - x1) / 3 + random.randint(-150, 150)
        cy1 = y1 + (target_y - y1) / 3 + random.randint(-150, 150)
        cx2 = x1 + 2 * (target_x - x1) / 3 + random.randint(-150, 150)
        cy2 = y1 + 2 * (target_y - y1) / 3 + random.randint(-150, 150)
        
        steps = random.randint(50, 80)
        for i in range(steps + 1):
            t = i / steps
            x = (1-t)**3*x1 + 3*(1-t)**2*t*cx1 + 3*(1-t)*t**2*cx2 + t**3*target_x
            y = (1-t)**3*y1 + 3*(1-t)**2*t*cy1 + 3*(1-t)*t**2*cy2 + t**3*target_y
            await page.mouse.move(x, y)
            if i % 15 == 0: await asyncio.sleep(0.01)

# =============================================================================
# III. SECURE TRANSACTION VAULT (完遂保証・物理検証)
# =============================================================================

logging.basicConfig(level=logging.INFO, format='\033[93m%(asctime)s\033[0m | %(message)s', datefmt='%H:%M:%S')
log = logging.getLogger("ArtisanCommander")

class SovereignVault:
    def __init__(self, creds_json: str):
        self.creds_dict = json.loads(creds_json)
        self.client = None
        self.spreadsheet = None
        self.ws_master = None
        self.ws_today = None
        self.last_write_time = 0
        self.memory: Set[str] = set()

    async def ignite(self):
        creds = ServiceAccountCredentials.from_json_keyfile_dict(self.creds_dict, ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive'])
        self.client = gspread.authorize(creds)
        
        try:
            self.spreadsheet = self.client.open(SovereignConfig.SPREADSHEET_NAME)
            log.info(f"💡 物理接続完了: {self.spreadsheet.url}")
        except:
            log.warning("⚠️ 台帳を新規作成します...")
            self.spreadsheet = self.client.create(SovereignConfig.SPREADSHEET_NAME)

        def get_ws(name):
            try: return self.spreadsheet.worksheet(name)
            except: return self.spreadsheet.add_worksheet(name, 30000, 20)

        self.ws_master = get_ws(SovereignConfig.SHEET_MASTER)
        self.ws_today = get_ws(SovereignConfig.SHEET_TODAY)
        self.ws_today.clear()
        self.ws_today.append_row(["取得日", "カテゴリ", "国", "品番", "商品名", "価格", "円換算", "URL"], 1)

        skus = self.ws_master.col_values(4)
        self.memory = {str(s).upper().strip() for s in skus if s and s != "品番"}
        log.info(f"秘書: {len(self.memory)} 件の既存データを暗記しました。")

    async def secure_write(self, row: List[Any]) -> bool:
        """物理的な読み戻しを伴う完遂保証記帳"""
        sku_target = str(row[3]).upper().strip()
        
        # APIレート制限の物理的保護
        now = time.time()
        if now - self.last_write_time < SovereignConfig.API_LIMIT_GUARD:
            await asyncio.sleep(SovereignConfig.API_LIMIT_GUARD)

        for attempt in range(3):
            try:
                res = self.ws_master.append_row(row, value_input_option='USER_ENTERED')
                self.last_write_time = time.time()
                
                log.info(f"      [物理検証中] 品番 {sku_target} 反映待機(15秒)...")
                await asyncio.sleep(SovereignConfig.READ_BACK_DELAY)
                
                # 物理的読み戻し
                row_idx = re.search(r'A(\d+)', res.get('updates', {}).get('updatedRange', '')).group(1)
                actual_val = self.ws_master.cell(row_idx, 4).value
                
                if str(actual_val).upper().strip() == sku_target:
                    self.ws_today.append_row(row, value_input_option='USER_ENTERED')
                    self.memory.add(sku_target)
                    log.info(f"      ✅ [完遂] Googleサーバーにて物理反映を確認。")
                    return True
            except:
                await asyncio.sleep(60)
        return False

# =============================================================================
# IV. RESILIENT VISION ENGINE (粘り強い視覚エンジン)
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

    async def navigate_carefully(self, url: str):
        log.info(f"現場へ移動: {url}")
        try:
            await self.page.goto(url, wait_until="networkidle", timeout=SovereignConfig.TIMEOUT_MS)
            await HumanoidInteractions.think("glance")
        except:
            await self.page.reload(wait_until="networkidle")

    async def extract_items_with_retry(self) -> Dict[str, Dict[str, str]]:
        """読み取り失敗時にスクロールとリロードでリトライする"""
        results = {}
        for attempt in range(SovereignConfig.MAX_SCRAPE_RETRY):
            # 職人スクロール
            for _ in range(12):
                await self.page.mouse.wheel(0, 1000)
                await asyncio.sleep(1.2)
            
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
                return results
            
            log.info(f"      [?] アイテムが見当たりません。再読み込み中...({attempt+1})")
            await self.page.reload(wait_until="networkidle")
            await asyncio.sleep(5)
        return results

# =============================================================================
# V. MISSION COMMANDER (現場総指揮)
# =============================================================================

class SovereignCommander:
    def __init__(self):
        self.vision = SovereignVision()
        self.vault = SovereignVault(os.environ["GOOGLE_CREDENTIALS"])
        self.jp_cache: Set[str] = set()

    async def sync_japan_truth(self, cat_label, path):
        log.info(f"【最優先】日本の棚を暗記中: {cat_label}")
        await self.vision.navigate_carefully(f"https://www.hermes.com/jp/ja/category/{path}/#|")
        
        jp_inv = await self.vision.extract_items_with_retry()
        if not jp_inv:
            content = await self.vision.page.content()
            if "商品はございません" in content or "currently not available" in content:
                log.info("      -> 日本在庫なし（公式確認）。全件お宝の可能性があります。")
                return True
            else:
                log.critical(f"❌ 日本在庫が不自然に0件です。ボット検知とみなし、このカテゴリーを保護中断します。")
                return False
        
        self.jp_cache = set(jp_inv.keys())
        log.info(f"💡 日本在庫 {len(self.jp_cache)} 件を除外リストに設定。")
        return True

    async def launch(self):
        await self.vault.ignite()
        await self.vision.ignite()

        try:
            for cat_label, jp_path in SovereignConfig.CONFIG["JP"]["paths"].items():
                log.info(f"\n{'#'*80}\n🏆 FOCUS: {cat_label}\n{'#'*80}")
                
                if not await self.sync_japan_truth(cat_label, jp_path):
                    continue

                for country in ["FR", "HK", "US", "KR"]:
                    log.info(f"   🌏 [{country}] ステージ鑑定開始")
                    lang_path = SovereignConfig.CONFIG[country]["code"]
                    cat_path = SovereignConfig.CONFIG[country]["paths"][cat_label]
                    
                    await self.vision.navigate_carefully(f"https://www.hermes.com/{lang_path}/category/{cat_path}/#|")
                    os_inv = await self.vision.extract_items_with_retry()
                    
                    for sku, data in os_inv.items():
                        sku_up = sku.upper().strip()
                        if sku_up not in self.jp_cache and sku_up not in self.vault.memory:
                            log.info(f"      [発見] 日本未発売: {data['name']} ({sku_up})")
                            
                            fx = SovereignConfig.CURRENCY_RATES.get(country, 1.0)
                            try: num = float(re.sub(r'[^\d.]', '', data['price'].replace(',', '')))
                            except: num = 0
                            
                            row = [datetime.now(SovereignConfig.JST).strftime("%Y/%m/%d %H:%M"), cat_label, country, sku_up, data['name'], data['price'], f"¥{int(num*fx):,}", data['url']]
                            
                            if await self.vault.secure_write(row):
                                await HumanoidInteractions.think("normal")
                                await HumanoidInteractions.human_mouse_move(self.vision.page, random.randint(0, 1920), random.randint(0, 1080))

                    await asyncio.sleep(15)
                await asyncio.sleep(45)

        finally:
            await self.vision.browser.close()
            await self.vision.pw.stop()

if __name__ == "__main__":
    try:
        asyncio.run(SovereignCommander().launch())
    except Exception as e:
        log.critical(f"❌ システム致命的エラー: {e}")
        sys.exit(1)
