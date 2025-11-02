import time
import hmac
import hashlib
import requests

from flask import Flask
import threading
import os
# ===== إعداد المفاتيح =====
API_KEY = "mx0vglVCmvw86sDJsF"
SECRET_KEY = "6618337a62114be7957593511d52cce5"
# ===== إعداد الاستراتيجية =====
symbol = "LTCUSDT"
BASE_URL = "https://api.mexc.com"
poll_interval = 300  # كل 5 دقائق (300 ثانية)
trade_amount = 1.0   # كل صفقة 1 دولار
profit_targets = [0.5 , 0.7 ,1.0,1.5, 2.0 , 3.0 , 4.0 , 5.0]

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
    print(f"📤 تم إرسال أمر {side}")
    return r.json()
# ===== واجهة ويب بسيطة للحفاظ على عمل Render =====
from flask import Flask
import threading
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Trading bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# تشغيل Flask في خيط منفصل (Thread)
threading.Thread(target=run_flask).start()
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

    except Exception as e:
        print("❌ خطأ:", e)
        time.sleep(5)
# ===== تشغيل خادم صغير حتى يظل البوت شغال على Render =====
from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ البوت شغال على Render بدون توقف!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

