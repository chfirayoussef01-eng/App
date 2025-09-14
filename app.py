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
    df = pd.DataFrame(columns=["Date", "Habit", "Done", "Color"])

# ------------------------------
# إعداد الصفحة
# ------------------------------
st.set_page_config(page_title="Ultimate Habit Tracker", layout="wide")
st.title("📋 Ultimate Daily Habit Tracker")

# ------------------------------
# إضافة عادة جديدة
# ------------------------------
with st.form("add_habit"):
    habit_name = st.text_input("أضف عادة جديدة:")
    habit_color = st.color_picker("اختر لون العادة", "#00FF00")
    submit = st.form_submit_button("➕ إضافة")
    if submit and habit_name:
        df = pd.concat([df, pd.DataFrame({"Date":[str(date.today())], "Habit":[habit_name], "Done":[False], "Color":[habit_color]})], ignore_index=True)
        df.to_csv(FILE, index=False)
        st.success(f"✅ تم إضافة عادة: {habit_name}")

# ------------------------------
# عرض عادات اليوم كبطاقات ديناميكية
# ------------------------------
today_habits = df[df["Date"] == str(date.today())]
st.subheader(f"🗓️ عادات اليوم ({date.today()})")

if not today_habits.empty:
    cols = st.columns(min(4, len(today_habits)))
    for i, (idx, row) in enumerate(today_habits.iterrows()):
        with cols[i % 4]:
            done = st.checkbox(row["Habit"], value=row["Done"], key=idx)
            df.at[idx, "Done"] = done
            bg_color = "#A2FFA2" if done else row["Color"]
            st.markdown(f"<div style='background-color:{bg_color}; padding:10px; border-radius:8px; text-align:center;'>{row['Habit']}</div>", unsafe_allow_html=True)
    df.to_csv(FILE, index=False)
else:
    st.info("لا توجد عادات لليوم. أضف عادة جديدة!")

# ------------------------------
# إشعارات تذكيرية يومية تلقائية
# ------------------------------
st.subheader("🔔 التذكيرات اليومية")
for i, row in today_habits.iterrows():
    if not row["Done"]:
        st.warning(f"⏰ تذكير: لم تُنجز عادة '{row['Habit']}' اليوم! حاول إكمالها الآن.")

# ------------------------------
# ملخص يومي
# ------------------------------
st.subheader("📊 ملخص اليوم")
completed = today_habits["Done"].sum()
total = len(today_habits)
st.metric("الإنجاز اليومي", f"{completed}/{total} تم ✅" if total>0 else "0/0")

# ------------------------------
# إحصائيات الأسبوع
# ------------------------------
st.subheader("📈 تقدم الأسبوع")
week_start = date.today() - timedelta(days=6)
week_df = df[pd.to_datetime(df["Date"]) >= pd.to_datetime(week_start)]
if not week_df.empty:
    week_summary = week_df.pivot_table(index="Date", columns="Habit", values="Done", fill_value=0)
    fig_week = px.bar(week_summary, barmode="group", title="التقدم الأسبوعي لكل عادة", labels={"value":"تم الإنجاز","Date":"التاريخ"})
    st.plotly_chart(fig_week, use_container_width=True)
else:
    st.info("لا توجد بيانات لهذا الأسبوع.")

# ------------------------------
# إحصائيات الشهر
# ------------------------------
st.subheader("📊 تقدم الشهر")
month_start = date.today() - timedelta(days=29)
month_df = df[pd.to_datetime(df["Date"]) >= pd.to_datetime(month_start)]
if not month_df.empty:
    month_summary = month_df.pivot_table(index="Date", columns="Habit", values="Done", fill_value=0)
    fig_month = px.bar(month_summary, barmode="stack", title="التقدم الشهري لكل عادة", labels={"value":"تم الإنجاز","Date":"التاريخ"})
    st.plotly_chart(fig_month, use_container_width=True)
else:
    st.info("لا توجد بيانات للشهر الحالي.")

# ------------------------------
# تصدير واستيراد البيانات
# ------------------------------
st.subheader("💾 تصدير واستيراد البيانات")
st.download_button("⬇️ تحميل البيانات CSV", df.to_csv(index=False), file_name="habits.csv", mime="text/csv")
uploaded_file = st.file_uploader("⬆️ رفع ملف CSV", type="csv")
if uploaded_file is not None:
    imported_df = pd.read_csv(uploaded_file)
    df = pd.concat([df, imported_df], ignore_index=True)
    df.drop_duplicates(subset=["Date","Habit"], keep="last", inplace=True)
    df.to_csv(FILE, index=False)
    st.success("✅ تم استيراد البيانات بنجاح")
    st.experimental_rerun()
