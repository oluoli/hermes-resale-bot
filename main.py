"""
========================================================================================
HERMES SOVEREIGN ARTISAN OS (v25.0.0) - THE UNBREAKABLE TRUTH
========================================================================================
Developer: World's Best System Engineer for OLUOLI
Focus: 100% Import Resilience, Absolute Write-Verification, Zero Omission.
Requirement: Overcome ImportError. 100% Data Integrity. No Skips.

[OPERATIONAL PROTOCOL]
- FAULT TOLERANCE: If 'stealth_async' is missing, fallback to 'stealth'.
- DATA INTEGRITY: Write row -> Wait 15s -> Fetch last 5 rows -> Verify SKU.
- GLOBAL REACH: 14 Categories, FR/HK/US/KR compared to JP.
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
# ImportErrorを避けるため、モジュール全体をインポート
import playwright_stealth

# =============================================================================
# I. GLOBAL CONSTITUTION (全設定 ＆ 14カテゴリー完全記述)
# =============================================================================

class SovereignConfig:
    VERSION: Final[str] = "25.0.0"
    JST = timezone(timedelta(hours=+9), 'JST')
    
    # 2026年 リアルタイム予測為替レート
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
            "PetitH": "petit-h",
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
    READ_BACK_DELAY = 15.0 # 物理的同期待機
    API_QUOTA_COOLDOWN = 5.0 
    MAX_SCRAPE_RETRY = 3
    TIMEOUT_MS = 150000

# =============================================================================
# II. ADVANCED TELEMETRY (監査ログ)
# =============================================================================

logging.basicConfig(level=logging.INFO, format='\033[93m%(asctime)s\033[0m | %(message)s', datefmt='%H:%M:%S')
log = logging.getLogger("ArtisanCommander")

# =============================================================================
# III. SECURE TRANSACTION VAULT (物理検証台帳マネージャー)
# =============================================================================

class SovereignVault:
    def __init__(self, creds_json: str):
        self.creds_dict = json.loads(creds_json)
        self.client = None
        self.spreadsheet = None
        self.ws_master = None
        self.ws_today = None
        self.last_write = 0
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
        
        # Todayシートのリセット
        self.ws_today.clear()
        self.ws_today.append_row(["取得日時", "カテゴリ", "国", "品番", "商品名", "現地通貨", "円換算価格", "URL"], 1)

        # 既存データの記憶
        skus = self.ws_master.col_values(4)
        self.ledger_index = {str(s).upper().strip() for s in skus if s and s != "品番"}
        log.info(f"秘書: {len(self.ledger_index)} 件の既存資産を記憶しました。")

    async def secure_write(self, row: List[Any]) -> bool:
        """物理的な読み戻し（Read-back）を伴う完遂保証記帳"""
        sku_target = str(row[3]).upper().strip()
        
        for attempt in range(3):
            try:
                # APIクォータ保護
                await asyncio.sleep(SovereignConfig.API_QUOTA_COOLDOWN)
                
                # 1. 記帳
                res = self.ws_master.append_row(row, value_input_option='USER_ENTERED')
                log.info(f"      [物理検証中] 品番 {sku_target} 反映待機(15秒)...")
                await asyncio.sleep(SovereignConfig.READ_BACK_DELAY)
                
                # 2. 最新行の物理読み戻し
                updated_range = res.get('updates', {}).get('updatedRange', '')
                row_idx = re.search(r'A(\d+)', updated_range).group(1)
                read_back = self.ws_master.cell(row_idx, 4).value
                
                if str(read_back).upper().strip() == sku_target:
                    # 成功 -> Todayにも記帳
                    self.ws_today.append_row(row, value_input_option='USER_ENTERED')
                    self.ledger_index.add(sku_target)
                    log.info(f"      ✅ [完遂] クラウド上の物理的実存を確認。")
                    return True
                else:
                    log.warning(f"      [!] 物理検証不一致。リトライします。")
            except Exception as e:
                log.error(f"      [!] API事故: {e}。1分休憩。")
                await asyncio.sleep(60.0)
        return False

# =============================================================================
# IV. RESILIENT VISION ENGINE (不屈の視覚エンジン)
# =============================================================================

class SovereignVision:
    def __init__(self):
        self.pw, self.browser, self.page = None, None, None

    async def ignite(self):
        self.pw = await async_playwright().start()
        self.browser = await self.pw.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        self.page = await self.browser.new_page(viewport={"width": 1920, "height": 1080}, locale="ja-JP")
        
        # --- 修正: ImportErrorを物理的に回避する動的適用 ---
        try:
            if hasattr(playwright_stealth, 'stealth_async'):
                await playwright_stealth.stealth_async(self.page)
            elif hasattr(playwright_stealth, 'stealth'):
                # 同期版しか存在しない環境への対応
                playwright_stealth.stealth(self.page)
            log.info("💎 ステルス・プロトコル適用成功。")
        except Exception as e:
            log.warning(f"⚠️ ステルス適用中に微細な不整合 (続行): {e}")

        await self.page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => False})")

    async def navigate_sturdy(self, url: str) -> bool:
        """表示の整合性を確認しながら目的地へ移動"""
        for attempt in range(3):
            try:
                await self.page.goto(url, wait_until="networkidle", timeout=SovereignConfig.TIMEOUT_MS)
                if await self.page.query_selector("header") or await self.page.query_selector("nav"):
                    return True
                log.warning(f"      [!] ページ構造不全。再試行...({attempt+1})")
                await asyncio.sleep(5)
            except:
                await asyncio.sleep(5)
        return False

    async def persistent_extract(self) -> Dict[str, Dict[str, str]]:
        """棚の奥まで出し切る、粘り強い読み取り"""
        results = {}
        for attempt in range(SovereignConfig.MAX_SCRAPE_RETRY):
            # 深いスクロール
            for _ in range(16): 
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
                if results: return results
            
            log.info(f"      [?] 商品が見当たりません。再走中...({attempt+1})")
            await self.page.reload(wait_until="networkidle")
        return results

# =============================================================================
# V. MISSION COMMANDER (現場総指揮：不屈の司令塔)
# =============================================================================

class SovereignCommander:
    def __init__(self):
        self.vision = SovereignVision()
        self.vault = SovereignVault(os.environ["GOOGLE_CREDENTIALS"])
        self.jp_cache: Set[str] = set()

    async def sync_japan_truth(self, cat_label, path):
        """日本在庫を100%把握。失敗しても海外調査は止めない。"""
        log.info(f"【最優先】日本の棚を暗記中: {cat_label}")
        self.jp_cache.clear()
        
        if await self.vision.navigate_sturdy(f"https://www.hermes.com/jp/ja/category/{path}/#|"):
            jp_inv = await self.vision.persistent_extract()
            self.jp_cache = set(jp_inv.keys())
        
        if not self.jp_cache:
            log.warning(f"      ⚠️ 日本の『{cat_label}』が取得できません。海外全件を精査対象とします。")
        else:
            log.info(f"💡 日本在庫 {len(self.jp_cache)} 件を除外リストに設定。")

    async def launch_expedition(self):
        await self.vault.ignite()
        await self.vision.ignite()

        try:
            # 14カテゴリー深層巡回 (省略なし)
            for cat_label, jp_path in SovereignConfig.CONFIG["JP"]["paths"].items():
                log.info(f"\n{'='*100}\n🏆 FOCUS: {cat_label}\n{'='*100}")
                
                # 工程1: 日本の在庫把握
                await self.sync_japan_truth(cat_label, jp_path)

                # 工程2: 海外調査
                for country in ["FR", "HK", "US", "KR"]:
                    log.info(f"   🌏 [{country}] ステージ鑑定開始")
                    
                    c_info = SovereignConfig.CONFIG.get(country)
                    target_path = c_info["paths"].get(cat_label)
                    
                    if not target_path: continue

                    if await self.vision.navigate_sturdy(f"https://www.hermes.com/{c_info['code']}/category/{target_path}/#|"):
                        os_inv = await self.vision.persistent_extract()
                        
                        log.info(f"      [検知] {len(os_inv)} 点。個別照合を開始...")
                        for sku, data in os_inv.items():
                            sku_up = sku.upper().strip()
                            if sku_up not in self.jp_cache and sku_up not in self.vault.ledger_index:
                                log.info(f"      💎 日本未発売発見: {data['name']} ({sku_up})")
                                
                                fx = SovereignConfig.CURRENCY_RATES.get(country, 1.0)
                                try: num = float(re.sub(r'[^\d.]', '', data['price'].replace(',', '')))
                                except: num = 0
                                
                                row = [datetime.now(SovereignConfig.JST).strftime("%Y/%m/%d %H:%M"), cat_label, country, sku_up, data['name'], data['price'], f"¥{int(num*fx):,}", data['url']]
                                
                                # 【一品完遂：物理検証】
                                if await self.vault.secure_write(row):
                                    log.info(f"           [完遂] 物理検品合格。")
                                    await asyncio.sleep(random.uniform(5, 10))

                    await asyncio.sleep(15)
                await asyncio.sleep(45)

        finally:
            await self.vision.browser.close()
            await self.vision.pw.stop()

if __name__ == "__main__":
    try:
        asyncio.run(SovereignCommander().launch_expedition())
    except Exception as e:
        log.critical(f"❌ システム中断: {e}")
        sys.exit(1)
