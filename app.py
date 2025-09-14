import streamlit as st
import pandas as pd
from datetime import date, timedelta
import os
import plotly.express as px

# ------------------------------
# ملف حفظ البيانات
# ------------------------------
FILE = "habits.csv"
if os.path.exists(FILE):
    df = pd.read_csv(FILE)
else:
    df = pd.DataFrame(columns=["Date","Habit","Done","Color"])

# ------------------------------
# Streamlit session state
# ------------------------------
if "df" not in st.session_state:
    st.session_state.df = df

# ------------------------------
# إعداد الصفحة
# ------------------------------
st.set_page_config(page_title="Luxury Habit Tracker", layout="wide")
st.markdown("""
    <h1 style='text-align: center; color: #FFD700;'>✨ Luxury Habit Tracker ✨</h1>
""", unsafe_allow_html=True)

# ------------------------------
# إضافة عادة جديدة
# ------------------------------
with st.expander("➕ إضافة عادة جديدة"):
    habit_name = st.text_input("اسم العادة:")
    habit_color = st.selectbox("لون العادة", ["#FFD700", "#800080", "#0A1172", "#4B0082", "#2F4F4F"])
    if st.button("إضافة عادة"):
        new_row = pd.DataFrame({
            "Date":[str(date.today())],
            "Habit":[habit_name],
            "Done":[False],
            "Color":[habit_color]
        })
        st.session_state.df = pd.concat([st.session_state.df,new_row], ignore_index=True)
        st.session_state.df.to_csv(FILE,index=False)
        st.success(f"✅ تم إضافة عادة: {habit_name}")

# ------------------------------
# عرض العادات بشكل شبكي
# ------------------------------
st.subheader(f"🗓️ عادات اليوم ({date.today()})")
today_habits = st.session_state.df[st.session_state.df["Date"]==str(date.today())]

if not today_habits.empty:
    cols = st.columns(3)
    for i, (idx,row) in enumerate(today_habits.iterrows()):
        col = cols[i % 3]
        with col:
            card_bg = row["Color"] if not row["Done"] else "#2E2E2E"
            card_text_color = "#FFFFFF" if row["Done"] else "#000000"
            st.markdown(f"""
                <div style='background-color: {card_bg}; padding: 15px; border-radius: 15px; margin-bottom: 10px; text-align:center;'>
                    <h3 style='color:{card_text_color};'>{row['Habit']}</h3>
                    <input type="checkbox" {"checked" if row["Done"] else ""} onclick="window.dispatchEvent(new Event('streamlit:rerun'));">
                </div>
            """, unsafe_allow_html=True)
            done = st.checkbox("", value=row["Done"], key=f"done{idx}")
            st.session_state.df.at[idx,"Done"]=done
else:
    st.info("لا توجد عادات لليوم.")

# ------------------------------
# ملخص اليوم
# ------------------------------
st.subheader("📊 ملخص اليوم")
completed = today_habits["Done"].sum()
total = len(today_habits)
st.metric("الإنجاز اليومي", f"{completed}/{total} تم ✅" if total>0 else "0/0")

# ------------------------------
# التقدم الأسبوعي
# ------------------------------
st.subheader("📈 التقدم الأسبوعي")
week_start = date.today() - timedelta(days=6)
week_df = st.session_state.df[pd.to_datetime(st.session_state.df["Date"]) >= pd.to_datetime(week_start)]
if not week_df.empty:
    week_summary = week_df.pivot_table(index="Date", columns="Habit", values="Done", fill_value=0)
    fig_week = px.bar(
        week_summary,
        barmode="group",
        title="التقدم الأسبوعي لكل عادة",
        labels={"value":"تم الإنجاز","Date":"التاريخ"},
        color_discrete_sequence=px.colors.sequential.Emrld
    )
    st.plotly_chart(fig_week,use_container_width=True)
else:
    st.info("لا توجد بيانات لهذا الأسبوع.")

# ------------------------------
# التقدم الشهري
# ------------------------------
st.subheader("📊 التقدم الشهري")
month_start = date.today() - timedelta(days=29)
month_df = st.session_state.df[pd.to_datetime(st.session_state.df["Date"]) >= pd.to_datetime(month_start)]
if not month_df.empty:
    month_summary = month_df.pivot_table(index="Date", columns="Habit", values="Done", fill_value=0)
    fig_month = px.bar(
        month_summary,
        barmode="stack",
        title="التقدم الشهري لكل عادة",
        labels={"value":"تم الإنجاز","Date":"التاريخ"},
        color_discrete_sequence=px.colors.sequential.Teal
    )
    st.plotly_chart(fig_month,use_container_width=True)
else:
    st.info("لا توجد بيانات للشهر الحالي.")

# ------------------------------
# تصدير واستيراد البيانات
# ------------------------------
st.subheader("💾 تصدير / استيراد البيانات")
st.download_button("⬇️ تحميل البيانات CSV",st.session_state.df.to_csv(index=False),file_name="habits.csv",mime="text/csv")
uploaded_file = st.file_uploader("⬆️ رفع ملف CSV", type="csv")
if uploaded_file is not None:
    imported_df = pd.read_csv(uploaded_file)
    st.session_state.df = pd.concat([st.session_state.df, imported_df], ignore_index=True)
    st.session_state.df.drop_duplicates(subset=["Date","Habit"], keep="last", inplace=True)
    st.session_state.df.to_csv(FILE,index=False)
    st.success("✅ تم استيراد البيانات بنجاح")
