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
# Streamlit session state لتخزين البيانات
# ------------------------------
if "df" not in st.session_state:
    st.session_state.df = df

# ------------------------------
# إعداد الصفحة
# ------------------------------
st.set_page_config(page_title="Professional Habit Tracker", layout="wide")
st.title("📋 Professional Habit Tracker")

# ------------------------------
# إضافة عادة جديدة
# ------------------------------
with st.expander("➕ إضافة عادة جديدة"):
    habit_name = st.text_input("اسم العادة:")
    habit_color = st.color_picker("لون العادة", "#00FF00")
    if st.button("إضافة عادة"):
        new_row = pd.DataFrame({"Date":[str(date.today())],"Habit":[habit_name],"Done":[False],"Color":[habit_color]})
        st.session_state.df = pd.concat([st.session_state.df,new_row], ignore_index=True)
        st.session_state.df.to_csv(FILE,index=False)
        st.success(f"✅ تم إضافة عادة: {habit_name}")

# ------------------------------
# عرض وتعديل وحذف العادات
# ------------------------------
st.subheader(f"🗓️ عادات اليوم ({date.today()})")
today_habits = st.session_state.df[st.session_state.df["Date"]==str(date.today())]

if not today_habits.empty:
    remove_indices = []
    for i, (idx,row) in enumerate(today_habits.iterrows()):
        col1,col2,col3 = st.columns([4,1,1])
        with col1:
            done = st.checkbox(row["Habit"], value=row["Done"], key=f"done{idx}")
            st.session_state.df.at[idx,"Done"]=done
        with col2:
            new_color = st.color_picker("", value=row["Color"], key=f"color{idx}")
            st.session_state.df.at[idx,"Color"]=new_color
        with col3:
            if st.button("❌", key=f"del{idx}"):
                remove_indices.append(idx)
    # حذف الصفوف بعد الحلقة لتجنب rerun داخل الحلقة
    if remove_indices:
        st.session_state.df = st.session_state.df.drop(remove_indices)
        st.session_state.df.to_csv(FILE,index=False)
        st.success("تم حذف العادة بنجاح!")
        st.experimental_rerun()
else:
    st.info("لا توجد عادات لليوم.")

# ------------------------------
# باقي التطبيق يبقى كما هو
# ------------------------------
# تذكيرات يومية
st.subheader("🔔 التذكيرات اليومية")
today_habits = st.session_state.df[st.session_state.df["Date"]==str(date.today())]
for i,row in today_habits.iterrows():
    if not row["Done"]:
        st.warning(f"⏰ تذكير: لم تُنجز عادة '{row['Habit']}' اليوم!")

# ملخص اليوم
st.subheader("📊 ملخص اليوم")
completed = today_habits["Done"].sum()
total = len(today_habits)
st.metric("الإنجاز اليومي", f"{completed}/{total} تم ✅" if total>0 else "0/0")

# إحصائيات الأسبوع والشهر، تصدير واستيراد كما في النسخة السابقة...
