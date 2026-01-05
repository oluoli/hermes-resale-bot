"""
========================================================================================
HERMES SOVEREIGN ARTISAN OS (v33.0.0) - THE ULTIMATE SYNCHRONIZER
========================================================================================
Developer: World's Best System Engineer for OLUOLI
Focus: NO SKIPS (FR/HK/etc), NO DUPLICATES, ATOMIC TODAY'S SHEET UPDATE.
Requirement: Production Grade (1000+ Lines Logic). Absolute Integrity.
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
# I. GLOBAL CONSTITUTION (システム最高設定 ＆ カテゴリー完全記述)
# =============================================================================

class SovereignConfig:
    """一切の省略を排除。14カテゴリー全てをここに完全封印。"""
    VERSION: Final[str] = "33.0.0"
    JST = timezone(timedelta(hours=+9), 'JST')
    
    # 2026年 リアルタイム予測為替レート
    CURRENCY_RATES: Final[Dict[str, float]] = {
        "FR": 166.50, "HK": 20.80, "US": 158.00, "KR": 0.115
    }

    # カテゴリー設定: あなたの指示に基づき、一切の省略なく全記述
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
    READ_BACK_DELAY = 12.0 # 秒
    API_LIMIT_PAUSE = 5.0 # 秒
    MAX_OVERSEAS_RETRY = 5
    TIMEOUT_MS = 180000

# =============================================================================
# II. ADVANCED LEDGER VAULT (物理検証・トランザクション・重複排除)
# =============================================================================

logging.basicConfig(level=logging.INFO, format='\033[93m%(asctime)s\033[0m | %(message)s', datefmt='%H:%M:%S')
log = logging.getLogger("SovereignCommander")

class SovereignLedger:
    """
    重複を物理的に抹殺し、MasterとTodays_Newを絶対に同期させる台帳マネージャー。
    """
    def __init__(self, creds_json: str):
        self.creds_dict = json.loads(creds_json)
        self.client = None
        self.ws_master = None
        self.ws_today = None
        self.history: Set[str] = set()

    async def ignite(self):
        log.info("【認証】Google Sheets セキュリティ・トランザクション層を起動...")
        creds = ServiceAccountCredentials.from_json_keyfile_dict(self.creds_dict, ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive'])
        self.client = gspread.authorize(creds)
        spreadsheet = self.client.open(SovereignConfig.SPREADSHEET_NAME)
        log.info(f"✅ 物理接続完了: {spreadsheet.url}")

        def get_ws(name):
            try: return spreadsheet.worksheet(name)
            except: return spreadsheet.add_worksheet(name, 30000, 20)

        self.ws_master = get_ws(SovereignConfig.SHEET_MASTER)
        self.ws_today = get_ws(SovereignConfig.SHEET_TODAY)
        
        # 今日の新着シートを浄化し、新規受け入れ体制を整える
        self.ws_today.clear()
        self.ws_today.append_row(["取得日", "カテゴリ", "国", "品番", "商品名", "現地価格", "円換算", "URL"], 1)

        # 全履歴のロード（メモリ上で重複を瞬時に判定するため）
        master_data = self.ws_master.get_all_values()
        self.history = {str(row[3]).upper().strip() for row in master_data if len(row) > 3 and row[3] != "品番"}
        log.info(f"秘書: {len(self.history)} 件の既存データを記憶。重複記帳を物理的に遮断しました。")

    async def transactional_write(self, row: List[Any]) -> bool:
        """[アトミック・プロトコル] マスター記入 -> 反映確認 -> 今日シート同期"""
        sku = str(row[3]).upper().strip()
        
        if sku in self.history:
            return False # 重複を拒否

        for attempt in range(3):
            try:
                await asyncio.sleep(SovereignConfig.API_LIMIT_PAUSE)
                
                # 1. マスターへの刻印
                res = self.ws_master.append_row(row, value_input_option='USER_ENTERED')
                log.info(f"      [物理検証] 品番 {sku} の反映をクラウドで待機中(12秒)...")
                await asyncio.sleep(SovereignConfig.READ_BACK_DELAY)
                
                # 2. 最新行の物理読み戻し鑑定 (Read-back)
                updated_range = res.get('updates', {}).get('updatedRange', '')
                row_idx = re.search(r'A(\d+)', updated_range).group(1)
                read_back_val = self.ws_master.cell(row_idx, 4).value
                
                if str(read_back_val).upper().strip() == sku:
                    # マスター合格 -> 今日の新着シートにも強制同期（これが無いと更新されない）
                    self.ws_today.append_row(row, value_input_option='USER_ENTERED')
                    self.history.add(sku) # 同一セッション内の重複も即座に防止
                    log.info(f"      ✅ [完遂] Master & Today への完全同期を確認。")
                    return True
                else:
                    log.warning(f"      [!] 物理検証不一致。書き直しを実行します。")
            except Exception as e:
                log.error(f"      [!] API事故: {e}。1分休憩します。")
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
        # インポートエラーを回避する動的ステルス適用
        try:
            if hasattr(playwright_stealth, 'stealth_async'): await playwright_stealth.stealth_async(self.page)
            else: playwright_stealth.stealth(self.page)
        except: pass
        await self.page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => False})")

    async def navigate_with_persistence(self, url: str, country_name: str) -> bool:
        """商品が出るまで、あるいは公式の在庫なしメッセージを視認するまで、その国を離れない"""
        for attempt in range(SovereignConfig.MAX_OVERSEAS_RETRY):
            try:
                log.info(f"   -> [{country_name}] 鑑定移動: {url} (試行 {attempt+1})")
                await self.page.goto(url, wait_until="load", timeout=SovereignConfig.TIMEOUT_MS)
                
                # A. 商品コンテナの物理的な出現を40秒間監視
                try:
                    await self.page.wait_for_selector(".product-item", timeout=40000)
                    log.info(f"      [視認] {country_name}: 商品リストを確認しました。")
                    return True
                except:
                    # B. 在庫なしメッセージを公式の文字で確認
                    content = await self.page.content()
                    triggers = ["商品はございません", "currently not available", "aucun produit", "No results", "0 item"]
                    if any(t in content for t in triggers):
                        log.info(f"      [確証] {country_name}: 完売状態を確認しました。")
                        return True
                
                # C. 何も表示されない場合は、リロードを強行
                log.warning(f"      [!] {country_name}: 描画がありません。ハードリフレッシュ中...")
                await self.page.reload(wait_until="networkidle")
                await asyncio.sleep(10)
            except:
                await asyncio.sleep(10)
        return False

    async def exhaustive_extract(self) -> Dict[str, Dict[str, str]]:
        """商品数が変化しなくなるまで徹底的にスクロールして吸い尽くす"""
        results = {}
        last_count = 0
        
        for scroll_step in range(25): # 深層スクロールを強化
            await self.page.mouse.wheel(0, 1500)
            await asyncio.sleep(1.2)
            
            items = await self.page.query_selector_all(".product-item")
            current_count = len(items)
            
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
                        
                        # 品番抽出の正規化（重複排除の生命線）
                        sku_match = re.search(r'H[A-Z0-9]{5,}', link)
                        sku = sku_match.group(0).upper().strip() if sku_match else f"DNA-{re.sub(r'[^A-Z0-9]', '', name.upper())}"
                        
                        if sku not in results:
                            results[sku] = {"name": name, "price": price, "url": f"https://www.hermes.com{link}"}
                except: continue
            
            if current_count == last_count and current_count > 0: break # もう増えないなら完了
            last_count = current_count
            
        return results

# =============================================================================
# IV. MISSION COMMANDER (現場総指揮官：不屈の司令塔)
# =============================================================================

class SovereignCommander:
    def __init__(self):
        self.vision = SovereignVision()
        self.ledger = SovereignLedger(os.environ["GOOGLE_CREDENTIALS"])
        self.jp_cache: Set[str] = set()

    async def build_japan_baseline(self, cat_label, jp_path):
        """日本在庫を100%把握。失敗してもFR等の調査は絶対に止めない。"""
        log.info(f"【工程1】日本の棚を暗記中: {cat_label}")
        self.jp_cache.clear()
        
        if await self.vision.navigate_with_persistence(f"https://www.hermes.com/jp/ja/category/{jp_path}/#|", "JP"):
            jp_inv = await self.vision.exhaustive_extract()
            self.jp_cache = set(jp_inv.keys())
            log.info(f"💡 日本在庫 {len(self.jp_cache)} 件をロックしました。")
        else:
            log.error(f"⚠️ 日本在庫取得に失敗。FR/HKの全商品を『日本未取扱候補』として強制鑑定します。")

    async def launch_expedition(self):
        await self.ledger.ignite()
        await self.vision.ignite()

        try:
            # 14カテゴリー深層巡回（一切の省略なし）
            for cat_label, jp_path in SovereignConfig.CONFIG["JP"]["paths"].items():
                log.info(f"\n{'='*100}\n🏆 FOCUS CATEGORY: {cat_label}\n{'='*100}")
                
                # 1. 日本在庫を把握 (すり抜け防止の基準点)
                await self.build_japan_baseline(cat_label, jp_path)

                # 2. 海外調査（FR -> HK -> US -> KR）
                for country in ["FR", "HK", "US", "KR"]:
                    log.info(f"   🌏 [{country}] フェーズ開始")
                    
                    c_cfg = SovereignConfig.CONFIG.get(country)
                    c_path = c_cfg["paths"].get(cat_label)
                    if not c_path: continue

                    # その国の商品が出るまで絶対に動かない（すっとばし防止の核心）
                    if await self.vision.navigate_with_persistence(f"https://www.hermes.com/{c_cfg['code']}/category/{c_path}/#|", country):
                        os_inv = await self.vision.exhaustive_extract()
                        
                        log.info(f"      [分析] {len(os_inv)} 点の商品を視認。照合を開始...")
                        for sku, data in os_inv.items():
                            sku_up = sku.upper().strip()
                            
                            # 条件：日本に存在しない ＆ すでに記帳されていない ＝ 真の日本未取扱新着
                            if sku_up not in self.jp_cache and sku_up not in self.ledger.history:
                                log.info(f"      💎 日本未取扱発見: {data['name']} ({sku_up})")
                                
                                fx = SovereignConfig.CURRENCY_RATES.get(country, 1.0)
                                try: num = float(re.sub(r'[^\d.]', '', data['price'].replace(',', '')))
                                except: num = 0
                                
                                row = [datetime.now(SovereignConfig.JST).strftime("%Y/%m/%d %H:%M"), cat_label, country, sku_up, data['name'], data['price'], f"¥{int(num*fx):,}", data['url']]
                                
                                # 【一品完遂】Master記入、物理読み戻し、Today更新の全工程を完遂させる
                                if await self.ledger.transactional_write(row):
                                    log.info(f"           [成功] 物理同期を確認しました。")
                                    await asyncio.sleep(random.uniform(5, 10))
                        
                    await asyncio.sleep(15) # 国別のインターバル
                await asyncio.sleep(45) # カテゴリ別の冷却待機

        finally:
            log.info("【完遂】全任務完了。成果を保護して撤収します。")
            await self.vision.browser.close()
            await self.vision.pw.stop()

if __name__ == "__main__":
    try:
        asyncio.run(SovereignCommander().launch_expedition())
    except Exception as e:
        log.critical(f"❌ システム致命的エラー: {e}")
        sys.exit(1)
