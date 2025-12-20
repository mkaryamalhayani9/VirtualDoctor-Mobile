import streamlit as st
import sqlite3
import math
from datetime import datetime, date
from streamlit_js_eval import get_geolocation

# --- 1. التصميم الاحترافي (ألوان بيبي بنك، بيبي بلو، أزرق طافي) ---
st.set_page_config(page_title="AI Doctor Premium", layout="wide")

st.markdown("""
    <style>
    /* الخلفية العامة */
    .stApp { background-color: #fcfcfc; }
    
    /* الحاوية الرئيسية (البطاقات) */
    .main-card {
        background-color: white;
        padding: 40px;
        border-radius: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        border: 1px solid #f0f2f6;
        max-width: 600px;
        margin: auto;
    }

    /* ألوان الأزرار */
    .stButton>button {
        background: linear-gradient(135deg, #89CFF0 0%, #F4C2C2 100%); /* مزيج بيبي بلو وبيبي بنك */
        color: white;
        border-radius: 15px;
        height: 3.5em;
        border: none;
        width: 100%;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(137, 207, 240, 0.4);
    }

    /* العناوين (أزرق طافي) */
    h1, h2, h3 {
        color: #2C3E50 !important; /* Navy Blue / أزرق طافي */
        text-align: center;
        font-family: 'Segoe UI', sans-serif;
    }

    /* تنسيق الحقول */
    input {
        border-radius: 12px !important;
        border: 1px solid #e0e0e0 !important;
    }

    /* بطاقة الطبيب */
    .doctor-box {
        background: white;
        border-left: 6px solid #89CFF0; /* بيبي بلو */
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    }

    /* تنبيه الطوارئ (بيبي بنك داكن) */
    .emergency-ui {
        background-color: #FFF0F0;
        border: 1px solid #F4C2C2;
        color: #D64545;
        padding: 15px;
        border-radius: 15px;
        text-align: center;
        font-weight: bold;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إعدادات قاعدة البيانات ---
DB_PATH = "virtual_doctor.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (u TEXT PRIMARY KEY, p TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS docs (name TEXT, spec TEXT, lat REAL, lon REAL)")
    c.execute("CREATE TABLE IF NOT EXISTS appts (u TEXT, d TEXT, dt TEXT, tm TEXT)")
    c.execute("SELECT COUNT(*) FROM docs")
    if c.fetchone()[0] == 0:
        c.executemany("INSERT INTO docs VALUES (?,?,?,?)", [
            ("د. علي الركابي", "قلب وباطنية", 33.3128, 44.3615),
            ("د. سارة الحسني", "جلدية", 33.3020, 44.4210),
            ("د. ليث السامرائي", "طوارئ وعام", 33.2750, 44.3750)
        ])
    conn.commit()
    conn.close()

init_db()

# --- 3. إدارة الحالة (الدخول والتسجيل) ---
if "auth" not in st.session_state: st.session_state.auth = False
if "page" not in st.session_state: st.session_state.page = "login"

# --- 4. صفحات تسجيل الدخول والإنشاء (بدون سايد بار) ---
if not st.session_state.auth:
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    if st.session_state.page == "login":
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.markdown("<h1>تسجيل الدخول</h1>", unsafe_allow_html=True)
        u = st.text_input("اسم المستخدم", key="l_u")
        p = st.text_input("كلمة المرور", type="password", key="l_p")
        
        if st.button("دخول"):
            conn = sqlite3.connect(DB_PATH)
            res = conn.execute("SELECT * FROM users WHERE u=? AND p=?", (u, p)).fetchone()
            conn.close()
            if res:
                st.session_state.auth = True
                st.session_state.user = u
                st.rerun()
            else: st.error("خطأ في البيانات")
            
        st.markdown("---")
        if st.button("ليس لديك حساب؟ إنشاء حساب جديد"):
            st.session_state.page = "register"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    elif st.session_state.page == "register":
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.markdown("<h1>إنشاء حساب جديد</h1>", unsafe_allow_html=True)
        nu = st.text_input("اختار اسم مستخدم", key="r_u")
        np = st.text_input("اختار كلمة مرور", type="password", key="r_p")
        
        if st.button("تأكيد الإنشاء"):
            if nu and np:
                try:
                    conn = sqlite3.connect(DB_PATH)
                    conn.execute("INSERT INTO users VALUES (?,?)", (nu, np))
                    conn.commit()
                    conn.close()
                    st.success("تم الإنشاء بنجاح! يمكنك الآن الدخول.")
                except: st.error("هذا الاسم مستخدم مسبقاً.")
            else: st.warning("يرجى ملء الحقول.")
            
        st.markdown("---")
        if st.button("لديك حساب بالفعل؟ سجل دخولك"):
            st.session_state.page = "login"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- 5. الصفحة الرئيسية بعد الدخول ---
else:
    with st.sidebar:
        st.markdown(f"<h3 style='color:#89CFF0;'>مرحباً {st.session_state.user}</h3>", unsafe_allow_html=True)
        menu = st.radio("الخدمات", ["التشخيص الذكي", "مواعيدي", "خروج"])
    
    if menu == "التشخيص الذكي":
        st.markdown("<h2>🔍 المساعد الطبي الذكي</h2>", unsafe_allow_html=True)
        
        syms = st.multiselect("حدد أعراضك:", ["ألم في الصدر", "ضيق تنفس", "طفح جلدي", "حمى"])
        
        if st.button("تحليل ورصد الأطباء"):
            target = "طوارئ وعام"
            is_em = False
            if "ألم في الصدر" in syms or "ضيق تنفس" in syms:
                target, is_em = "قلب وباطنية", True
            elif "طفح جلدي" in syms: target = "جلدية"
            
            if is_em:
                st.markdown('<div class="emergency-ui">⚠️ حالة طارئة: تم حصر الأطباء بالأقرب لتخصص القلب.</div>', unsafe_allow_html=True)
            
            loc = get_geolocation()
            if loc:
                u_lat, u_lon = loc['coords']['latitude'], loc['coords']['longitude']
                conn = sqlite3.connect(DB_PATH)
                docs = conn.execute("SELECT * FROM docs WHERE spec=?", (target,)).fetchall()
                conn.close()
                
                res = sorted([(d, math.sqrt((u_lat-d[2])*2 + (u_lon-d[3])*2)*111) for d in docs], key=lambda x: x[1])
                
                for d_info, d_dist in res:
                    st.markdown(f"""
                    <div class="doctor-box">
                        <h4 style='color:#2C3E50;'>👨‍⚕️ {d_info[0]}</h4>
                        <p style='color:#7f8c8d;'>المسافة: {d_dist:.2f} كم</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    c1, c2 = st.columns(2)
                    with c1: d_val = st.date_input("اليوم", min_value=date.today(), key=d_info[0])
                    with c2: t_val = st.selectbox("الوقت", ["4:00 PM", "6:00 PM", "8:00 PM"], key=f"t_{d_info[0]}")
                    
                    if st.button(f"تأكيد الموعد عند {d_info[0]}", key=f"b_{d_info[0]}"):
                        conn = sqlite3.connect(DB_PATH)
                        conn.execute("INSERT INTO appts VALUES (?,?,?,?)", (st.session_state.user, d_info[0], str(d_val), t_val))
                        conn.commit(); conn.close()
                        st.balloons(); st.success("تم الحجز!")
            else:
                st.warning("يرجى تفعيل الـ GPS")

    elif menu == "مواعيدي":
        st.markdown("<h2>📅 حجوزاتي</h2>", unsafe_allow_html=True)
        conn = sqlite3.connect(DB_PATH)
        data = conn.execute("SELECT d, dt, tm FROM appts WHERE u=?", (st.session_state.user,)).fetchall()
        conn.close()
        for appt in data:
            st.markdown(f'<div class="doctor-box"><b>{appt[0]}</b><br>التاريخ: {appt[1]} | الوقت: {appt[2]}</div>', unsafe_allow_html=True)

    elif menu == "خروج":
        st.session_state.auth = False
        st.rerun()