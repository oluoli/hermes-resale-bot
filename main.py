"""
========================================================================================
HERMES SOVEREIGN ARTISAN OS (v27.0.0) - THE TOTAL RECONNAISSANCE
========================================================================================
Developer: World's Best System Engineer for OLUOLI
Focus: FR/Overseas Absolute Capture. Zero-Skip Logic. Physical Verification.
Status: Professional Execution Grade. (No Omissions)

[CRITICAL OPERATIONAL CHANGES]
- NO MORE SKIPS: Even if Japan sync fails, FR/HK/US/KR will be FULLY audited.
- DEEP WAIT: Specific logic to wait for French grid-items to physically render.
- WRITE GUARANTEE: Verification by reading back the actual cell value from Google Cloud.
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
    VERSION: Final[str] = "27.0.0"
    JST = timezone(timedelta(hours=+9), 'JST')
    
    CURRENCY_RATES: Final[Dict[str, float]] = {
        "FR": 166.50, "HK": 20.80, "US": 158.00, "KR": 0.115
    }

    # カテゴリー設定: あなたの指示に基づき、一切の省略なく14カテゴリーを全記述
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
            "PetitH": "petit-h", "バッグ": "women/bags-and-small-leather-goods/bags-and-clutches",
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

    SPREADSHEET_NAME: Final[str] = "Hermes_Check_List"
    SHEET_MASTER: Final[str] = "master"
    SHEET_TODAY: Final[str] = "todays_new"

    # API検証 ＆ ステルス定数
    READ_BACK_DELAY = 12.0 
    API_LIMIT_PAUSE = 4.5
    MAX_RETRY = 5
    TIMEOUT_MS = 150000

# =============================================================================
# II. SECURE TRANSACTION VAULT (物理検証・台帳マネージャー)
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
        self.history: Set[str] = set()

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
        self.ws_today.append_row(["取得日", "カテゴリ", "国", "品番", "商品名", "現地価格", "円換算", "URL"], 1)

        skus = self.ws_master.col_values(4)
        self.history = {str(s).upper().strip() for s in skus if s and s != "品番"}
        log.info(f"秘書: {len(self.history)} 件の既存資産を記憶しました。")

    async def secure_write(self, row: List[Any]) -> bool:
        """物理的な読み戻し（Read-back）を伴う完遂保証記帳"""
        sku_target = str(row[3]).upper().strip()
        for attempt in range(SovereignConfig.MAX_RETRY):
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
                    self.history.add(sku_target)
                    log.info(f"      ✅ [完遂] クラウド上の物理実存を確認。")
                    return True
            except Exception as e:
                log.warning(f"      [!] API制限または通信エラー。1分休息します ({attempt+1}): {e}")
                await asyncio.sleep(60)
        return False

# =============================================================================
# III. UNYIELDING VISION ENGINE (不屈の視覚エンジン)
# =============================================================================

class SovereignVision:
    def __init__(self):
        self.pw, self.browser, self.page = None, None, None

    async def ignite(self):
        self.pw = await async_playwright().start()
        self.browser = await self.pw.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        self.page = await self.browser.new_page(viewport={"width": 1920, "height": 1080}, locale="ja-JP")
        
        # --- 動的ステルス適用 (ImportError 回避) ---
        try:
            if hasattr(playwright_stealth, 'stealth_async'):
                await playwright_stealth.stealth_async(self.page)
            else:
                playwright_stealth.stealth(self.page)
        except: pass
        await self.page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => False})")

    async def navigate_with_patience(self, url: str) -> bool:
        """表示の整合性を確認しながら目的地へ移動。FR等の遅延に対応。"""
        for attempt in range(3):
            try:
                log.info(f"   -> 移動中: {url} (試行 {attempt+1})")
                await self.page.goto(url, wait_until="load", timeout=SovereignConfig.TIMEOUT_MS)
                
                # 商品リストが表示されるか、あるいは「在庫なし」メッセージが出るまで待機
                try:
                    await self.page.wait_for_selector(".product-item", timeout=30000)
                    return True
                except:
                    # 在庫なしメッセージの確認
                    content = await self.page.content()
                    if "商品はございません" in content or "currently not available" in content or "aucun produit" in content:
                        log.info("      [報告] 在庫なし（公式メッセージ確認済）")
                        return True
                    
                log.warning("      [!] コンテンツの描画が確認できません。リフレッシュします...")
                await self.page.reload(wait_until="networkidle")
                await asyncio.sleep(5)
            except:
                await asyncio.sleep(5)
        return False

    async def exhaustive_extract(self, country_code: str) -> Dict[str, Dict[str, str]]:
        """棚の奥まで出し切る、フランス等で1件も漏らさないための抽出"""
        results = {}
        # 徹底的なスクロール工程
        for wheel_step in range(20):
            await self.page.mouse.wheel(0, 1500)
            await asyncio.sleep(1.0)
            
            items = await self.page.query_selector_all(".product-item")
            for item in items:
                try:
                    name_el = await item.query_selector(".product-item-name")
                    link_el = await item.query_selector("a")
                    price_el = await item.query_selector(".product-item-price")
                    
                    if name_el and link_el:
                        name = (await name_el.inner_text()).strip()
                        price = (await price_el.inner_text()).strip() if price_el else "0"
                        link = await link_el.get_attribute("href")
                        if not link: continue
                        
                        # 品番抽出（URLからの正規表現 ＋ フォールバックとして名称ハッシュ）
                        sku_match = re.search(r'H[A-Z0-9]{5,}', link)
                        sku = sku_match.group(0).upper().strip() if sku_match else f"GEN-{hash(name)}"
                        
                        if sku not in results:
                            results[sku] = {"name": name, "price": price, "url": f"https://www.hermes.com{link}"}
                except: continue
                
        if results:
            log.info(f"      [成功] {country_code}: {len(results)}個の商品を正確に補足。")
        return results

# =============================================================================
# IV. MISSION COMMANDER (現場総指揮官：不屈の司令塔)
# =============================================================================

class SovereignCommander:
    def __init__(self):
        self.vision = SovereignVision()
        self.vault = SovereignVault(os.environ["GOOGLE_CREDENTIALS"])
        self.jp_cache: Set[str] = set()

    async def launch_expedition(self):
        await self.vault.ignite()
        await self.vision.ignite()

        try:
            # 14カテゴリー完全巡回
            for cat_label, jp_path in SovereignConfig.CONFIG["JP"]["paths"].items():
                log.info(f"\n{'='*100}\n🏆 FOCUS CATEGORY: {cat_label}\n{'='*100}")
                
                # --- 工程1: 日本在庫のキャッシュ構築 ---
                self.jp_cache.clear()
                if await self.vision.navigate_with_patience(f"https://www.hermes.com/jp/ja/category/{jp_path}/#|"):
                    jp_inv = await self.vision.exhaustive_extract("JP")
                    self.jp_cache = set(jp_inv.keys())
                    log.info(f"💡 日本在庫 {len(self.jp_cache)} 件をキャッシュ。")
                else:
                    log.error(f"⚠️ 日本の在庫取得に失敗。FR/海外の全商品を『日本未入荷』として精査します。")

                # --- 工程2: 海外調査 (FR -> HK -> US -> KR) ---
                for country in ["FR", "HK", "US", "KR"]:
                    log.info(f"   🌏 [{country}] ステージ鑑定開始")
                    
                    config_country = SovereignConfig.CONFIG.get(country)
                    target_path = config_country["paths"].get(cat_label)
                    
                    if not target_path: continue

                    if await self.vision.navigate_with_patience(f"https://www.hermes.com/{config_country['code']}/category/{target_path}/#|"):
                        os_inv = await self.vision.exhaustive_extract(country)
                        
                        for sku, data in os_inv.items():
                            sku_up = sku.upper().strip()
                            
                            # 記帳判断：日本に存在しない ＆ 過去台帳に未記載 ＝ 新規お宝
                            # (日本取得失敗時は jp_cache が空なので、全てが記帳対象になる＝見逃しゼロ)
                            if sku_up not in self.jp_cache and sku_up not in self.vault.history:
                                log.info(f"      💎 未発売特定: {data['name']} ({sku_up})")
                                
                                fx = SovereignConfig.CURRENCY_RATES.get(country, 1.0)
                                try: num = float(re.sub(r'[^\d.]', '', data['price'].replace(',', '')))
                                except: num = 0
                                
                                row = [datetime.now(SovereignConfig.JST).strftime("%Y/%m/%d %H:%M"), cat_label, country, sku_up, data['name'], data['price'], f"¥{int(num*fx):,}", data['url']]
                                
                                # 【一品完遂：物理検証】
                                if await self.vault.secure_write(row):
                                    log.info(f"           [完遂] スプレッドシート同期完了。")
                                    await asyncio.sleep(random.uniform(5, 10))
                        
                    await asyncio.sleep(15) # 国別待機
                await asyncio.sleep(45) # カテゴリ別待機

        finally:
            await self.vision.browser.close()
            await self.vision.pw.stop()

if __name__ == "__main__":
    try:
        asyncio.run(SovereignCommander().launch_expedition())
    except Exception as e:
        log.critical(f"❌ システム中断: {e}")
        traceback.print_exc()
        sys.exit(1)
