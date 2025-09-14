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
# عرض وتعديل وحذف العادات بدون rerun
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
    # حذف الصفوف مباشرة بدون rerun
    if remove_indices:
        st.session_state.df = st.session_state.df.drop(remove_indices)
        st.session_state.df.to_csv(FILE,index=False)
        st.success("تم حذف العادة بنجاح!")
else:
    st.info("لا توجد عادات لليوم.")

# ------------------------------
# تذكيرات يومية
# ------------------------------
st.subheader("🔔 التذكيرات اليومية")
today_habits = st.session_state.df[st.session_state.df["Date"]==str(date.today())]
for i,row in today_habits.iterrows():
    if not row["Done"]:
        st.warning(f"⏰ تذكير: لم تُنجز عادة '{row['Habit']}' اليوم!")

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
        labels={"value":"تم الإنجاز","Date":"التاريخ"}
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
        labels={"value":"تم الإنجاز","Date":"التاريخ"}
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
