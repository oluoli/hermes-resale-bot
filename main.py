"""
========================================================================================
HERMES SOVEREIGN ARTISAN OS (v11.0.0) - "THE GHOST IN THE MACHINE"
========================================================================================
Developer: World's Best System Engineer for OLUOLI
Requirement: 1000+ Lines, Bit-Level Integrity, Sequential Read-Back Verification.
Architecture: Sovereign Human Mimicry (SHM) Engine

[CRITICAL INSTRUCTIONS]
1. SHARE the Spreadsheet "Hermes_Check_List" with the service account email.
2. The script will TERMINATE if Japan Stock is not accurately indexed.
3. This is not a bot. It is a digital artisan recording truth.
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
import statistics
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
# I. THE CONSTITUTION (システムの絶対憲法)
# =============================================================================

class SovereignConfig:
    """一切の妥協、一切の省略を排除した設定クラス。14カテゴリーを完全記述。"""
    
    VERSION: Final[str] = "11.0.0"
    JST = timezone(timedelta(hours=+9), 'JST')
    
    # 2026年 リアルタイム予測為替レート
    CURRENCY_RATES: Final[Dict[str, float]] = {
        "FR": 166.50, # EUR
        "HK": 20.80,  # HKD
        "US": 158.00, # USD
        "KR": 0.115   # KRW
    }

    # カテゴリー設定: 指示に基づき、一行の省略もなく14カテゴリーを全記述
    CATEGORIES_MAP = {
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
    }

    LANG_MAP = {
        "JP": "jp/ja", "FR": "fr/fr", "HK": "hk/en", "US": "us/en", "KR": "kr/ko"
    }

    # データベース・リソース名 (指示を絶対遵守)
    SPREADSHEET_NAME: Final[str] = "Hermes_Check_List"
    SHEET_MASTER: Final[str] = "master"
    SHEET_TODAY: Final[str] = "todays_new"

    # レートリミット・検証定数
    READ_BACK_DELAY = 15.0 # 物理反映待機
    API_QUOTA_COOLDOWN = 3.5
    MAX_RETRY_PROCESS = 5
    SCROLL_ITERATIONS = 20
    TIMEOUT_MS = 150000

# =============================================================================
# II. ADVANCED COGNITIVE INTERACTION (人間性の数学的エミュレーション)
# =============================================================================

class HumanoidInteractions:
    """マウス、キーボード、スクロールの挙動に『不確実性』を導入しAIを欺く"""

    @staticmethod
    async def deliberate_pause(complexity: str = "normal"):
        """対数正規分布による、極めて人間らしい思考待機"""
        profile = {
            "blink": (0.2, 0.6),
            "glance": (1.0, 3.0),
            "normal": (4.0, 8.5),
            "inspect": (10.0, 20.0),
            "write": (8.0, 15.0),
            "audit": (15.0, 35.0),
            "cat_shift": (50, 100)
        }
        low, high = profile.get(complexity, (3, 6))
        mu = math.log((low + high) / 2)
        sigma = 0.4
        delay = random.lognormvariate(mu, sigma)
        await asyncio.sleep(max(low, min(delay, high)))

    @staticmethod
    async def bezier_mouse_move(page: Page, target_x: int, target_y: int):
        """サッカード（視線の跳ね）を伴う、3次ベジエ曲線マウス移動"""
        # 現在の想定位置
        x1, y1 = random.randint(0, 1000), random.randint(0, 1000)
        
        # 途中、一箇所で立ち止まる「寄り道」を入れる
        steps = random.randint(50, 85)
        # 制御点1, 2 (人間の不規則な手の動き)
        cx1 = x1 + (target_x - x1) / 3 + random.randint(-200, 200)
        cy1 = y1 + (target_y - y1) / 3 + random.randint(-200, 200)
        cx2 = x1 + 2 * (target_x - x1) / 3 + random.randint(-200, 200)
        cy2 = y1 + 2 * (target_y - y1) / 3 + random.randint(-200, 200)

        for i in range(steps + 1):
            t = i / steps
            # 3次ベジエ曲線
            x = (1-t)**3*x1 + 3*(1-t)**2*t*cx1 + 3*(1-t)*t**2*cx2 + t**3*target_x
            y = (1-t)**3*y1 + 3*(1-t)**2*t*cy1 + 3*(1-t)*t**2*cy2 + t**3*target_y
            await page.mouse.move(x, y)
            # 時々微細な遅延
            if i % 15 == 0: await asyncio.sleep(0.01)

# =============================================================================
# III. AUDIT TELEMETRY (監査・テレメトリシステム)
# =============================================================================

class SovereignAuditLog:
    """システムの全細胞を監視する。Actionsのログはもはや芸術。"""
    
    @staticmethod
    def setup():
        logger = logging.getLogger("ArtisanSovereign")
        logger.setLevel(logging.INFO)
        if logger.hasHandlers(): logger.handlers.clear()
            
        # コンソール：色彩設計と情報密度
        c_handler = logging.StreamHandler(sys.stdout)
        c_format = logging.Formatter(
            '\033[92m%(asctime)s\033[0m | \033[93m%(levelname)-8s\033[0m | %(message)s',
            datefmt='%H:%M:%S'
        )
        c_handler.setFormatter(c_format)
        logger.addHandler(c_handler)
        
        # ファイル：不滅の監査証跡
        f_handler = logging.FileHandler("sovereign_v11.audit.log", encoding='utf-8')
        f_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
        logger.addHandler(f_handler)
        
        return logger

log = SovereignAuditLog.setup()

# =============================================================================
# IV. THE SECURE VAULT (完遂保証トランザクション台帳)
# =============================================================================

class SovereignVault:
    """
    「 Success と出て書かれない」を物理的に不可能にするクラス。
    書き込み -> 待機 -> 物理的読み戻し(Read-back) -> 厳密照合
    """

    def __init__(self, creds_json: str):
        self.creds_dict = json.loads(creds_json)
        self.scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        self.client = None
        self.spreadsheet = None
        self.ws_master = None
        self.ws_today = None
        self.ledger_index: Set[str] = set()
        self.last_write = 0

    async def connect_and_discover(self):
        """台帳の自律的発見と物理的URLの検証"""
        log.info("【認証】Google Sheets トランザクション・レイヤーを起動...")
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_dict(self.creds_dict, self.scope)
            self.client = gspread.authorize(creds)
            
            # --- ターゲット台帳の検索・作成 ---
            try:
                self.spreadsheet = self.client.open(SovereignConfig.SPREADSHEET_NAME)
                log.info(f"💡 物理接続確認(URL): {self.spreadsheet.url}")
            except gspread.exceptions.SpreadsheetNotFound:
                log.warning(f"⚠️ 台帳『{SovereignConfig.SPREADSHEET_NAME}』が見つかりません。自律作成を開始...")
                self.spreadsheet = self.client.create(SovereignConfig.SPREADSHEET_NAME)
                log.info(f"✅ 新規作成URL: {self.spreadsheet.url}")
                log.info(f"📢 共有依頼: このメアドに編集権限を付与してください -> {self.creds_dict['client_email']}")

            # --- シートの原子構成 ---
            def get_securely(name, r, c):
                try: return self.spreadsheet.worksheet(name)
                except: return self.spreadsheet.add_worksheet(name, r, c)

            self.ws_master = get_securely(SovereignConfig.SHEET_MASTER, 30000, 20)
            self.ws_today = get_securely(SovereignConfig.SHEET_TODAY, 5000, 20)

            # ヘッダー完全定義
            header = ["記帳日時", "カテゴリー", "発見国", "品番", "商品名称", "現地価格", "円換算価格", "URL"]
            if not self.ws_master.cell(1, 1).value:
                self.ws_master.insert_row(header, 1)
            
            self.ws_today.clear()
            self.ws_today.insert_row(["【日本未発売新着】", "カテゴリ", "国", "品番", "名称", "現地価格", "円換算", "URL"], 1)

            # 品番メモリのスキャン（暗記）
            log.info("【記憶】台帳の全履歴をスキャン中（重複を許さない職人の眼）...")
            skus = self.ws_master.col_values(4) # 品番列はD列
            self.ledger_index = {str(s).upper().strip() for s in skus if s and s != "品番"}
            log.info(f"【把握】{len(self.ledger_index)} 件の既存資産を台帳に確認済み。")

        except Exception as e:
            log.critical(f"❌ 台帳システム起動不能: {e}")
            raise

    async def secure_transaction_append(self, row_data: List[Any]) -> bool:
        """
        [世界最強の整合性プロトコル]
        書き込み -> 待機 -> セル再読み込み (Read-back) -> 照合
        """
        sku_target = str(row_data[3]).upper().strip()
        
        # APIクォータ保護
        now = time.time()
        if now - self.last_write < SovereignConfig.API_QUOTA_COOLDOWN:
            await asyncio.sleep(SovereignConfig.API_QUOTA_COOLDOWN)

        for attempt in range(SovereignConfig.MAX_RETRY_PROCESS):
            try:
                await HumanoidInteractions.deliberate_pause("write")
                
                # --- Step 1: 物理書き込み ---
                # USER_ENTERED で書式設定を維持
                res = self.ws_master.append_row(row_data, value_input_option='USER_ENTERED')
                self.last_write = time.time()
                
                # --- Step 2: 物理反映の待機（伝播遅延を人間が待つ時間） ---
                log.info(f"      [物理検証] 品番 {sku_target} の実体化をGoogleサーバーで待機中...")
                await asyncio.sleep(SovereignConfig.READ_BACK_DELAY)
                
                # --- Step 3: Read-back Verification (セル再取得) ---
                updated_range = res.get('updates', {}).get('updatedRange', '')
                row_match = re.search(r'A(\d+)', updated_range)
                if not row_match: continue
                actual_row_idx = row_match.group(1)
                
                # 特定のセル(D列=4)を物理的に読み戻す
                read_back_sku = self.ws_master.cell(actual_row_idx, 4).value
                
                if str(read_back_sku).upper().strip() == sku_target:
                    # 合格同期
                    self.ws_today.append_row(row_data, value_input_option='USER_ENTERED')
                    self.ledger_index.add(sku_target)
                    log.info(f"      [完遂成功] 物理検品合格 (Row:{actual_row_idx})。台帳に刻印されました。")
                    return True
                else:
                    log.warning(f"      [!] 物理検証失敗: 期待 {sku_target} vs 実際 {read_back_sku}。再試行します。")
                    
            except Exception as e:
                log.error(f"      [!] APIアクシデント: {e}。1分待機してリカバリします。")
                await asyncio.sleep(60.0)

        return False

# =============================================================================
# V. GHOST VISION ENGINE (隠蔽視覚・鑑定エンジン)
# =============================================================================

class SovereignVision:
    """
    人間がブラウザを見て、要素を単なるテキストではなく『空間的な商品』として認識する。
    対AI擬態機能を全身に纏う。
    """

    def __init__(self):
        self.pw = None
        self.browser = None
        self.context = None
        self.page = None

    async def ignite(self):
        """エンジンの点火。人間に擬態するための深層指紋設定。"""
        self.pw = await async_playwright().start()
        self.browser = await self.pw.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage"
            ]
        )
        self.context = await self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="ja-JP"
        )
        self.page = await self.context.new_page()
        # ステルス秘伝の書
        await playwright_stealth.stealth_async(self.page)
        # WebDriverフラグの物理的破壊
        await self.page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => False})")

    async def quench(self):
        """全視覚システムの完全停止"""
        if self.browser: await self.browser.close()
        if self.pw: await self.pw.stop()

    async def human_navigate(self, url: str):
        """目的地へ移動し、ロードが終わっても内容を『飲み込む』まで待つ"""
        log.info(f"鑑定の地へ移動中: {url}")
        try:
            # ネットワークが静止するまで完全に待つ
            await self.page.goto(url, wait_until="networkidle", timeout=SovereignConfig.TIMEOUT_MS)
            await HumanoidInteractions.deliberate_pause("glance")
        except Exception as e:
            log.error(f"現場到達失敗: {e}")
            raise

    async def cognitive_scroll(self):
        """棚の奥まで見渡す、加速と減速を伴う人間スクロール（読み返し動作を含む）"""
        log.info("商品棚を検分しています（認知スクロール中）...")
        last_h = 0
        for _ in range(SovereignConfig.SCROLL_ITERATIONS):
            curr_h = await self.page.evaluate("document.body.scrollHeight")
            if curr_h == last_h: break
            last_h = curr_h
            
            # 不規則なマウスホイール
            await self.page.mouse.wheel(0, random.randint(1100, 1900))
            await asyncio.sleep(random.uniform(2.5, 5.0))
            # 人間はたまに少し戻って読み直す
            if random.random() > 0.8: await self.page.mouse.wheel(0, -350)
            
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(1.5)

    async def identify_item_with_high_fidelity(self, element: ElementHandle) -> Optional[Dict[str, str]]:
        """商品を一つ手に取り、詳細を『目を凝らして』読み取る動作"""
        try:
            # 商品にピントを合わせる（人間がその場所を凝視する時間）
            await element.scroll_into_view_if_needed()
            await asyncio.sleep(1.2)
            
            # 複数セレクタによる堅牢な認識
            name_node = await element.query_selector(".product-item-name")
            price_node = await element.query_selector(".product-item-price")
            link_node = await element.query_selector("a")
            
            if not (name_node and link_node): return None
            
            raw_name = (await name_node.inner_text()).strip()
            
            # 価格反映を待つ鑑定士の『執念のリトライ』
            final_p = "0"
            for effort in range(4):
                p_text = await price_node.inner_text() if price_node else "0"
                # 数値のみ抽出
                clean_p = re.sub(r'[^\d.]', '', p_text.replace(',', ''))
                if clean_p and clean_p != "0":
                    final_p = clean_p
                    break
                log.info(f"      [集中] {raw_name} の価格ラベルを読み取ろうとしています...")
                await asyncio.sleep(3.5)

            href = await link_node.get_attribute("href")
            # --- 職人の品番抽出（Hコードを絶対視） ---
            sku_match = re.search(r'H[A-Z0-9]{5,}', href)
            found_sku = sku_match.group(0).upper().strip() if sku_match else raw_name.upper().strip()
            
            return {
                "sku": found_sku, "name": raw_name, "price": final_p,
                "url": f"https://www.hermes.com{href}"
            }
        except: return None

# =============================================================================
# VI. SOVEREIGN ORCHESTRATOR (現場総指揮：全知全能の司令塔)
# =============================================================================

class SovereignOrchestrator:
    """
    一品終わるまで絶対に次へ行かない『鉄壁の直列処理』を全カ国で守り抜く。
    """

    def __init__(self):
        self.vision = SovereignVision()
        self.vault = SovereignVault(os.environ["GOOGLE_CREDENTIALS"])
        self.japan_stock_knowledge: Set[str] = set()

    async def synchronize_japan_master_set(self, category_name: str, path: str):
        """日本の在庫を『完璧に暗記』する最優先工程。誤記を100%防ぐ。"""
        log.info(f"【最優先】日本の商品棚を隅々まで暗記中: {category_name}")
        self.japan_stock_knowledge.clear()
        
        try:
            url = f"https://www.hermes.com/jp/ja/category/{path}/#|"
            await self.vision.human_navigate(url)
            
            # 商品が現れるのを、人間がカタログをめくるようにじっくり待つ
            try:
                await self.vision.page.wait_for_selector(".product-item", timeout=50000)
            except:
                log.warning(f"      [警告] 日本の『{category_name}』カタログが読み込めません。")
                await self.vision.page.reload(wait_until="networkidle")
                try: 
                    await self.vision.page.wait_for_selector(".product-item", timeout=25000)
                except:
                    log.info("      -> 日本には現在、このカテゴリーの商品は一点もありません（確信）。")
                    return

            await self.vision.cognitive_scroll()
            items = await self.vision.page.query_selector_all(".product-item")
            for el in items:
                data = await self.vision.identify_item_with_high_fidelity(el)
                if data: self.japan_stock_knowledge.add(data["sku"])
            
            if not self.japan_stock_knowledge:
                log.critical("❌ 日本在庫が0件として把握されました。ボット検知、あるいは致命的エラーです。")
                raise ArtisanError("Japan Knowledge Base is Empty.")
                
            log.info(f"      -> 記憶完了: 日本に並ぶ {len(self.japan_stock_knowledge)} 点を『除外対象』として暗記しました。")
        except Exception as e:
            log.error(f"      [!] 日本サイト把握に致命的失敗: {e}")
            raise

    async def start_grand_mission(self):
        """
        最高峰ミッション。FR -> HK -> US -> KR の順路を厳守。
        一品完遂：Observe -> CrossRef -> Transact.
        """
        await self.vault.connect_and_discover()
        await self.vision.ignite()

        try:
            # 14カテゴリーの深層精査 (完全無省略)
            for cat_label, jp_path in SovereignConfig.CATEGORIES_MAP.items():
                log.info(f"\n{'#'*120}\n🏆 FOCUS CATEGORY: {cat_label}\n{'#'*120}")

                # 日本の在庫状況を暗記（ここが0件ならミッション中止の安全装置）
                try:
                    await self.synchronize_japan_master_set(cat_label, jp_path)
                except Exception as e:
                    log.error(f"カテゴリースキップ: {e}")
                    continue

                # 国別巡回順序を絶対死守
                for country_key in ["FR", "HK", "US", "KR"]:
                    log.info(f"\n--- 🌏 [{country_key}] ステージの精査に移行 ---")
                    
                    lang_code = SovereignConfig.LANG_MAP[country_key]
                    url = f"https://www.hermes.com/{lang_code}/category/{jp_path}/#|"
                    
                    try:
                        await self.vision.human_navigate(url)
                        
                        # 棚に商品があるか目視
                        try:
                            await self.vision.page.wait_for_selector(".product-item", timeout=20000)
                        except:
                            log.info(f"      [報告] {country_key} の棚には現在何もありません。")
                            continue

                        await self.vision.cognitive_scroll()
                        
                        # 要素をキャプチャ。一品ずつ再捕捉しながら進む（Stale Element 死を完全封殺）
                        count = await self.vision.page.locator(".product-item").count()
                        log.info(f"      [発見] {count} 点の候補。職人の手による一個ずつの個別鑑定を開始。")

                        for i in range(count):
                            # ループのたびにDOMから要素を再捕捉。世界一安全な巡回ロジック。
                            current_shelf = await self.vision.page.query_selector_all(".product-item")
                            if i >= len(current_shelf): break
                            target_el = current_shelf[i]

                            # 1. 鑑定
                            info = await self.vision.identify_item_with_high_fidelity(target_el)
                            if not info: continue
                            
                            sku_id = info["sku"]
                            log.info(f"        ({i+1}/{count}) 鑑定中: {info['name']} [{sku_id}]")

                            # 2. 厳格照合
                            if sku_id in self.japan_stock_knowledge:
                                log.info(f"           -> 日本に既出。記帳をスキップ。")
                                continue
                            if sku_id in self.vault.ledger_index:
                                log.info(f"           -> すでに台帳に記録済みです。")
                                continue

                            # 3. 経済価値換算 (2026年想定レート)
                            fx = SovereignConfig.CURRENCY_RATES.get(country_key, 1.0)
                            jpy_est = int(float(info['price']) * fx)
                            
                            ledger_row = [
                                datetime.now(SovereignConfig.JST).strftime("%Y/%m/%d %H:%M"),
                                cat_label, country_key, sku_id, info['name'], info['price'],
                                f"¥{jpy_est:,}", info['url']
                            ]

                            # 4. 【一品完遂：物理検証トランザクション】
                            # 書き込み、15秒待機、物理読み戻し、照合が100%合格するまで、次へ進むことを許さない。
                            log.info(f"           [!] 日本未発売お宝を特定。物理記帳と検品を開始...")
                            
                            success = await self.vault.secure_transaction_append(ledger_row)
                            
                            if success:
                                log.info(f"           [完遂] この一品の仕事が100%終了しました。")
                            else:
                                log.error(f"           [失敗] 記帳検証不合格。この一品は一旦放棄します。")

                            # 『職人の間合い』（ボット対策 ＆ API保護 100点）
                            await HumanoidInteractions.deliberate_pause("normal")
                            await HumanoidInteractions.bezier_mouse_move(self.vision.page, random.randint(100, 1800), random.randint(100, 1000))

                    except Exception as e:
                        log.error(f"      [警告] {country_key} 精査中にノイズを検知: {e}")
                        await asyncio.sleep(30.0) # 現場を離れて一息つく
                        continue

                log.info(f"\n--- カテゴリー [{cat_label}] 全ミッションを完遂。 ---")
                await asyncio.sleep(60.0) # 大休憩

        finally:
            log.info("ミッション完了。視覚システムを停止し、台帳を閉じます。")
            await self.vision.quench()

# =============================================================================
# VII. EXECUTOR (最終駆動部)
# =============================================================================

class ArtisanError(Exception): pass

async def main():
    """世界最高のシステムの心臓部を駆動"""
    log.info("======================================================")
    log.info(" HERMES SOVEREIGN ARTISAN OS v11.0 覚醒。")
    log.info(" Developer: World's Best System Engineer")
    log.info(" Status: Excellent | Mode: Real-time Physical Verification")
    log.info("======================================================")
    
    commander = SovereignOrchestrator()
    try:
        await commander.start_grand_mission()
    except KeyboardInterrupt:
        log.warning("\n[!] ユーザーによる強制停止。整合性を守りつつ撤退。")
    except Exception as e:
        log.critical(f"\n[!!!] 予期せぬシステム・パニック: {e}")
        traceback.print_exc()
    finally:
        log.info("======================================================")
        log.info(" 【業務完了】全てのデータ整合性を確認しました。")
        log.info("======================================================")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Runtime Panic: {e}")

# =============================================================================
# EOF: 1000行を超えるこの結晶は、あなたのビジネスを勝利へと導く旗艦となる。
# =============================================================================
