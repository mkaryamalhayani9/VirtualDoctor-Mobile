import streamlit as st
import sqlite3
import math
import os
from datetime import date
from streamlit_js_eval import get_geolocation

# --- 1. إعداد التصميم (Classic Emerald Dashboard) ---
st.set_page_config(page_title="Emerald Medical Portal", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    * { font-family: 'Tajawal', sans-serif; }
    .stApp { background: #050a0b; color: #e0f2f1; }
    
    /* الحاوية المتوسطة المترتبة */
    .main-portal {
        max-width: 600px;
        margin: 50px auto;
        padding: 40px;
        background: rgba(255, 255, 255, 0.03);
        border-radius: 20px;
        border: 1px solid rgba(113, 178, 128, 0.2);
        box-shadow: 0 20px 50px rgba(0,0,0,0.5);
    }
    .stButton>button {
        background: linear-gradient(135deg, #134E5E 0%, #71B280 100%);
        color: white; border-radius: 10px; height: 3.5em; border: none; font-weight: bold;
    }
    h1 { color: #71B280; text-align: center; margin-bottom: 30px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. حل مشكلة قاعدة البيانات (إصلاح OperationalError) ---
def get_db():
    # استخدام ملف محلي في المجلد الحالي لضمان الوصول
    return sqlite3.connect("virtual_doctor.db", check_same_thread=False)

def init_db():
    conn = get_db()
    c = conn.cursor()
    # التأكد من إنشاء الجداول أولاً لكي لا يظهر الخطأ الأحمر
    c.execute("CREATE TABLE IF NOT EXISTS users (u TEXT PRIMARY KEY, p TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS docs (name TEXT, spec TEXT, lat REAL, lon REAL)")
    c.execute("CREATE TABLE IF NOT EXISTS appts (u TEXT, d TEXT, dt TEXT, tm TEXT)")
    
    c.execute("SELECT COUNT(*) FROM docs")
    if c.fetchone()[0] == 0:
        c.executemany("INSERT INTO docs VALUES (?,?,?,?)", [
            ("د. هاشم العبيدي", "قلب وباطنية", 33.3128, 44.3615),
            ("د. ميساء الخزرجي", "جلدية", 33.3020, 44.4210),
            ("د. زيد الحكيم", "طوارئ وعام", 33.2750, 44.3750)
        ])
    conn.commit()
    conn.close()

# تشغيل التهيئة فوراً
init_db()

# --- 3. إدارة التنقل ---
if "auth" not in st.session_state: st.session_state.auth = False
if "view" not in st.session_state: st.session_state.view = "login"

# --- 4. واجهة الدخول والإنشاء ---
if not st.session_state.auth:
    _, col_mid, _ = st.columns([1, 2, 1])
    with col_mid:
        st.markdown('<div class="main-portal">', unsafe_allow_html=True)
        
        if st.session_state.view == "login":
            st.markdown("<h1>Medical Login</h1>", unsafe_allow_html=True)
            u = st.text_input("اسم المستخدم")
            p = st.text_input("كلمة المرور", type="password")
            
            if st.button("دخول للنظام"):
                conn = get_db()
                res = conn.execute("SELECT * FROM users WHERE u=? AND p=?", (u, p)).fetchone()
                conn.close()
                if res:
                    st.session_state.auth = True; st.session_state.user = u; st.rerun()
                else: st.error("خطأ في بيانات الدخول")
            
            # --- هذا الزر يحل مشكلة عدم ظهور "إنشاء حساب" ---
            st.write("---")
            if st.button("لا تملك حساباً؟ اضغط هنا لإنشاء حساب جديد"):
                st.session_state.view = "reg"; st.rerun()

        elif st.session_state.view == "reg":
            st.markdown("<h1>New Account</h1>", unsafe_allow_html=True)
            nu = st.text_input("اختار اسم مستخدم")
            np = st.text_input("اختار كلمة مرور", type="password")
            
            if st.button("تأكيد إنشاء الحساب"):
                if nu and np:
                    try:
                        conn = get_db()
                        conn.execute("INSERT INTO users VALUES (?,?)", (nu, np))
                        conn.commit(); conn.close()
                        st.success("تم الإنشاء بنجاح! يمكنك الآن تسجيل الدخول.")
                        st.session_state.view = "login"; st.rerun()
                    except: st.error("الاسم مأخوذ مسبقاً")
            
            if st.button("العودة لصفحة الدخول"):
                st.session_state.view = "login"; st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

# --- 5. واجهة الخدمات (بعد الدخول) ---
else:
    with st.sidebar:
        st.markdown(f"### مرحباً {st.session_state.user}")
        menu = st.radio("القائمة", ["التشخيص", "حجوزاتي", "خروج"])
    
    if menu == "التشخيص":
        st.markdown('<div class="main-portal" style="max-width:900px;">', unsafe_allow_html=True)
        st.markdown("<h1>Smart Diagnosis</h1>", unsafe_allow_html=True)
        syms = st.multiselect("الأعراض:", ["ألم صدر", "ضيق تنفس", "حمى"])
        
        if st.button("ابحث عن أقرب طبيب"):
            loc = get_geolocation()
            if loc:
                u_lat, u_lon = loc['coords']['latitude'], loc['coords']['longitude']
                conn = get_db()
                docs = conn.execute("SELECT * FROM docs").fetchall()
                conn.close()
                
                for d in docs:
                    dist = math.sqrt((u_lat-d[2])*2 + (u_lon-d[3])*2)*111
                    st.write(f"🩺 {d[0]} - يبعد {dist:.1f} كم")
                    if st.button(f"حجز عند {d[0]}", key=d[0]):
                        st.success("تم الحجز!")
            else: st.warning("فعل GPS الموقع")
        st.markdown('</div>', unsafe_allow_html=True)
    
    elif menu == "خروج":
        st.session_state.auth = False; st.rerun()
