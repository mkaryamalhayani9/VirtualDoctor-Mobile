import streamlit as st
import sqlite3
import math
from datetime import date
from streamlit_js_eval import get_geolocation

# --- 1. التصميم (Premium Web Interface) ---
st.set_page_config(page_title="Emerald Medical Portal", layout="wide")

st.markdown("""
    <style>
    /* استيراد خط احترافي */
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    
    * { font-family: 'Tajawal', sans-serif; }

    .stApp {
        background: radial-gradient(circle at top, #0d1b1e, #050a0b);
        color: #e0f2f1;
    }

    /* الحاوية المتوسطة والمرتبة */
    .main-container {
        max-width: 800px;
        margin: 50px auto;
        padding: 40px;
        background: rgba(255, 255, 255, 0.02);
        border-radius: 20px;
        border: 1px solid rgba(113, 178, 128, 0.1);
        box-shadow: 0 30px 60px rgba(0,0,0,0.5);
    }

    /* تنسيق العناوين */
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #71B280, #fff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 30px;
        text-align: center;
    }

    /* الأزرار الاحترافية */
    .stButton>button {
        background: linear-gradient(135deg, #134E5E 0%, #71B280 100%);
        color: white; border-radius: 8px; height: 3.2em; border: none;
        width: 100%; font-weight: 700; letter-spacing: 0.5px;
        transition: 0.3s all ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(113, 178, 128, 0.3);
    }

    /* روابط التنقل الهادئة */
    .nav-link {
        color: #71B280;
        text-align: center;
        margin-top: 20px;
        font-size: 0.95rem;
        cursor: pointer;
        opacity: 0.8;
    }
    .nav-link:hover { opacity: 1; text-decoration: underline; }

    /* حقول الإدخال */
    input {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(113,178,128,0.2) !important;
        color: white !important;
        border-radius: 10px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إدارة قاعدة البيانات ---
def get_db():
    return sqlite3.connect("virtual_doctor.db", check_same_thread=False)

def init_db():
    with get_db() as conn:
        c = conn.cursor()
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

init_db()

# --- 3. المنطق وإدارة الجلسة ---
if "auth" not in st.session_state: st.session_state.auth = False
if "view" not in st.session_state: st.session_state.view = "login"

# --- 4. واجهات تسجيل الدخول والإنشاء (Centered Design) ---
if not st.session_state.auth:
    # إنشاء صفوف وأعمدة لوضع المحتوى في الوسط
    _, col_main, _ = st.columns([1, 2, 1])
    
    with col_main:
        st.markdown('<div class="main-container">', unsafe_allow_html=True)
        
        if st.session_state.view == "login":
            st.markdown('<h1 class="main-title">Medical Login</h1>', unsafe_allow_html=True)
            u = st.text_input("Username", placeholder="أدخل اسم المستخدم")
            p = st.text_input("Password", type="password", placeholder="أدخل كلمة المرور")
            
            if st.button("تسجيل الدخول"):
                with get_db() as conn:
                    res = conn.execute("SELECT * FROM users WHERE u=? AND p=?", (u, p)).fetchone()
                if res:
                    st.session_state.auth = True; st.session_state.user = u; st.rerun()
                else: st.error("عذراً، البيانات غير صحيحة")
            
            # رابط إنشاء الحساب
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("ليس لديك حساب؟ إنشاء حساب جديد"):
                st.session_state.view = "reg"; st.rerun()

        elif st.session_state.view == "reg":
            st.markdown('<h1 class="main-title">New Account</h1>', unsafe_allow_html=True)
            nu = st.text_input("New Username")
            np = st.text_input("New Password", type="password")
            
            if st.button("تأكيد التسجيل"):
                if nu and np:
                    try:
                        with get_db() as conn:
                            conn.execute("INSERT INTO users VALUES (?,?)", (nu, np))
                            conn.commit()
                        st.success("تم الإنشاء بنجاح! توجه للدخول.")
                        st.session_state.view = "login"; st.rerun()
                    except: st.error("الاسم مأخوذ مسبقاً")
            
            if st.button("لديك حساب؟ اذهب لتسجيل الدخول"):
                st.session_state.view = "login"; st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

# --- 5. واجهة التطبيق الرئيسية (بعد الدخول) ---
else:
    with st.sidebar:
        st.markdown(f"<h3 style='color:#71B280;'>Elite: {st.session_state.user}</h3>", unsafe_allow_html=True)
        menu = st.radio("القائمة الرئيسية", ["التشخيص الذكي", "مواعيدي", "خروج"])
    
    st.markdown('<div class="main-container" style="max-width:1000px;">', unsafe_allow_html=True)
    
    if menu == "التشخيص الذكي":
        st.markdown('<h1 class="main-title">Smart Diagnosis</h1>', unsafe_allow_html=True)
        syms = st.multiselect("حدد الأعراض الظاهرة:", ["ألم في الصدر", "ضيق تنفس", "طفح جلدي", "حمى"])
        
        if st.button("تحليل الحالة وإيجاد الطبيب"):
            loc = get_geolocation()
            if loc:
                u_lat, u_lon = loc['coords']['latitude'], loc['coords']['longitude']
                spec = "طوارئ وعام"
                if "ألم في الصدر" in syms: spec = "قلب وباطنية"
                
                with get_db() as conn:
                    docs = conn.execute("SELECT * FROM docs WHERE spec=?", (spec,)).fetchall()
                
                st.write("---")
                for d in docs:
                    dist = math.sqrt((u_lat-d[2])*2 + (u_lon-d[3])*2)*111
                    st.markdown(f"""
                    <div style="background:rgba(255,255,255,0.03); padding:20px; border-radius:15px; margin-bottom:15px; border-right:5px solid #71B280;">
                        <h4 style="margin:0; color:#71B280;">{d[0]}</h4>
                        <p style="margin:5px 0;">المسافة: {dist:.1f} كم | التخصص: {d[1]}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    dt = st.date_input("اختر تاريخ الموعد", min_value=date.today(), key=d[0])
                    if st.button(f"حجز موعد نهائي عند {d[0]}", key=f"b_{d[0]}"):
                        with get_db() as conn:
                            conn.execute("INSERT INTO appts VALUES (?,?,?,?)", (st.session_state.user, d[0], str(dt), "6:00 PM"))
                        st.balloons(); st.success("تم الحجز بنجاح!")
            else: st.warning("يرجى تفعيل الموقع (GPS) للمتابعة")
            
    elif menu == "خروج":
        st.session_state.auth = False; st.rerun()
        
    st.markdown('</div>', unsafe_allow_html=True)
