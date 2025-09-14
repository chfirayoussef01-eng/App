import streamlit as st
import pandas as pd
import requests
import plotly.graph_objs as go
from datetime import datetime

# ------------------------------
# جلب البيانات من Binance
# ------------------------------
def get_binance_data(symbol="BTCUSDT", interval="5m", limit=200):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if not data or len(data) == 0:
            return pd.DataFrame()  # إرجاع DataFrame فارغ

        df = pd.DataFrame(data, columns=[
            "time", "open", "high", "low", "close", "volume",
            "close_time", "quote_asset_volume", "trades",
            "taker_base", "taker_quote", "ignore"
        ])
        df["time"] = pd.to_datetime(df["time"], unit="ms")
        df["open"] = df["open"].astype(float)
        df["high"] = df["high"].astype(float)
        df["low"] = df["low"].astype(float)
        df["close"] = df["close"].astype(float)
        df["volume"] = df["volume"].astype(float)
        return df
    except Exception as e:
        st.error(f"❌ خطأ في جلب البيانات: {e}")
        return pd.DataFrame()

# ------------------------------
# واجهة التطبيق
# ------------------------------
st.set_page_config(page_title="BTC Scalping App", layout="wide")

st.title("📈 BTC Scalping Dashboard")

# جلب البيانات
df = get_binance_data("BTCUSDT", interval="5m", limit=200)

if df is None or df.empty:
    st.warning("⚠️ لم يتم العثور على بيانات حالياً. أعد المحاولة بعد قليل.")
else:
    latest_price = df["close"].iloc[-1]
    st.metric("💰 آخر سعر", f"{latest_price:.2f} USDT")

    # رسم الشارت
    fig = go.Figure(data=[go.Candlestick(
        x=df["time"],
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        name="BTC/USDT"
    )])

    fig.update_layout(
        xaxis_rangeslider_visible=False,
        height=500,
        title="BTC/USDT 5m",
        yaxis_title="Price (USDT)"
    )

    st.plotly_chart(fig, use_container_width=True)

    # قسم الصفقات (مثال بسيط مبدئي)
    st.subheader("📊 الصفقات النشطة (Active Trades)")
    if "trades" not in st.session_state:
        st.session_state["trades"] = []

    if st.button("➕ إضافة صفقة تجريبية"):
        trade = {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": "BUY",
            "entry": latest_price,
            "sl": latest_price * 0.99,
            "tp": latest_price * 1.01
        }
        st.session_state["trades"].append(trade)

    if st.session_state["trades"]:
        st.table(st.session_state["trades"])
    else:
        st.info("لا توجد صفقات حالياً ✅")
