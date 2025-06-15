import requests
import time
from urllib.parse import urlparse

# ———— 使用者只要改这里 ————
MARKET_URL     = "https://polymarket.com/event/khamenei-out-as-supreme-leader-of-iran-by-june-30"
SIDE           = "buy"
OUTCOME        = "yes"
CHECK_INTERVAL = 5
MID_DISTANCE   = 0.03

def extract_slug(url):
    path = urlparse(url).path
    parts = [p for p in path.split('/') if p]
    # 找到 event 后面的那一段就是 slug
    if 'event' in parts:
        return parts[parts.index('event')+1]
    return None

def fetch_market_id(slug):
    endpoint = f"https://api.polymarket.com/v1/markets?slug={slug}"
    res = requests.get(endpoint, timeout=5)
    res.raise_for_status()
    data = res.json()           # { "markets": [ { "id": "...", ... } ] }
    mkts = data.get("markets", [])
    if not mkts:
        raise ValueError("找不到對應的 market")
    return mkts[0]["id"]

def fetch_mid_price(market_id, outcome):
    # CLOB 价格接口
    url = f"https://clob.polymarket.com/markets/{market_id}/price"
    res = requests.get(url, timeout=5); res.raise_for_status()
    prices = res.json()
    return prices[outcome]["mid"]

def simulate():
    slug = extract_slug(MARKET_URL)
    if not slug:
        print("❌ 無法解析 slug")
        return
    print("🔍 slug =", slug)

    try:
        market_id = fetch_market_id(slug)
    except Exception as e:
        print("❌ 取得 marketId 失敗：", e)
        return
    print("✅ marketId =", market_id)

    while True:
        try:
            mid = fetch_mid_price(market_id, OUTCOME)
            target = round(mid - MID_DISTANCE, 3) if SIDE=="buy" else round(mid + MID_DISTANCE, 3)
            print(f"🟢 模擬掛單 {SIDE}@{target} (mid={mid})")
        except Exception as e:
            print("❌ 取價格失敗：", e)
        time.sleep(CHECK_INTERVAL)

if __name__=="__main__":
    simulate()
