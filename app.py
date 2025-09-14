import streamlit as st
import pandas as pd
import requests
import datetime

# -------------------------------
# إعداد الصفحة
# -------------------------------
st.set_page_config(
    page_title="ICT/SMC + Candlestick Signals",
    page_icon="📊",
    layout="wide"
)

# -------------------------------
# جلب بيانات Binance
# -------------------------------
BINANCE_API = "https://api.binance.com/api/v3/klines"

def get_binance_data(symbol="BTCUSDT", interval="5m", limit=200):
    url = f"{BINANCE_API}?symbol={symbol}&interval={interval}&limit={limit}"
    data = requests.get(url).json()
    df = pd.DataFrame(data, columns=[
        "time","open","high","low","close","volume",
        "close_time","qav","num_trades","taker_base_vol","taker_quote_vol","ignore"
    ])
    df["time"] = pd.to_datetime(df["time"], unit="ms")
    df = df.astype({"open": float, "high": float, "low": float, "close": float, "volume": float})
    return df

# -------------------------------
# خوارزميات الكشف ICT/SMC
# -------------------------------
def detect_liquidity_grab(df):
    signals = []
    for i in range(2, len(df)):
        if df["high"][i] > df["high"][i-1] and df["close"][i] < df["high"][i-1]:
            signals.append({"type": "Liquidity Grab (High)", "direction": "SELL", "price": df['close'][i]})
        if df["low"][i] < df["low"][i-1] and df["close"][i] > df["low"][i-1]:
            signals.append({"type": "Liquidity Grab (Low)", "direction": "BUY", "price": df['close'][i]})
    return signals

def detect_order_blocks(df):
    signals = []
    for i in range(2, len(df)):
        if df["close"][i] > df["open"][i] and df["close"][i] > df["high"][i-1]:
            signals.append({"type": "Bullish Order Block", "direction": "BUY", "price": df['close'][i]})
        if df["close"][i] < df["open"][i] and df["close"][i] < df["low"][i-1]:
            signals.append({"type": "Bearish Order Block", "direction": "SELL", "price": df['close'][i]})
    return signals

def detect_breaker_blocks(df):
    signals = []
    for i in range(3, len(df)):
        if df["close"][i] > df["high"][i-2] and df["close"][i-2] < df["open"][i-2]:
            signals.append({"type": "Bullish Breaker Block", "direction": "BUY", "price": df['close'][i]})
        if df["close"][i] < df["low"][i-2] and df["close"][i-2] > df["open"][i-2]:
            signals.append({"type": "Bearish Breaker Block", "direction": "SELL", "price": df['close'][i]})
    return signals

def detect_mss(df):
    signals = []
    for i in range(2, len(df)):
        if df["close"][i] > df["high"][i-2]:
            signals.append({"type": "MSS (Bullish)", "direction": "BUY", "price": df['close'][i]})
        elif df["close"][i] < df["low"][i-2]:
            signals.append({"type": "MSS (Bearish)", "direction": "SELL", "price": df['close'][i]})
    return signals

# -------------------------------
# خوارزميات الشموع اليابانية
# -------------------------------
def detect_candlestick_patterns(df):
    signals = []
    for i in range(1, len(df)):
        o, h, l, c = df["open"][i], df["high"][i], df["low"][i], df["close"][i]

        # Engulfing
        if c > o and df["close"][i-1] < df["open"][i-1] and c > df["open"][i-1]:
            signals.append({"type": "Bullish Engulfing", "direction": "BUY", "price": c})
        elif c < o and df["close"][i-1] > df["open"][i-1] and c < df["open"][i-1]:
            signals.append({"type": "Bearish Engulfing", "direction": "SELL", "price": c})

        # Pin Bar
        body = abs(c - o)
        candle = h - l
        upper_wick = h - max(c, o)
        lower_wick = min(c, o) - l
        if upper_wick > 2 * body and upper_wick > 2 * lower_wick:
            signals.append({"type": "Bearish Pin Bar", "direction": "SELL", "price": c})
        elif lower_wick > 2 * body and lower_wick > 2 * upper_wick:
            signals.append({"type": "Bullish Pin Bar", "direction": "BUY", "price": c})

        # Doji
        if abs(c - o) <= (0.1 * (h - l)):
            signals.append({"type": "Doji", "direction": "NEUTRAL", "price": c})

        # Inside Bar
        if h < df["high"][i-1] and l > df["low"][i-1]:
            signals.append({"type": "Inside Bar", "direction": "NEUTRAL", "price": c})

    return signals

# -------------------------------
# التطبيق
# -------------------------------
st.title("📊 ICT/SMC + Candlestick Signals Dashboard")

# اختيار الزوج والفريم
col1, col2 = st.columns(2)
with col1:
    symbol = st.selectbox("اختر زوج التداول:", ["BTCUSDT", "ETHUSDT", "BNBUSDT", "XRPUSDT", "SOLUSDT"])
with col2:
    interval = st.selectbox("اختر الفريم الزمني:", ["1m","5m","15m","1h","4h","1d"])

# TradingView
st.subheader(f"Live Chart: {symbol} ({interval})")
tradingview_embed = f"""
<iframe src="https://www.tradingview.com/widgetembed/?frameElementId=tradingview_chart&symbol=BINANCE:{symbol}&interval={interval}&hidesidetoolbar=1&theme=dark&style=1&timezone=Etc/UTC" 
width="100%" height="500" frameborder="0" allowtransparency="true" scrolling="no"></iframe>
"""
st.components.v1.html(tradingview_embed, height=500)

# بيانات
df = get_binance_data(symbol=symbol, interval=interval)
latest_price = df["close"].iloc[-1]
latest_vol = df["volume"].iloc[-1]

c1, c2 = st.columns(2)
c1.metric(f"{symbol} Price", f"{latest_price:.2f} $")
c2.metric("Volume", f"{latest_vol:.2f}")

# إشارات نشطة
st.subheader("🔔 Active Signals (Today Only)")
today = datetime.datetime.utcnow().date()

signals = (
    detect_liquidity_grab(df) +
    detect_order_blocks(df) +
    detect_breaker_blocks(df) +
    detect_mss(df) +
    detect_candlestick_patterns(df)
)

active_signals = [s for s in signals if df["time"].iloc[-1].date() == today]

if active_signals:
    for sig in active_signals:
        color = "green" if sig["direction"] == "BUY" else ("red" if sig["direction"] == "SELL" else "orange")
        st.markdown(f"<span style='color:{color};font-weight:bold'>[{sig['direction']}] {sig['type']} @ {sig['price']:.2f}$</span>", unsafe_allow_html=True)
else:
    st.info("لا توجد إشارات نشطة اليوم.")

# صفقات مستقبلية
st.subheader("📅 Pending Trades")
pending = [
    {"type": "BUY Limit", "entry": latest_price * 0.98, "sl": latest_price * 0.95, "tp": latest_price * 1.03, "time": today},
    {"type": "SELL Limit", "entry": latest_price * 1.02, "sl": latest_price * 1.05, "tp": latest_price * 0.97, "time": today}
]
st.table(pd.DataFrame(pending))

# تحديث تلقائي
st.experimental_autorefresh(interval=5*60*1000, key="datarefresh")