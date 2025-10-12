import time
import hmac
import hashlib
import requests

from flask import Flask
import threading

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host="0.0.0.0", port=10000)

def keep_alive():
    t = threading.Thread(target=run)
    t.start()

keep_alive()  # ← استدعِها قبل بدء البوت
# ===== إعداد المفاتيح =====
API_KEY = "mx0vglcybDNzKBdv3Y"
SECRET_KEY = "2d198ab42cab41318cef277858e8571f"

# ===== إعداد الاستراتيجية =====
symbol = "LTCUSDT"
BASE_URL = "https://api.mexc.com"
poll_interval = 600  # كل 10 دقائق (600 ثانية)
trade_amount = 1.0   # كل صفقة 1 دولار
profit_targets = [0.5, 1.0, 2.0]

# ===== دوال مساعدة =====
def get_price(sym):
    url = f"{BASE_URL}/api/v3/ticker/price?symbol={sym}"
    r = requests.get(url)
    return float(r.json()["price"])

def sign(params):
    qs = "&".join([f"{k}={params[k]}" for k in params])
    return hmac.new(SECRET_KEY.encode(), qs.encode(), hashlib.sha256).hexdigest()

def place_order(side, sym, **kwargs):
    endpoint = "/api/v3/order"
    ts = int(time.time() * 1000)
    params = {"symbol": sym, "side": side, "timestamp": ts}
    params.update(kwargs)
    params["signature"] = sign(params)
    headers = {"X-MEXC-APIKEY": API_KEY}
    r = requests.post(BASE_URL + endpoint, headers=headers, params=params)
    data = r.json()

    # تحقق من الرد إذا فيه خطأ
    if "msg" in data:
        print(f"⚠️ فشل أمر {side}: {data['msg']}")
    else:
        print(f"📤 تم إرسال أمر {side} بنجاح")

    return data

# ===== المنطق الرئيسي =====
print(f"🚀 بدء تشغيل البوت على {symbol} (كل 5 دقائق 5 صفقات × 1 USDT)")

while True:
    try:
        current_price = get_price(symbol)
        print(f"\n🕒 {time.strftime('%Y-%m-%d %H:%M:%S')} | 💰 السعر الحالي: {current_price}")

        for idx, profit in enumerate(profit_targets, start=1):
            qty = round(trade_amount / current_price, 4)
            buy_resp = place_order("BUY", symbol, type="MARKET", quantity=str(qty))
            print(f"✅ تم الشراء #{idx} بسعر تقريبي: {current_price}")

            sell_price = round(current_price * (1 + profit / 100), 4)
            print(f"🎯 الصفقة #{idx}: هدف البيع عند {sell_price} (+{profit}%)")

            # إنشاء أمر بيع محدد
            place_order("SELL", symbol, type="LIMIT", quantity=str(qty),
                        price=str(sell_price), timeInForce="GTC")

        print("⏳ انتظار 5 دقائق قبل الصفقات القادمة...\n")
        time.sleep(poll_interval)
print(f"⏰ انتهى الانتظار - الوقت الحالي: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    except Exception as e:
        print("❌ خطأ:", e)
        time.sleep(5)
