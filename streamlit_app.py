import streamlit as st
import sqlite3
import math
import os
from datetime import datetime, date
from streamlit_js_eval import get_geolocation
import pandas as pd

# --- إعدادات الواجهة ---
st.set_page_config(page_title="AI Doctor Local", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .custom-card {
        padding: 20px; border-radius: 15px;
        background-color: #ffffff; border: 1px solid #d1d9e6;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 20px;
    }
    .stButton>button {
        background-color: #89CFF0; color: white; border-radius: 10px; width: 100%;
    }
    h1, h2 { color: #6c757d; }
    </style>
    """, unsafe_allow_html=True)

# --- إدارة قاعدة البيانات ---
DB_NAME = "local_medical.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS doctors (id INTEGER PRIMARY KEY, name TEXT, specialty TEXT, area TEXT, lat REAL, lon REAL)")
    c.execute("CREATE TABLE IF NOT EXISTS appointments (id INTEGER PRIMARY KEY, username TEXT, doctor_name TEXT, date TEXT, time TEXT)")
    
    c.execute("SELECT COUNT(*) FROM doctors")
    if c.fetchone()[0] == 0:
        docs = [
            (1, "د. علي الركابي", "قلب وباطنية", "المنصور", 33.3128, 44.3615),
            (2, "د. سارة الحسني", "جلدية", "الكرادة", 33.3020, 44.4210),
            (3, "د. ليث السامرائي", "طوارئ وعام", "الجادرية", 33.2750, 44.3750)
        ]
        c.executemany("INSERT INTO doctors VALUES (?,?,?,?,?,?)", docs)
    conn.commit()
    conn.close()

init_db()

# --- حساب المسافة ---
def calculate_dist(lat1, lon1, lat2, lon2):
    R = 6371
    dlat, dlon = math.radians(lat2-lat1), math.radians(lon2-lon1)
    a = math.sin(dlat/2)*2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)*2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

# --- التحكم في الجلسة ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False

# --- الواجهة الجانبية ---
with st.sidebar:
    st.markdown("<h2 style='color: #89CFF0;'>🩺 AI Doctor</h2>", unsafe_allow_html=True)
    if st.session_state.logged_in:
        choice = st.radio("القائمة:", ["التشخيص الذكي", "مواعيدي", "خروج"])
    else:
        choice = st.radio("البوابة:", ["تسجيل دخول", "إنشاء حساب"])

# --- صفحة الدخول ---
if choice == "تسجيل دخول":
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    u = st.text_input("اسم المستخدم")
    p = st.text_input("الرمز", type="password")
    if st.button("دخول"):
        conn = sqlite3.connect(DB_NAME)
        res = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (u, p)).fetchone()
        conn.close()
        if res:
            st.session_state.logged_in = True
            st.session_state.user_name = u
            st.rerun()
        else: st.error("بيانات خاطئة")
    st.markdown('</div>', unsafe_allow_html=True)

# --- صفحة التشخيص الذكي والـ GPS ---
elif choice == "التشخيص الذكي" and st.session_state.logged_in:
    st.title("🔍 التشخيص وترشيح الأطباء")
    syms = st.multiselect("بماذا تشعر؟", ["ألم صدر", "ضيق تنفس", "طفح جلدي", "حمى"])
    
    if st.button("تحليل وحساب الأقرب"):
        spec = "طوارئ وعام"
        if any(s in syms for s in ["ألم صدر", "ضيق تنفس"]): spec = "قلب وباطنية"
        elif "طفح جلدي" in syms: spec = "جلدية"
        
        st.info(f"التخصص المرشح: {spec}")
        
        # جلب الموقع
        loc = get_geolocation()
        if loc:
            u_lat, u_lon = loc['coords']['latitude'], loc['coords']['longitude']
            conn = sqlite3.connect(DB_NAME)
            all_docs = conn.execute("SELECT * FROM doctors WHERE specialty=?", (spec,)).fetchall()
            conn.close()
            
            # ترتيب حسب المسافة
            results = sorted([(d, calculate_dist(u_lat, u_lon, d[4], d[5])) for d in all_docs], key=lambda x: x[1])
            
            for d_info, d_dist in results:
                with st.expander(f"د. {d_info[1]} | {d_dist:.2f} كم"):
                    sel_date = st.date_input("موعد الحجز", min_value=date.today(), key=f"date_{d_info[0]}")
                    if st.button("تأكيد الحجز", key=f"btn_{d_info[0]}"):
                        conn = sqlite3.connect(DB_NAME)
                        conn.execute("INSERT INTO appointments (username, doctor_name, date, time) VALUES (?,?,?,?)",
                                    (st.session_state.user_name, d_info[1], str(sel_date), "04:00 PM"))
                        conn.commit()
                        conn.close()
                        st.success("تم الحجز بنجاح!")
        else:
            st.warning("يرجى الانتظار لتحديد موقعك أو السماح بالوصول للـ GPS.")

elif choice == "خروج":
    st.session_state.logged_in = False
    st.rerun()