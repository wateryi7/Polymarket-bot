import requests
import time

# ===== 使用者設定區 =====
MARKET_URL = "https://polymarket.com/event/khamenei-out-as-supreme-leader-of-iran-by-june-30"
SIDE = "buy"  # buy 或 sell
OUTCOME = "yes"
CHECK_INTERVAL = 5  # 每幾秒檢查一次
MID_DISTANCE = 0.03
REPLACE_THRESHOLD = 0.001
MIN_PRICE_ALLOWED = 0.8
MAX_PRICE_ALLOWED = 0.95
SIMULATION_MODE = True

# ===== 解析 slug =====
def extract_slug_from_url(url):
    parts = url.split("/event/")
    if len(parts) > 1:
        slug = parts[1].split("?")[0].strip("/")
        return slug
    return None

# ===== 根據 slug 抓取 market id（從 clob.polymarket.com 的 slug 精確比對） =====
def get_market_id_from_slug(slug):
    try:
        response = requests.get("https://clob.polymarket.com/markets")
        response.raise_for_status()
        raw = response.json()

        print("[DEBUG] API 回傳類型:", type(raw))
        print("[DEBUG] 回傳內容預覽:", str(raw)[:500])

        # ✅ 正確解析資料
        if isinstance(raw, dict) and "data" in raw:
            markets = raw["data"]
            for market in markets:
                if "slug" in market and market["slug"] == slug:
                    return market.get("id")
            print("[❌] 沒有找到對應 slug 的市場（比對 slug）")
        else:
            print("[❌] API 回傳格式錯誤，預期為 dict 且包含 data")
        return None
    except Exception as e:
        print(f"[❌] 查詢 market ID 時失敗: {e}")
        return None


# ===== 擷取中間價（從 orderbook 中計算 mid price） =====
def get_mid_price(market_id, outcome):
    try:
        url = f"https://clob.polymarket.com/markets/{market_id}/orderbook"
        res = requests.get(url)
        res.raise_for_status()
        book = res.json()

        bids = book.get("bids", {}).get(outcome, [])
        asks = book.get("asks", {}).get(outcome, [])

        best_bid = float(bids[0]["price"]) if bids else 0.0
        best_ask = float(asks[0]["price"]) if asks else 1.0

        mid_price = round((best_bid + best_ask) / 2, 4)
        return mid_price
    except Exception as e:
        print(f"[❌] 價格取得失敗: {e}")
        return None

# ===== 模擬掛單函式 =====
def simulate_bot():
    slug = extract_slug_from_url(MARKET_URL)
    if not slug:
        print("[❌] 無法從網址取得 slug")
        return

    print(f"[🔍] 擷取 slug: {slug}")
    market_id = get_market_id_from_slug(slug)
    if not market_id:
        print("[❌] 找不到對應的 marketId")
        return

    print(f"[✅] 取得 Market ID: {market_id}")
    print(f"[🔁] 模擬掛單開始...")

    while True:
        try:
            mid_price = get_mid_price(market_id, OUTCOME)
            if mid_price is None:
                time.sleep(CHECK_INTERVAL)
                continue

            if MIN_PRICE_ALLOWED <= mid_price <= MAX_PRICE_ALLOWED:
                target_price = round(mid_price - MID_DISTANCE, 3) if SIDE == "buy" else round(mid_price + MID_DISTANCE, 3)
                print(f"[🟢] 模擬掛單：{SIDE} {OUTCOME} @ {target_price} USDC")
            else:
                print(f"[⚠️] 當前中間價 {mid_price} 超出允許範圍")
        except Exception as e:
            print(f"[❌] 發生錯誤: {e}")

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    simulate_bot()
