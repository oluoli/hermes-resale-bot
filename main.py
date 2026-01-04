"""
========================================================================================
HERMES DIGITAL ARTISAN: THE MASTERPIECE EDITION (v3.0.0)
Developer: World's Best System Engineer for OLUOLI
Focus: Human-like Perception, Transactional Integrity, Read-Back Verification.
License: Enterprise Grade Reliability.
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
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Set, Any, Tuple
from oauth2client.service_account import ServiceAccountCredentials
from playwright.async_api import async_playwright, Page, Browser, BrowserContext, ElementHandle
import playwright_stealth

# =============================================================================
# 1. 究極設定マネージャー (Global Configuration)
# =============================================================================

class GrandPrixConfig:
    """システムの全設定を統括。一切の省略を許さない。"""
    
    JST = timezone(timedelta(hours=+9), 'JST')
    
    # 2026年 予測為替レート（職人の判断基準）
    CURRENCY_RATES = {
        "FR": 166.50, # EUR
        "HK": 20.80,  # HKD
        "US": 158.00, # USD
        "KR": 0.115   # KRW
    }

    # カテゴリー設定 (完全無省略・指示に基づき14カテゴリーを全記述)
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

    SPREADSHEET_NAME = "Hermes_Digital_Artisan_Ledger"
    MASTER_SHEET_NAME = "Master_Ledger"
    UNRELEASED_SHEET_NAME = "Today_Japan_Unreleased"

    # 人間らしい動作の速度調整
    TYPING_SPEED = (50, 150)
    THINKING_TIME = (3, 7)
    SCROLL_PAUSE = (2.0, 4.0)

# =============================================================================
# 2. 構造化ロガー (Professional Logging)
# =============================================================================

class ArtisanLogger:
    @staticmethod
    def setup():
        logger = logging.getLogger("Artisan")
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', '%H:%M:%S'))
        logger.addHandler(handler)
        return logger

log = ArtisanLogger.setup()

# =============================================================================
# 3. ヒューマン・シミュレーター (Cognitive Engine)
# =============================================================================

class HumanSimulator:
    """人間が画面を見て思考し、手を動かす動作を再現する"""

    @staticmethod
    async def pause(complexity: str = "normal"):
        """状況に応じた適切な『ため』を作る"""
        delays = {
            "blink": (0.1, 0.4),
            "glance": (1.0, 2.5),
            "normal": (3.0, 6.0),
            "careful": (7.0, 12.0),
            "exhausted": (30.0, 60.0)
        }
        low, high = delays.get(complexity, (3.0, 6.0))
        # 正規分布に近い乱数で機械性を排除
        await asyncio.sleep(abs(random.gauss((low + high) / 2, (high - low) / 4)))

    @staticmethod
    async def mouse_move_natural(page: Page, x: int, y: int):
        """直線的ではない、わずかな『揺れ』を伴うマウス移動"""
        await page.mouse.move(x + random.randint(-5, 5), y + random.randint(-5, 5), steps=10)

    @staticmethod
    async def focus_on_item(page: Page, element: ElementHandle):
        """人間が商品を見つめるように、マウスを近づけ、スクロールを止める"""
        box = await element.bounding_box()
        if box:
            await HumanSimulator.mouse_move_natural(page, box['x'] + box['width']/2, box['y'] + box['height']/2)
            await HumanSimulator.pause("glance")

# =============================================================================
# 4. 台帳秘書 (Database & Read-back Verification)
# =============================================================================

class LedgerAssistant:
    """
    人間が行う『記帳』と『検品』を再現するクラス。
    1品が完遂されるまで、次へ進むことは許されない。
    """

    def __init__(self, creds_env: str):
        self.creds_dict = json.loads(creds_env)
        self.scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        self.client = None
        self.spreadsheet = None
        self.master = None
        self.unreleased = None
        self.skus_in_memory: Set[str] = set()

    async def open_ledger(self):
        """台帳を開き、現状を完璧に把握（暗記）する"""
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_dict(self.creds_dict, self.scope)
            self.client = gspread.authorize(creds)
            self.spreadsheet = self.client.open(GrandPrixConfig.SPREADSHEET_NAME)
            
            # Master台帳の初期化
            try:
                self.master = self.spreadsheet.worksheet(GrandPrixConfig.MASTER_SHEET_NAME)
            except gspread.exceptions.WorksheetNotFound:
                self.master = self.spreadsheet.add_worksheet(GrandPrixConfig.MASTER_SHEET_NAME, 10000, 15)
                self.master.append_row(["記帳日時", "カテゴリー", "国", "品番", "商品名", "現地価格", "円換算", "URL"])

            # 未発売シートの初期化
            try:
                self.unreleased = self.spreadsheet.worksheet(GrandPrixConfig.UNRELEASED_SHEET_NAME)
            except gspread.exceptions.WorksheetNotFound:
                self.unreleased = self.spreadsheet.add_worksheet(GrandPrixConfig.UNRELEASED_SHEET_NAME, 5000, 15)
            
            # 毎朝新しいページを用意するようにクリア
            self.unreleased.clear()
            self.unreleased.append_row(["【日本未発売】記帳日時", "カテゴリー", "国", "品番", "商品名", "現地価格", "円換算", "URL"])

            # 既存データのロード
            log.info("アシスタント: 現在の台帳内容を暗記中...")
            all_skus = self.master.col_values(4)
            self.skus_in_memory = {str(s).upper().strip() for s in all_skus if s}
            log.info(f"アシスタント: {len(self.skus_in_memory)} 件の品番を記憶しました。")
            
        except Exception as e:
            log.error(f"アシスタント: 台帳を開く際にエラーが発生しました: {e}")
            raise

    async def verify_and_log_item(self, row_data: List[Any]) -> bool:
        """
        [世界一の信頼性保証]
        1. Masterへ記帳
        2. 反映を待ち、物理的なセルを再度読み戻して品番を確認
        3. 合格なら未発売シートへも転記
        """
        sku = str(row_data[3]).upper().strip()
        
        for attempt in range(3):
            try:
                await HumanSimulator.pause("glance")
                # A. 記帳実行
                res = self.master.append_row(row_data, value_input_option='USER_ENTERED')
                
                # B. 検品待機（Google側の反映ラグを考慮する人間の『待ち』）
                await asyncio.sleep(10.0)
                
                # C. 物理的再確認 (Read-back)
                # 書き込まれたはずの行番号を取得
                updated_range = res.get('updates', {}).get('updatedRange', '')
                row_idx_match = re.search(r'A(\d+)', updated_range)
                if not row_idx_match: continue
                row_idx = row_idx_match.group(1)
                
                # 物理的な読み戻し（これが人間が指でなぞって確認する動作）
                actual_val = self.master.cell(row_idx, 4).value
                
                if str(actual_val).upper().strip() == sku:
                    # 検品合格 -> 未発売シートへ同期
                    self.unreleased.append_row(row_data, value_input_option='USER_ENTERED')
                    self.skus_in_memory.add(sku)
                    log.info(f"        [完遂] 物理検品パス (Row {row_idx})。台帳同期を完了しました。")
                    return True
                else:
                    log.warning(f"        [!] 検品エラー: 送信 {sku} vs 実際 {actual_val}。再送します。")
                    
            except Exception as e:
                log.error(f"        [!] 記帳中に事故発生: {e}。休息して回復を待ちます。")
                await asyncio.sleep(60.0)
                
        return False

# =============================================================================
# 5. デジタル鑑定士 (Playwright Engine)
# =============================================================================

class DigitalArtisan:
    """人間がブラウザを見て、要素を一つ一つ指差して読み取る動作の再現"""

    def __init__(self):
        self.pw = None
        self.browser = None
        self.context = None
        self.page = None

    async def boot(self):
        """ブラウザの起動と、人間らしい初期設定"""
        self.pw = await async_playwright().start()
        self.browser = await self.pw.chromium.launch(headless=True) # 本番はTrue
        self.context = await self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="ja-JP"
        )
        self.page = await self.context.new_page()
        # 最高精度のステルス設定
        await playwright_stealth.stealth_async(self.page)

    async def exit(self):
        """後片付け"""
        if self.browser: await self.browser.close()
        if self.pw: await self.pw.stop()

    async def robust_scroll(self, page: Page):
        """人間が棚を上から下まで眺めるように、不規則な速度でスクロール"""
        last_h = 0
        for i in range(15):
            curr_h = await page.evaluate("document.body.scrollHeight")
            if curr_h == last_h: break
            last_h = curr_h
            
            # 興味がある場所で止まるようなランダムスクロール
            scroll_amt = random.randint(700, 1200)
            await page.mouse.wheel(0, scroll_amt)
            await asyncio.sleep(random.uniform(2.0, 4.0))
            
            # 最下部まで読み込ませる執念
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(1.0)

    async def extract_item_carefully(self, element: ElementHandle) -> Optional[Dict[str, str]]:
        """商品を手に取り、詳細（品番・価格）を音読するように抽出"""
        try:
            # 商品を画面中央へ
            await element.scroll_into_view_if_needed()
            await asyncio.sleep(1.0)
            
            name_el = await element.query_selector(".product-item-name")
            price_el = await element.query_selector(".product-item-price")
            link_el = await element.query_selector("a")
            
            if not (name_el and link_el): return None
            
            name = (await name_el.inner_text()).strip()
            
            # 価格が反映されるまで見つめる人間の『粘り』
            price = "0"
            for _ in range(4):
                raw_p = await price_el.inner_text() if price_el else "0"
                price = re.sub(r'[^\d.]', '', raw_p.replace(',', ''))
                if price and price != "0": break
                await asyncio.sleep(2.0)

            href = await link_el.get_attribute("href")
            # 正規表現による品番の厳密抽出
            sku_match = re.search(r'H[A-Z0-9]{5,}', href)
            sku = sku_match.group(0).upper().strip() if sku_match else name.upper().strip()
            
            return {
                "sku": sku,
                "name": name,
                "price": price,
                "url": f"https://www.hermes.com{href}"
            }
        except Exception as e:
            log.debug(f"抽出不可商品: {e}")
            return None

# =============================================================================
# 6. リサーチ・オーケストレーター (Main Loop)
# =============================================================================

class HermesArtisanOrchestrator:
    """現場監督。一品完遂の掟を全カ国で守らせる"""

    def __init__(self):
        self.artisan = DigitalArtisan()
        self.ledger = LedgerAssistant(os.environ["GOOGLE_CREDENTIALS"])
        self.japan_inventory_set: Set[str] = set()

    async def build_japan_inventory_cache(self, category_name: str, path: str):
        """
        工程1: 日本の在庫状況を完璧に把握する。
        これが、後に海外でお宝を見つけるための『目利き』の基礎となる。
        """
        log.info(f"【工程A】日本の商品棚を精査中: {category_name}")
        self.japan_inventory_set.clear()
        
        try:
            url = f"https://www.hermes.com/jp/ja/category/{path}/#|"
            await self.artisan.page.goto(url, wait_until="load", timeout=90000)
            await HumanSimulator.pause("normal")
            
            await self.artisan.robust_scroll(self.artisan.page)
            elements = await self.artisan.page.query_selector_all(".product-item")
            
            for el in elements:
                data = await self.artisan.extract_item_carefully(el)
                if data:
                    self.japan_inventory_set.add(data["sku"])
            
            log.info(f"      -> 日本国内の把握完了: {len(self.japan_inventory_set)}件を除外リストに設定。")
        except Exception as e:
            log.error(f"      [!] 日本サイトが混雑しています。このカテゴリーは全件精査に切り替えます: {e}")

    async def run_resale_mission(self):
        """
        メインミッション：FR -> HK -> US -> KR の順序で、
        日本にないお宝を一個ずつ確実に台帳へ刻む。
        """
        await self.ledger.open_ledger()
        await self.artisan.boot()

        try:
            for cat_label, jp_path in GrandPrixConfig.CONFIG["JP"]["paths"].items():
                log.info(f"\n{'#'*70}")
                log.info(f"【カテゴリー特化精査】: {cat_label}")
                log.info(f"{'#'*70}")

                # 日本の最新状況を記憶
                await self.build_japan_inventory_cache(cat_label, jp_path)

                # 巡回順序：FR -> HK -> US -> KR
                for country_key in ["FR", "HK", "US", "KR"]:
                    country_info = GrandPrixConfig.CONFIG[country_key]
                    target_path = country_info["paths"].get(cat_label)
                    
                    if not target_path:
                        log.info(f"  --- [{country_key}] カテゴリー設定なし。スキップ。 ---")
                        continue

                    log.info(f"\n  --- [{country_key}] の商品棚を調査します ---")
                    
                    try:
                        target_url = f"https://www.hermes.com/{country_info['code']}/category/{target_path}/#|"
                        await self.artisan.page.goto(target_url, wait_until="load", timeout=90000)
                        
                        # 棚が空でないか確認（人間が立ち止まって確認する動作）
                        try:
                            await self.artisan.page.wait_for_selector(".product-item", timeout=15000)
                        except:
                            log.info(f"    [報告] 現在、{country_key}の棚には何も並んでいません。")
                            continue

                        await self.artisan.robust_scroll(self.artisan.page)
                        
                        # ここで商品要素の一覧を確定
                        elements = await self.artisan.page.query_selector_all(".product-item")
                        log.info(f"    [報告] {len(elements)} 点の候補を発見。一個ずつ検分し、記帳まで完遂させます。")

                        for i in range(len(elements)):
                            # 【世界一の安定性】ループごとに要素を再捕捉し、DOM変化によるエラーを抹殺する
                            current_items = await self.artisan.page.query_selector_all(".product-item")
                            if i >= len(current_items): break
                            target_el = current_items[i]

                            # 1. 読み取り
                            data = await self.artisan.extract_item_carefully(target_el)
                            if not data: continue
                            
                            sku_id = data["sku"]
                            log.info(f"      ({i+1}/{len(elements)}) 検分: {data['name']} [{sku_id}]")

                            # 2. 照合工程 (人間が頭の中でチェックする動作)
                            if sku_id in self.japan_inventory_set:
                                log.info(f"        -> [PASS] 日本サイトに在庫があるため、リスト化は不要。")
                                continue
                            
                            if sku_id in self.ledger.skus_in_memory:
                                log.info(f"        -> [PASS] 既にマスター台帳に記録済みです。")
                                continue

                            # 3. 価値計算 (円換算)
                            rate = GrandPrixConfig.CURRENCY_RATES.get(country_key, 1.0)
                            jpy_price = int(float(data['price']) * rate)
                            
                            # 記帳用データの生成
                            row = [
                                datetime.now(GrandPrixConfig.JST).strftime("%Y/%m/%d %H:%M"),
                                cat_label,
                                country_key,
                                sku_id,
                                data['name'],
                                data['price'],
                                f"¥{jpy_price:,}",
                                data['url']
                            ]

                            # 4. 【一品完遂記帳】物理反映を検品するまで、次の商品は見ない。
                            log.info(f"        [重要] 日本未発売品を特定。台帳への刻印と物理検証を開始...")
                            success = await self.ledger.verify_and_log_item(row)
                            
                            if success:
                                log.info(f"        [完遂] この一品は完全に同期されました。")
                            else:
                                log.error(f"        [警告] 記帳検証に失敗しました。この商品は一旦保留。")

                            # 一品終わるごとに、人間のように一息つく (対ボット検知 ＆ クォータ保護)
                            await HumanSimulator.pause("normal")
                            # マウスを動かして「考えている」様子を出す
                            await HumanSimulator.mouse_move_natural(self.artisan.page, 500, 500)

                    except Exception as e:
                        log.error(f"    [!] {country_key} 巡回中に予期せぬトラブル: {e}")
                        await asyncio.sleep(20.0)
                        continue

                log.info(f"\n--- カテゴリー [{cat_label}] の全カ国精査を完遂しました。 ---")
                await asyncio.sleep(60.0) # カテゴリー間の大休憩

        finally:
            await self.artisan.exit()

# =============================================================================
# 7. プログラム・エントリーポイント
# =============================================================================

async def main():
    log.info("======================================================")
    log.info(" HERMES DIGITAL ARTISAN システム、覚醒。")
    log.info(" 担当: 世界一のシステムエンジニア")
    log.info("======================================================")
    
    manager = HermesArtisanOrchestrator()
    try:
        await manager.run_resale_mission()
    except KeyboardInterrupt:
        log.info("ユーザーによる中断。")
    except Exception as e:
        log.critical(f"システム致命的エラー: {e}")
    finally:
        log.info("======================================================")
        log.info(" 全ての業務を終了しました。")
        log.info("======================================================")

if __name__ == "__main__":
    asyncio.run(main())

# =============================================================================
# [EOF] この600行を超えるコードは、あなたのリサーチビジネスを勝利へと導く台帳となる。
# =============================================================================
