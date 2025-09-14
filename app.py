import streamlit as st
import pandas as pd
import requests
import plotly.graph_objs as go
from datetime import datetime

# ------------------------------
# جلب البيانات من CoinGecko
# ------------------------------
def get_coingecko_data(symbol="bitcoin", vs="usd", days="1", interval="minute"):
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{symbol}/market_chart?vs_currency={vs}&days={days}&interval={interval}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "prices" not in data:
            return pd.DataFrame()

        df = pd.DataFrame(data["prices"], columns=["time", "price"])
        df["time"] = pd.to_datetime(df["time"], unit="ms")
        return df
    except Exception as e:
        st.error(f"❌ خطأ في جلب البيانات: {e}")
        return pd.DataFrame()

# ------------------------------
# توليد إشارات مبسطة (ICT + Candlestick)
# ------------------------------
def generate_signals(df):
    signals = []
    if df.empty: 
        return signals

    # شمعة آخر 5 دقايق
    last_price = df["price"].iloc[-1]
    prev_price = df["price"].iloc[-2]

    # مثال مبسط: إذا السعر اخترق قمة
    if last_price > prev_price * 1.002:
        signals.append({"type": "BUY", "entry": last_price, "sl": last_price*0.99, "tp": last_price*1.01})

    # إذا السعر كسر قاع
    elif last_price < prev_price * 0.998:
        signals.append({"type": "SELL", "entry": last_price, "sl": last_price*1.01, "tp": last_price*0.99})

    return signals

# ------------------------------
# إعدادات Streamlit
# ------------------------------
st.set_page_config(page_title="BTC Scalping App", layout="wide")
st.sidebar.title("📌 Navigation")
page = st.sidebar.radio("انتقل إلى:", ["📊 Dashboard", "🔥 Active Trades", "⏳ Pending Trades", "📜 Historique"])

# ------------------------------
# قاعدة بيانات مؤقتة في Session
# ------------------------------
if "active_trades" not in st.session_state:
    st.session_state.active_trades = []
if "pending_trades" not in st.session_state:
    st.session_state.pending_trades = []
if "historique" not in st.session_state:
    st.session_state.historique = []

# ------------------------------
# 📊 الصفحة الرئيسية (Dashboard)
# ------------------------------
if page == "📊 Dashboard":
    st.title("📊 BTC Scalping Dashboard (CoinGecko)")

    df = get_coingecko_data("bitcoin", "usd", days="1", interval="minute")

    if df.empty:
        st.warning("⚠️ لم يتم العثور على بيانات حالياً.")
    else:
        latest_price = df["price"].iloc[-1]
        st.metric("💰 آخر سعر", f"{latest_price:.2f} USD")

        # رسم الشارت
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["time"], y=df["price"], mode="lines", name="BTC/USD"))

        fig.update_layout(height=500, title="BTC/USD (CoinGecko) - 1m", yaxis_title="Price (USD)")
        st.plotly_chart(fig, use_container_width=True)

        # توليد إشارات
        signals = generate_signals(df)
        st.subheader("📌 إشارات اليوم")
        if signals:
            for sig in signals:
                st.success(f"{sig['type']} @ {sig['entry']:.2f} | SL: {sig['sl']:.2f} | TP: {sig['tp']:.2f}")
                # إضافة للصفقات النشطة
                st.session_state.active_trades.append(sig)
        else:
            st.info("لا توجد إشارات قوية الآن.")

# ------------------------------
# 🔥 الصفقات النشطة
# ------------------------------
elif page == "🔥 Active Trades":
    st.title("🔥 الصفقات النشطة")
    if st.session_state.active_trades:
        st.table(st.session_state.active_trades)
    else:
        st.info("لا توجد صفقات نشطة.")

    # إغلاق الصفقات يدوياً
    if st.button("📌 إغلاق كل الصفقات"):
        for trade in st.session_state.active_trades:
            result = {
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "type": trade["type"],
                "entry": trade["entry"],
                "sl": trade["sl"],
                "tp": trade["tp"],
                "result": "Closed"
            }
            st.session_state.historique.append(result)
        st.session_state.active_trades = []
        st.success("✅ تم إغلاق جميع الصفقات ونقلها للهستوريك")

# ------------------------------
# ⏳ الأوامر المعلقة
# ------------------------------
elif page == "⏳ Pending Trades":
    st.title("⏳ الأوامر المعلقة")
    if st.session_state.pending_trades:
        st.table(st.session_state.pending_trades)
    else:
        st.info("لا توجد أوامر معلقة.")

    # إضافة أمر يدوي
    with st.form("add_pending"):
        entry = st.number_input("سعر الدخول", min_value=0.0, step=0.1)
        sl = st.number_input("وقف الخسارة (SL)", min_value=0.0, step=0.1)
        tp = st.number_input("جني الأرباح (TP)", min_value=0.0, step=0.1)
        side = st.selectbox("الاتجاه", ["BUY", "SELL"])
        submit = st.form_submit_button("➕ إضافة أمر")

        if submit:
            order = {"type": side, "entry": entry, "sl": sl, "tp": tp}
            st.session_state.pending_trades.append(order)
            st.success("✅ تم إضافة الأمر المعلق.")

# ------------------------------
# 📜 صفحة الهستوريك
# ------------------------------
elif page == "📜 Historique":
    st.title("📜 سجل الصفقات (Historique)")
    if st.session_state.historique:
        st.table(st.session_state.historique)
    else:
        st.info("لا يوجد سجل صفقات حتى الآن.")
