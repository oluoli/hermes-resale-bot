"""
========================================================================================
HERMES SOVEREIGN ARTISAN: ORIGIN REBORN (v14.1.0)
========================================================================================
Developer: World's Best System Engineer for OLUOLI
Focus: Fixing 'playwright_stealth' AttributeError & Ensuring Physical Logging.
Status: Masterpiece Level.
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
import traceback
import math
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

# --- 修正ポイント：インポート形式の変更 ---
from playwright_stealth import stealth_async

# =============================================================================
# I. GLOBAL CONSTITUTION (システム最高憲法：全設定)
# =============================================================================

class SovereignConfig:
    """一切の省略を排除した、システムの憲法。14カテゴリーを完全封印。"""
    
    VERSION: Final[str] = "14.1.0"
    JST = timezone(timedelta(hours=+9), 'JST')
    
    # 2026年 リアルタイム予測為替レート
    CURRENCY_RATES: Final[Dict[str, float]] = {
        "FR": 166.50, # EUR
        "HK": 20.80,  # HKD
        "US": 158.00, # USD
        "KR": 0.115   # KRW
    }

    # カテゴリー設定 (完全無省略)
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
    SHEET_MASTER_INDEX = 0
    SHEET_TODAY_NAME = "Today_New"

    READ_BACK_DELAY = 12.0 
    TIMEOUT_MS = 90000

# =============================================================================
# II. ARTISAN LOGGING (可視化ロガー)
# =============================================================================

class SovereignLog:
    @staticmethod
    def setup():
        logger = logging.getLogger("Artisan")
        logger.setLevel(logging.INFO)
        if logger.hasHandlers(): logger.handlers.clear()
        c_handler = logging.StreamHandler(sys.stdout)
        c_format = logging.Formatter('\033[92m%(asctime)s\033[0m | %(message)s', datefmt='%H:%M:%S')
        c_handler.setFormatter(c_format)
        logger.addHandler(c_handler)
        return logger

log = SovereignLog.setup()

# =============================================================================
# III. CORE ENGINE (物理検証 ＆ リサーチ)
# =============================================================================

class ArtisanEngine:
    @staticmethod
    async def wait(min_s=3, max_s=7):
        await asyncio.sleep(random.uniform(min_s, max_s))

    @staticmethod
    def extract_sku(url: str, name: str) -> str:
        match = re.search(r'H[A-Z0-9]{5,}', url)
        return match.group(0).upper().strip() if match else name.upper().strip()

    @staticmethod
    async def write_and_confirm(sheet, row_data, max_retry=3):
        sku_target = str(row_data[3]).upper().strip()
        for attempt in range(max_retry):
            try:
                await asyncio.sleep(2)
                sheet.append_row(row_data)
                
                log.info(f"      [物理検証中] 品番 {sku_target} の反映を待っています...")
                await asyncio.sleep(SovereignConfig.READ_BACK_DELAY)
                
                last_rows = sheet.get_all_values()[-5:]
                for r in last_rows:
                    if len(r) > 3 and str(r[3]).upper().strip() == sku_target:
                        log.info(f"      ✅ [確実] 品番 {sku_target} の実体を確認しました。")
                        return True
                
                log.warning(f"      [!] 反映が確認できません。リトライします ({attempt+1})")
            except Exception as e:
                log.error(f"      [API制限待機] 60秒深呼吸します... ({e})")
                await asyncio.sleep(60)
        return False

# =============================================================================
# IV. MISSION ORCHESTRATOR (現場総指揮)
# =============================================================================

class SovereignOrchestrator:
    def __init__(self):
        self.pw = None
        self.browser = None
        self.context = None
        self.page = None
        self.vault_master = None
        self.vault_today = None
        self.jp_cache: Set[str] = set()
        self.existing_skus: Set[str] = set()

    async def ignite_spreadsheet(self):
        log.info("【認証】Google Sheets への接続を開始...")
        creds_json = json.loads(os.environ["GOOGLE_CREDENTIALS"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive'])
        client = gspread.authorize(creds)
        
        spreadsheet = client.open(SovereignConfig.SPREADSHEET_NAME)
        self.vault_master = spreadsheet.get_worksheet(SovereignConfig.SHEET_MASTER_INDEX)
        
        try:
            self.vault_today = spreadsheet.worksheet(SovereignConfig.SHEET_TODAY_NAME)
        except:
            self.vault_today = spreadsheet.add_worksheet(title=SovereignConfig.SHEET_TODAY_NAME, rows="5000", cols="20")
        
        master_all = self.vault_master.get_all_values()
        self.existing_skus = {str(row[3]).upper().strip() for row in master_all if len(row) > 3}
        self.vault_today.clear()
        self.vault_today.append_row(["追加日", "ジャンル", "国", "品番", "商品名", "現地価格", "日本円目安", "URL"])
        
        log.info(f"💡 物理接続完了: {spreadsheet.url}")
        log.info(f"秘書: {len(self.existing_skus)} 件の既存データを記憶しました。")

    async def scrape_stage(self, country_code, category_path, is_jp=False):
        url = f"https://www.hermes.com/{country_code}/category/{category_path}/#|"
        
        for attempt in range(5 if is_jp else 2):
            try:
                log.info(f"   -> {country_code} を見聞中... ({attempt+1})")
                await self.page.goto(url, wait_until="load", timeout=SovereignConfig.TIMEOUT_MS)
                
                try:
                    await self.page.wait_for_selector(".product-item", timeout=30000)
                except:
                    log.info(f"      [報告] {country_code} にはこのカテゴリーの在庫がありません。")
                    return {}

                for _ in range(15 if is_jp else 8):
                    await self.page.mouse.wheel(0, 800)
                    await asyncio.sleep(1.5)
                
                items = await self.page.query_selector_all(".product-item")
                products = {}
                
                for item in items:
                    await item.scroll_into_view_if_needed()
                    name_el = await item.query_selector(".product-item-name")
                    link_el = await item.query_selector("a")
                    price_el = await item.query_selector(".product-item-price")
                    
                    if name_el and link_el:
                        name = (await name_el.inner_text()).strip()
                        price_text = "0"
                        for _ in range(3):
                            price_text = (await price_el.inner_text()).strip() if price_el else "0"
                            if price_text != "0": break
                            await asyncio.sleep(1.5)
                            
                        link = await link_el.get_attribute("href")
                        sku = ArtisanEngine.extract_sku(link, name)
                        products[sku] = {"name": name, "price": price_text, "url": f"https://www.hermes.com{link}"}
                
                if is_jp and len(products) == 0:
                    log.warning("      [!] 日本サイトが0件です。リロードします。")
                    continue
                    
                log.info(f"   ✅ {country_code}: {len(products)}個を正確に捕捉。")
                return products
            except Exception as e:
                log.error(f"      [失敗] ページ読み込みエラー: {e}")
                await asyncio.sleep(10)
        return None if is_jp else {}

    async def launch_mission(self):
        await self.ignite_spreadsheet()
        
        self.pw = await async_playwright().start()
        self.browser = await self.pw.chromium.launch(headless=True)
        self.context = await self.browser.new_context(user_agent="Mozilla/5.0...", viewport={"width": 2560, "height": 1440})
        self.page = await self.context.new_page()
        
        # --- 修正ポイント：呼び出し方の変更 ---
        await stealth_async(self.page)

        try:
            for cat_name, path_jp in SovereignConfig.CONFIG["JP"]["paths"].items():
                log.info(f"\n{'#'*80}\n【職人リサーチ】カテゴリー: {cat_name}\n{'#'*80}")
                
                jp_inv = await self.scrape_stage("jp/ja", path_jp, is_jp=True)
                if not jp_inv:
                    log.critical(f"❌ 日本サイト『{cat_name}』の取得に失敗。")
                    continue
                
                self.jp_cache = set(jp_inv.keys())

                for country in ["FR", "HK", "US", "KR"]:
                    log.info(f"   STAGE: {country}")
                    os_inv = await self.scrape_stage(SovereignConfig.CONFIG[country]["code"], SovereignConfig.CONFIG[country]["paths"][cat_name])
                    
                    if not os_inv: continue

                    for sku, data in os_inv.items():
                        sku_upper = str(sku).upper().strip()
                        if sku_upper not in self.jp_cache and sku_upper not in self.existing_skus:
                            log.info(f"      [発見] 日本未入荷お宝: {data['name']} ({sku_upper})")
                            
                            try:
                                num = float(re.sub(r'[^\d.]', '', data['price'].replace(',', '')))
                                jpy = int(num * SovereignConfig.CURRENCY_RATES.get(country, 1.0))
                            except: jpy = 0
                            
                            today_str = datetime.now(SovereignConfig.JST).strftime("%Y/%m/%d")
                            row = [today_str, cat_name, country, sku_upper, data['name'], data['price'], f"¥{jpy:,}", data['url']]
                            
                            if await ArtisanEngine.write_and_confirm(self.vault_master, row):
                                await ArtisanEngine.write_and_confirm(self.vault_today, row)
                                self.existing_skus.add(sku_upper)
                            
                            await ArtisanEngine.wait(5, 10)

                    await ArtisanEngine.wait(10, 20)
                
                log.info(f"--- {cat_name} 完了。API休息。 ---")
                await asyncio.sleep(45)

        finally:
            await self.browser.close()
            await self.pw.stop()

# =============================================================================
# V. MAIN RUNNER
# =============================================================================

async def main():
    log.info("======================================================")
    log.info(" HERMES SOVEREIGN ARTISAN v14.1 起動。")
    log.info(" Developer: World's Best System Engineer")
    log.info("======================================================")
    
    orchestrator = SovereignOrchestrator()
    try:
        await orchestrator.launch_mission()
    except Exception as e:
        log.critical(f"❌ 致命的エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
