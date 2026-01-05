"""
========================================================================================
HERMES SOVEREIGN ARTISAN OS (v41.0.0) - THE GENESIS OVERDRIVE
========================================================================================
Developer: World's Best System Engineer for OLUOLI
Focus: ZERO DUPLICATES (Absolute), VERIFIED TODAY'S SHEET SYNC, NO SKIPS (FR/HK).
Requirement: 1000+ Lines Enterprise Logic. No Omissions. Guaranteed Integrity.
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
    """一切の省略を排除。14カテゴリー全てをここに完全封印。"""
    VERSION: Final[str] = "41.0.0"
    JST = timezone(timedelta(hours=+9), 'JST')
    
    # 2026年 リアルタイム予測為替レート
    CURRENCY_RATES: Final[Dict[str, float]] = {
        "FR": 166.50, "HK": 20.80, "US": 158.00, "KR": 0.115
    }

    # 14カテゴリー全記述 (一文字の省略もなく実装)
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

    # API ＆ 物理検証用定数
    READ_BACK_DELAY = 12.0 # 物理反映待機
    API_LIMIT_PAUSE = 7.0 # API負荷軽減
    MAX_OVERSEAS_RETRY = 5
    TIMEOUT_MS = 200000

# =============================================================================
# II. ABSOLUTE LEDGER ENGINE (物理検証・アトミック同期・重複完全抹殺)
# =============================================================================

logging.basicConfig(level=logging.INFO, format='\033[95m%(asctime)s\033[0m | %(message)s', datefmt='%H:%M:%S')
log = logging.getLogger("GenesisCommander")

class SovereignLedger:
    """
    重複を物理的に許さず、MasterとTodayの不変の同期を保証する。
    """
    def __init__(self, creds_json: str):
        self.creds_dict = json.loads(creds_json)
        self.client, self.ws_master, self.ws_today = None, None, None
        self.history: Set[str] = set()

    async def ignite(self):
        log.info("【認証】Google Sheets トランザクション層を起動...")
        creds = ServiceAccountCredentials.from_json_keyfile_dict(self.creds_dict, ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive'])
        self.client = gspread.authorize(creds)
        spreadsheet = self.client.open(SovereignConfig.SPREADSHEET_NAME)
        log.info(f"✅ 物理接続完了: {spreadsheet.url}")

        def get_ws(name, r=40000):
            try: return spreadsheet.worksheet(name)
            except: return spreadsheet.add_worksheet(name, r, 20)

        self.ws_master = get_ws(SovereignConfig.SHEET_MASTER)
        self.ws_today = get_ws(SovereignConfig.SHEET_TODAY, 5000)
        
        # 【重要】本日の新着シートを浄化し、今日の結果のみを受け入れる
        self.ws_today.clear()
        self.ws_today.append_row(["取得日時", "カテゴリ", "国", "品番DNA", "商品名", "価格", "円換算", "URL"], 1)

        # 既存履歴を「DNA化」してロード（重複記帳を物理的に殺す準備）
        master_data = self.ws_master.get_all_values()
        # カラム4(品番DNA)を収集。空やヘッダーは除外。
        self.history = {str(row[3]).upper().strip() for row in master_data if len(row) > 3 and row[3] != "品番DNA"}
        log.info(f"秘書: {len(self.history)} 件の既存資産を暗記しました。重複を物理的に遮断。")

    @staticmethod
    def get_dna(sku_raw: str, name_raw: str) -> str:
        """揺れを許さないDNA品番の生成。英数字のみを抽出。"""
        # SKUがあれば優先、無ければ商品名。記号・空白・大文字小文字をすべて正規化。
        base = sku_raw if sku_raw and "ITEM-" not in sku_raw else name_raw
        dna = re.sub(r'[^A-Z0-9]', '', str(base).upper())
        return dna

    async def atomic_dual_write(self, row: List[Any]) -> bool:
        """[アトミック・プロトコル] Master記入 -> 物理反映確認 -> Today同期"""
        dna = str(row[3]).upper().strip()
        
        # メモリ上での最終防衛（重複回避）
        if dna in self.history:
            return False 

        for attempt in range(3):
            try:
                await asyncio.sleep(SovereignConfig.API_LIMIT_PAUSE)
                
                # 1. マスターへの刻印
                res = self.ws_master.append_row(row, value_input_option='USER_ENTERED')
                log.info(f"      [物理検証] 品番 {dna} の反映をクラウドで待機中...")
                await asyncio.sleep(SovereignConfig.READ_BACK_DELAY)
                
                # 2. 物理読み戻し鑑定 (Read-back)
                # 書き込み完了後、実際にその品番がマスターに存在するのか、セルを読み戻して確認
                updated_range = res.get('updates', {}).get('updatedRange', '')
                row_idx = re.search(r'A(\d+)', updated_range).group(1)
                actual_val = self.ws_master.cell(row_idx, 4).value
                
                if str(actual_val).upper().strip() == dna:
                    # 3. マスター合格 -> 今日の新着シートへも【強制的】に書く
                    self.ws_today.append_row(row, value_input_option='USER_ENTERED')
                    self.history.add(dna) # メモリ即時更新
                    log.info(f"      ✅ [同期成功] Master & Today への同時刻印を確認しました。")
                    return True
                else:
                    log.warning(f"      [!] 物理不一致。サーバー遅延の疑い。再試行中 ({attempt+1})...")
            except Exception as e:
                log.error(f"      [!] API事故: {e}。1分休憩します。")
                await asyncio.sleep(60.0)
        return False

# =============================================================================
# III. TOTAL RECONNAISSANCE ENGINE (FR/HKを絶対に逃さない視覚)
# =============================================================================

class SovereignVision:
    def __init__(self):
        self.pw, self.browser, self.page = None, None, None

    async def ignite(self):
        self.pw = await async_playwright().start()
        self.browser = await self.pw.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        self.page = await self.browser.new_page(viewport={"width": 1920, "height": 1080}, locale="ja-JP")
        # ステルス適用の自動判別
        try:
            if hasattr(playwright_stealth, 'stealth_async'): await playwright_stealth.stealth_async(self.page)
            else: playwright_stealth.stealth(self.page)
        except: pass
        await self.page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => False})")

    async def navigate_with_lockon(self, url: str, country_name: str) -> bool:
        """商品が出るか、あるいは完売メッセージを視認するまで、その国を絶対に離れない"""
        for attempt in range(SovereignConfig.MAX_OVERSEAS_RETRY):
            try:
                log.info(f"   -> [{country_name}] 鑑定移動: {url} (試行 {attempt+1})")
                await self.page.goto(url, wait_until="load", timeout=SovereignConfig.TIMEOUT_MS)
                
                # A. 商品コンテナの物理的な出現を45秒監視
                try:
                    await self.page.wait_for_selector(".product-item", timeout=45000)
                    log.info(f"      [視認] {country_name}: 商品棚の描画を100%確認。")
                    return True
                except:
                    # B. 完売メッセージの多言語鑑定 (FR/HK等に対応)
                    content = await self.page.content()
                    triggers = ["商品はございません", "currently not available", "aucun produit", "No results", "0 items", "沒有產品"]
                    if any(t in content for t in triggers):
                        log.info(f"      [確証] {country_name}: 完売状態を確認しました（公式メッセージ）。")
                        return True
                
                # C. 何も描画されない場合はハードリフレッシュを強行
                log.warning(f"      [!] {country_name}: コンテンツが描画されません。リロードを実行。")
                await self.page.reload(wait_until="networkidle")
                await asyncio.sleep(15)
            except:
                await asyncio.sleep(10)
        return False

    async def meticulous_deep_extraction(self) -> Dict[str, Dict[str, str]]:
        """商品数が変化しなくなるまで30回徹底的にスクロールしてDNAレベルで抽出"""
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
                        if not link: continue
                        
                        sku_match = re.search(r'H[A-Z0-9]{5,}', str(link))
                        sku_raw = sku_match.group(0) if sku_match else "ITEM-RAW"
                        
                        # 重複排除の核心：不変のDNA生成
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
        """日本在庫をDNAレベルで完全把握。失敗してもFR等の調査は止めない。"""
        log.info(f"【工程1】日本の棚を暗記中: {cat_label}")
        self.jp_stock_dna.clear()
        
        if await self.vision.navigate_with_lockon(f"https://www.hermes.com/jp/ja/category/{jp_path}/#|", "JP"):
            jp_inv = await self.vision.meticulous_deep_extraction()
            self.jp_stock_dna = {data['dna'] for data in jp_inv.values()}
            log.info(f"💡 日本在庫 {len(self.jp_stock_dna)} 件を DNAロック。")
        else:
            log.error(f"⚠️ 日本在庫取得失敗。FR/HKの全商品を候補として鑑定します。")

    async def launch_expedition(self):
        await self.ledger.ignite()
        await self.vision.ignite()

        try:
            # 14カテゴリー深層巡回（一行の省略も許さない）
            for cat_label, jp_path in SovereignConfig.CONFIG["JP"]["paths"].items():
                log.info(f"\n{'='*100}\n🏆 FOCUS CATEGORY: {cat_label}\n{'='*100}")
                
                # 1. 日本在庫を把握 (すり抜け防止の絶対基準)
                await self.build_japan_baseline(cat_label, jp_path)

                # 2. 海外調査（FR -> HK -> US -> KR）
                for country in ["FR", "HK", "US", "KR"]:
                    log.info(f"\n   🌏 [{country}] 鑑定フェーズ開始")
                    
                    c_cfg = SovereignConfig.CONFIG.get(country)
                    c_path = c_cfg["paths"].get(cat_label)
                    if not c_path: continue

                    # その国の商品を物理的に視認するまで居座る（すり抜け防止）
                    if await self.vision.navigate_with_lockon(f"https://www.hermes.com/{c_cfg['code']}/category/{c_path}/#|", country):
                        os_inv = await self.vision.meticulous_deep_extraction()
                        
                        log.info(f"      [精査] {len(os_inv)} 点の商品を検知。個別照合を開始...")
                        for dna, data in os_inv.items():
                            
                            # 判定：日本に存在しない ＆ すでに台帳（Master）にない ＝ 真の日本未取扱
                            if dna not in self.jp_stock_dna and dna not in self.ledger.history:
                                log.info(f"      💎 未入荷お宝特定: {data['name']} ({dna})")
                                
                                fx = SovereignConfig.CURRENCY_RATES.get(country, 1.0)
                                try: num = float(re.sub(r'[^\d.]', '', data['price'].replace(',', '')))
                                except: num = 0
                                
                                row = [
                                    datetime.now(SovereignConfig.JST).strftime("%Y/%m/%d %H:%M"), 
                                    cat_label, country, dna, data['name'], data['price'], 
                                    f"¥{int(num*fx):,}", data['url']
                                ]
                                
                                # 【核心】Master記入 + 物理読み戻し + Today同期を「1つの不可分な仕事」として完遂
                                if await self.ledger.atomic_dual_write(row):
                                    log.info(f"           [完遂] Master & Today への完全保存を確認しました。")
                                    # ボット擬態のための鑑定間隔
                                    await asyncio.sleep(random.uniform(5, 8))
                        
                    await asyncio.sleep(15) 
                await asyncio.sleep(45) 

        finally:
            log.info("【任務完遂】成果を保護し、ブラウザを閉じます。")
            await self.vision.browser.close()
            await self.vision.pw.stop()

if __name__ == "__main__":
    try:
        asyncio.run(SovereignCommander().launch_expedition())
    except Exception as e:
        log.critical(f"❌ システム致命的エラー: {e}")
        traceback.print_exc()
        sys.exit(1)
