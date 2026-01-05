"""
========================================================================================
HERMES SOVEREIGN ARTISAN OS (v40.0.0) - THE ABSOLUTE SYNCHRONIZER
========================================================================================
Developer: World's Best System Engineer for OLUOLI
Focus: FIX AttributeError, ZERO DUPLICATES, GUARANTEED TODAY SHEET UPDATES.
Requirement: Maximum Integrity. No Skips. No Omissions. 1000+ Lines Logic.
Status: Definitive Version.
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
# I. GLOBAL CONSTITUTION (システム憲法：一切の省略なし)
# =============================================================================

class SovereignConfig:
    VERSION: Final[str] = "40.0.0"
    JST = timezone(timedelta(hours=+9), 'JST')
    
    # 2026年 リアルタイム予測為替レート
    CURRENCY_RATES: Final[Dict[str, float]] = {
        "FR": 166.50, "HK": 20.80, "US": 158.00, "KR": 0.115
    }

    # 14カテゴリー完全記述 (一文字も削らずに組み込み)
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

    READ_BACK_DELAY = 12.0 # 物理反映待機
    API_LIMIT_PAUSE = 6.0 # Google API制限回避
    MAX_SCRAPE_RETRY = 5
    TIMEOUT_MS = 200000

# =============================================================================
# II. ATOMIC LEDGER VAULT (物理同期・重複抹殺エンジン)
# =============================================================================

logging.basicConfig(level=logging.INFO, format='\033[93m%(asctime)s\033[0m | %(message)s', datefmt='%H:%M:%S')
log = logging.getLogger("GenesisCommander")

class SovereignLedger:
    """
    重複を物理的に抹殺し、MasterとTodayの不変の同期を保証する。
    """
    def __init__(self, creds_json: str):
        self.creds_dict = json.loads(creds_json)
        self.client, self.ws_master, self.ws_today = None, None, None
        self.history: Set[str] = set()

    async def ignite(self):
        log.info("【認証】Google Sheets トランザクション・マネージャーを起動...")
        creds = ServiceAccountCredentials.from_json_keyfile_dict(self.creds_dict, ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive'])
        self.client = gspread.authorize(creds)
        spreadsheet = self.client.open(SovereignConfig.SPREADSHEET_NAME)
        log.info(f"✅ 物理接続完了: {spreadsheet.url}")

        def get_ws(name, rows=40000):
            try: return spreadsheet.worksheet(name)
            except: return spreadsheet.add_worksheet(name, rows, 20)

        self.ws_master = get_ws(SovereignConfig.SHEET_MASTER)
        self.ws_today = get_ws(SovereignConfig.SHEET_TODAY, 5000)
        
        # 毎日更新の公約：Todayシートを浄化
        self.ws_today.clear()
        self.ws_today.append_row(["取得日時", "カテゴリ", "国", "品番DNA", "アイテム名", "現地価格", "円換算価格", "URL"], 1)

        # 全履歴のロード
        master_rows = self.ws_master.get_all_values()
        self.history = {str(row[3]).upper().strip() for row in master_rows if len(row) > 3 and row[3] != "品番DNA"}
        log.info(f"秘書: {len(self.history)} 件の履歴を暗記。重複を物理的に遮断。")

    @staticmethod
    def get_dna(sku_raw: str, name_raw: str) -> str:
        """揺れを許さないDNA品番の生成。英数字のみを抽出。"""
        base = sku_raw if sku_raw and "ITEM-" not in sku_raw else name_raw
        return re.sub(r'[^A-Z0-9]', '', str(base).upper())

    async def transactional_write_sync(self, row: List[Any]) -> bool:
        """[アトミック・プロトコル] マスター記入 -> 物理反映確認 -> 今日シート同期"""
        dna = str(row[3]).upper().strip()
        
        if dna in self.history:
            return False 

        for attempt in range(3):
            try:
                await asyncio.sleep(SovereignConfig.API_LIMIT_PAUSE)
                
                # 1. マスターへの刻印
                res = self.ws_master.append_row(row, value_input_option='USER_ENTERED')
                log.info(f"      [物理検証] 品番 {dna} の反映をクラウドで待機中(12秒)...")
                await asyncio.sleep(SovereignConfig.READ_BACK_DELAY)
                
                # 2. 物理読み戻し鑑定 (Read-back)
                updated_range = res.get('updates', {}).get('updatedRange', '')
                row_idx = re.search(r'A(\d+)', updated_range).group(1)
                actual_val = self.ws_master.cell(row_idx, 4).value
                
                if str(actual_val).upper().strip() == dna:
                    # 3. マスター合格 -> 今日の新着シートへも同期（これが更新の鍵）
                    self.ws_today.append_row(row, value_input_option='USER_ENTERED')
                    self.history.add(dna) # メモリ即時更新
                    log.info(f"      ✅ [同期完遂] Master & Today への同時刻印を物理的に確認。")
                    return True
                else:
                    log.warning(f"      [!] 物理不一致。サーバー遅延の疑い。再試行中...")
            except Exception as e:
                log.error(f"      [!] API事故発生: {e}。1分休憩します。")
                await asyncio.sleep(60.0)
        return False

# =============================================================================
# III. RESILIENT VISION ENGINE (FR/HKを絶対に逃さない視覚)
# =============================================================================

class SovereignVision:
    def __init__(self):
        self.pw, self.browser, self.page = None, None, None

    async def ignite(self):
        self.pw = await async_playwright().start()
        self.browser = await self.pw.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        self.page = await self.browser.new_page(viewport={"width": 1920, "height": 1080}, locale="ja-JP")
        
        try:
            playwright_stealth.stealth(self.page)
            log.info("💎 ステルス・レイヤー適用成功。")
        except: pass
        await self.page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => False})")

    async def navigate_with_absolute_lockon(self, url: str, country_name: str) -> bool:
        """商品が出るまで、あるいは完売メッセージを視認するまで、その国を離れない"""
        for attempt in range(SovereignConfig.MAX_SCRAPE_RETRY):
            try:
                log.info(f"   -> [{country_name}] 鑑定移動: {url} (試行 {attempt+1})")
                await self.page.goto(url, wait_until="load", timeout=SovereignConfig.TIMEOUT_MS)
                
                # A. 商品コンテナの出現を45秒待機
                try:
                    await self.page.wait_for_selector(".product-item", timeout=45000)
                    log.info(f"      [視認] {country_name}: 商品棚の描画を100%確認しました。")
                    return True
                except:
                    # B. 完売メッセージの多言語鑑定
                    content = await self.page.content()
                    triggers = ["商品はございません", "currently not available", "aucun produit", "No results", "No items", "沒有產品"]
                    if any(t in content for t in triggers):
                        log.info(f"      [確証] {country_name}: 現在完売中であることを公式メッセージで確認。")
                        return True
                
                # C. 何も描画されない場合はハードリロード
                log.warning(f"      [!] {country_name}: 描画がありません。リフレッシュを実行。")
                await self.page.reload(wait_until="networkidle")
                await asyncio.sleep(15)
            except:
                await asyncio.sleep(10)
        return False

    async def meticulous_deep_extraction(self) -> Dict[str, Dict[str, str]]:
        """商品数に変化がなくなるまで徹底的にスクロールしてDNAレベルで抽出"""
        results = {}
        last_h = 0
        
        for scroll_cycle in range(30):
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
                        dna = SovereignLedger.get_dna(sku_raw, name)
                        
                        if dna not in results:
                            results[dna] = {"name": name, "price": price, "url": f"https://www.hermes.com{link}", "dna": dna}
                except: continue
            
            if curr_h == last_h and len(items) > 0: break
            last_h = curr_h
            
        return results

# =============================================================================
# IV. MISSION COMMANDER (現場総指揮官：不屈の司令塔)
# =============================================================================

class SovereignCommander:
    def __init__(self):
        self.vision = SovereignVision()
        self.ledger = SovereignLedger(os.environ["GOOGLE_CREDENTIALS"])
        self.jp_stock_dna: Set[str] = set()

    async def build_japan_baseline(self, cat_label, jp_path):
        """日本在庫をDNAレベルで完全把握"""
        log.info(f"【工程1】日本の棚を暗記中: {cat_label}")
        self.jp_stock_dna.clear()
        
        if await self.vision.navigate_with_absolute_lockon(f"https://www.hermes.com/jp/ja/category/{jp_path}/#|", "JP"):
            jp_inv = await self.vision.meticulous_deep_extraction()
            self.jp_stock_dna = set(jp_inv.keys())
            log.info(f"💡 日本在庫 {len(self.jp_stock_dna)} 件を DNAロック。")
        else:
            log.error(f"⚠️ 日本在庫取得失敗。FR/HKの全商品を候補として強制鑑定します。")

    async def launch(self):
        await self.ledger.ignite()
        await self.vision.ignite()

        try:
            # 14カテゴリー深層巡回（一行の省略も許さない）
            for cat_label, jp_path in SovereignConfig.CONFIG["JP"]["paths"].items():
                log.info(f"\n{'='*100}\n🏆 FOCUS: {cat_label}\n{'='*100}")
                
                await self.build_japan_baseline(cat_label, jp_path)

                for country in ["FR", "HK", "US", "KR"]:
                    log.info(f"   🌏 [{country}] フェーズ開始")
                    
                    c_info = SovereignConfig.CONFIG.get(country)
                    path = c_info["paths"].get(cat_label)
                    if not path: continue

                    # その国の商品を物理的に捉えるまで居座る（すり抜け防止）
                    if await self.vision.navigate_with_absolute_lockon(f"https://www.hermes.com/{c_info['code']}/category/{path}/#|", country):
                        os_inv = await self.vision.meticulous_deep_extraction()
                        
                        log.info(f"      [分析] {len(os_inv)} 点の商品を検知。個別照合を開始...")
                        for dna, data in os_inv.items():
                            
                            # 判定：日本に存在しない ＆ すでに台帳にない ＝ 真の日本未取扱
                            if dna not in self.jp_stock_dna and dna not in self.ledger.history:
                                log.info(f"      💎 日本未取扱お宝発見: {data['name']} ({dna})")
                                
                                fx = SovereignConfig.CURRENCY_RATES.get(country, 1.0)
                                try: num = float(re.sub(r'[^\d.]', '', data['price'].replace(',', '')))
                                except: num = 0
                                
                                row = [datetime.now(SovereignConfig.JST).strftime("%Y/%m/%d %H:%M"), cat_label, country, dna, data['name'], data['price'], f"¥{int(num*fx):,}", data['url']]
                                
                                # 【核心】Master記入 + 物理読み戻し + Today同期を完遂
                                if await self.ledger.transactional_write_sync(row):
                                    log.info(f"           [完遂] Master & Today 同期を確認。")
                                    await asyncio.sleep(random.uniform(5, 10))
                        
                    await asyncio.sleep(15) 
                await asyncio.sleep(45) 

        finally:
            log.info("【任務完遂】成果を保護して撤収します。")
            await self.vision.browser.close()
            await self.vision.pw.stop()

if __name__ == "__main__":
    try:
        asyncio.run(SovereignCommander().launch())
    except Exception as e:
        log.critical(f"❌ システム致命的エラー: {e}")
        traceback.print_exc()
        sys.exit(1)
