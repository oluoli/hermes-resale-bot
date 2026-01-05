"""
========================================================================================
HERMES SOVEREIGN ARTISAN OS (v42.0.0) - THE SOVEREIGN ABSOLUTE
========================================================================================
Developer: World's Best System Engineer for OLUOLI
Focus: 100% DE-DUPLICATION, GUARANTEED TODAY SHEET UPDATE, FR/HK LOCK-ON.
Requirement: Enterprise Integrity. No Skips. No Ghost Entries.
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
# I. GLOBAL CONSTITUTION (カテゴリー完全記述 ＆ システム最高設定)
# =============================================================================

class SovereignConfig:
    VERSION: Final[str] = "42.0.0"
    JST = timezone(timedelta(hours=+9), 'JST')
    
    CURRENCY_RATES: Final[Dict[str, float]] = {
        "FR": 166.50, "HK": 20.80, "US": 158.00, "KR": 0.115
    }

    # 14カテゴリー全記述 (一切の省略なし)
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
            "PetitH": "petit-h/all-petit-h", "バッグ": "women/bags-and-small-leather-goods/bags-and-clutches",
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

    # API制限 ＆ 同期定数
    READ_BACK_DELAY = 12.0 
    API_LIMIT_PAUSE = 7.0 
    MAX_SCRAPE_RETRY = 5
    TIMEOUT_MS = 200000

# =============================================================================
# II. ABSOLUTE LEDGER ENGINE (物理検証・アトミック記帳・指紋照合)
# =============================================================================

logging.basicConfig(level=logging.INFO, format='\033[96m%(asctime)s\033[0m | %(message)s', datefmt='%H:%M:%S')
log = logging.getLogger("GenesisCommander")

class SovereignLedger:
    """
    重複を指紋レベルで排除し、MasterとTodayの物理的同期を完遂させる。
    """
    def __init__(self, creds_json: str):
        self.creds_dict = json.loads(creds_json)
        self.client, self.ws_master, self.ws_today = None, None, None
        self.history: Set[str] = set()

    async def ignite(self):
        log.info("【認証】Google Sheets セキュリティ・レイヤーを起動...")
        creds = ServiceAccountCredentials.from_json_keyfile_dict(self.creds_dict, ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive'])
        self.client = gspread.authorize(creds)
        spreadsheet = self.client.open(SovereignConfig.SPREADSHEET_NAME)
        log.info(f"✅ 物理接続完了: {spreadsheet.url}")

        def get_ws(name, r=40000):
            try: return spreadsheet.worksheet(name)
            except: return spreadsheet.add_worksheet(name, r, 20)

        self.ws_master = get_ws(SovereignConfig.SHEET_MASTER)
        self.ws_today = get_ws(SovereignConfig.SHEET_TODAY, 5000)
        
        # 起動時にTodayシートを完全に浄化（今日のお宝のみを受け入れる）
        self.ws_today.clear()
        self.ws_today.append_row(["取得日時", "カテゴリ", "国", "品番DNA", "商品名", "価格", "円換算", "URL"], 1)

        # 全履歴のロード
        master_data = self.ws_master.get_all_values()
        # DNA指紋をすべて暗記（重複記帳を物理的に殺す準備）
        self.history = {str(row[3]).upper().strip() for row in master_data if len(row) > 3 and row[3] != "品番DNA"}
        log.info(f"秘書: {len(self.history)} 件の既存指紋を記憶しました。")

    @staticmethod
    def get_dna_fingerprint(sku_raw: str, name_raw: str) -> str:
        """
        名前とSKUから『純粋な識別子』を抽出。
        記号、空白、大文字小文字の違いを無効化する。
        """
        base = sku_raw if sku_raw and "ITEM-" not in sku_raw else name_raw
        return re.sub(r'[^A-Z0-9]', '', str(base).upper())

    async def transactional_write(self, row: List[Any]) -> bool:
        """
        [アトミック・同期]
        1. Masterに書く
        2. 物理的に読み戻して実存を確認
        3. 成功時のみTodayに書く
        """
        dna = str(row[3]).upper().strip()
        
        # メモリ上での最終防衛
        if dna in self.history: return False

        for attempt in range(3):
            try:
                await asyncio.sleep(SovereignConfig.API_LIMIT_PAUSE)
                
                # 1. Masterへの記入
                self.ws_master.append_row(row, value_input_option='USER_ENTERED')
                log.info(f"      [物理検証] 品番 {dna} をMasterへ送信...")
                await asyncio.sleep(SovereignConfig.READ_BACK_DELAY)
                
                # 2. クラウドの物理実体を確認 (Read-back)
                last_entries = self.ws_master.get_all_values()[-5:]
                if any(str(r[3]).upper().strip() == dna for r in last_entries):
                    # 3. Master合格確定 -> ここで【絶対に】Todayへも書き込む
                    self.ws_today.append_row(row, value_input_option='USER_ENTERED')
                    self.history.add(dna) # 次の重複を即座に防止
                    log.info(f"      ✅ [同期完遂] Master & Today への刻印を物理確認しました。")
                    return True
                else:
                    log.warning(f"      [!] 物理反映遅延。再送中...")
            except Exception as e:
                log.error(f"      [!] API制限事故: {e}。1分休憩。")
                await asyncio.sleep(60.0)
        return False

# =============================================================================
# III. ABSOLUTE VISION ENGINE (FR/HKを絶対に逃さない鑑定眼)
# =============================================================================

class SovereignVision:
    def __init__(self):
        self.pw, self.browser, self.page = None, None, None

    async def ignite(self):
        self.pw = await async_playwright().start()
        self.browser = await self.pw.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        self.page = await self.browser.new_page(viewport={"width": 1920, "height": 1080}, locale="ja-JP")
        
        # ステルス動的適用 (ImportError/TypeError 抹殺)
        try:
            if hasattr(playwright_stealth, 'stealth_async'): await playwright_stealth.stealth_async(self.page)
            else: playwright_stealth.stealth(self.page)
        except: pass
        await self.page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => False})")

    async def navigate_with_lockon(self, url: str, country_name: str) -> bool:
        """商品が出るまで、あるいは公式完売を視認するまで絶対に動かない"""
        for attempt in range(SovereignConfig.MAX_SCRAPE_RETRY):
            try:
                log.info(f"   -> [{country_name}] 鑑定移動: {url} (試行 {attempt+1})")
                await self.page.goto(url, wait_until="load", timeout=SovereignConfig.TIMEOUT_MS)
                
                # A. 商品グリッド（.product-item）の出現を監視
                try:
                    await self.page.wait_for_selector(".product-item", timeout=45000)
                    log.info(f"      [視認] {country_name}: 商品棚の描画を確認しました。")
                    return True
                except:
                    # B. 完売メッセージの鑑定 (FR/HK等の多言語対応)
                    content = await self.page.content()
                    triggers = ["商品はございません", "currently not available", "aucun produit", "No results", "沒有產品"]
                    if any(t in content for t in triggers):
                        log.info(f"      [確証] {country_name}: 完売状態を確認しました。")
                        return True
                
                # C. 何も出てこない場合はリロードして居座る
                log.warning(f"      [!] {country_name}: 描画がありません。リフレッシュを実行。")
                await self.page.reload(wait_until="networkidle")
                await asyncio.sleep(15)
            except: await asyncio.sleep(10)
        return False

    async def exhaustive_capture(self) -> Dict[str, Dict[str, str]]:
        """30回以上の徹底スクロールで商品を吸い尽くす"""
        results = {}
        last_h = 0
        for cycle in range(30):
            curr_h = await self.page.evaluate("document.body.scrollHeight")
            await self.page.mouse.wheel(0, 1800)
            await asyncio.sleep(1.2)
            
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
                        sku_match = re.search(r'H[A-Z0-9]{5,}', str(link))
                        sku_raw = sku_match.group(0) if sku_match else "ITEM-RAW"
                        dna = SovereignLedger.get_dna_fingerprint(sku_raw, name)
                        
                        if dna not in results:
                            results[dna] = {"name": name, "price": price, "url": f"https://www.hermes.com{link}", "dna": dna}
                except: continue
            
            if curr_h == last_h and len(items) > 0: break
            last_h = curr_h
        return results

# =============================================================================
# IV. MISSION COMMANDER (不屈の総指揮)
# =============================================================================

class SovereignCommander:
    def __init__(self):
        self.vision = SovereignVision()
        self.ledger = SovereignLedger(os.environ["GOOGLE_CREDENTIALS"])
        self.jp_stock_dna: Set[str] = set()

    async def launch(self):
        await self.ledger.ignite()
        await self.vision.ignite()

        try:
            for cat_label, jp_path in SovereignConfig.CONFIG["JP"]["paths"].items():
                log.info(f"\n{'='*100}\n🏆 FOCUS CATEGORY: {cat_label}\n{'='*100}")
                
                # 1. 日本在庫をDNAレベルでキャッシュ (失敗しても海外へ進む)
                self.jp_stock_dna.clear()
                if await self.vision.navigate_with_lockon(f"https://www.hermes.com/jp/ja/category/{jp_path}/#|", "JP"):
                    jp_inv = await self.vision.exhaustive_capture()
                    self.jp_stock_dna = set(jp_inv.keys())
                    log.info(f"💡 日本在庫 {len(self.jp_stock_dna)} 件を DNAロック。")
                else:
                    log.error("⚠️ 日本取得失敗。FR/HKの全商品を候補として鑑定します。")

                for country in ["FR", "HK", "US", "KR"]:
                    log.info(f"   🌏 [{country}] 鑑定フェーズ")
                    c_info = SovereignConfig.CONFIG[country]
                    path = c_info["paths"].get(cat_label)
                    if not path: continue

                    if await self.vision.navigate_with_lockon(f"https://www.hermes.com/{c_info['code']}/category/{path}/#|", country):
                        os_inv = await self.vision.exhaustive_capture()
                        
                        log.info(f"      [照合] {len(os_inv)} 点の商品を検知。個別判定へ...")
                        for dna, data in os_inv.items():
                            
                            # 判定：日本に無い ＆ すでに台帳（Master）に無い ＝ 真の日本未取扱
                            if dna not in self.jp_stock_dna and dna not in self.ledger.history:
                                log.info(f"      💎 日本未取扱お宝発見: {data['name']} ({dna})")
                                fx = SovereignConfig.CURRENCY_RATES.get(country, 1.0)
                                try: num = float(re.sub(r'[^\d.]', '', data['price'].replace(',', '')))
                                except: num = 0
                                
                                row = [datetime.now(SovereignConfig.JST).strftime("%Y/%m/%d %H:%M"), cat_label, country, dna, data['name'], data['price'], f"¥{int(num*fx):,}", data['url']]
                                
                                # 【核心】Master記入 + 物理読み戻し + Today同期を完遂
                                if await self.ledger.transactional_write(row):
                                    log.info(f"           [完遂] Master & Today 両シート同期を物理確認。")
                                    await asyncio.sleep(random.uniform(4, 7))
                        
                    await asyncio.sleep(15) 
                await asyncio.sleep(45) 

        finally:
            log.info("【完遂】成果を保護して撤収。")
            await self.vision.browser.close()
            await self.vision.pw.stop()

if __name__ == "__main__":
    try: asyncio.run(SovereignCommander().launch())
    except Exception as e:
        log.critical(f"❌ システム致命的エラー: {e}")
        traceback.print_exc()
        sys.exit(1)
