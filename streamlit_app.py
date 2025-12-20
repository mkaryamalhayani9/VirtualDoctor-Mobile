import streamlit as st
import sqlite3
import hashlib
import math
import random
from datetime import datetime, timedelta
from streamlit_js_eval import get_geolocation

# --- 1. التصميم الزمردي الفخم (Emerald Dark Classic) ---
st.set_page_config(page_title="Al Doctor", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,700&family=Tajawal:wght@400;700&display=swap');
    
    * { font-family: 'Tajawal', sans-serif; direction: rtl; }
    .stApp { background: #040d0a; color: #d1d1d1; }
    
    /* شعار الموقع كلاسيك */
    .classic-logo { 
        font-family: 'Playfair Display', serif; 
        color: #50c878; 
        text-align: center; 
        font-size: 50px; 
        letter-spacing: 2px;
        margin-bottom: 5px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    .sub-logo { text-align: center; color: #888; font-size: 14px; margin-bottom: 30px; }

    /* تصغير حجم مربعات الإدخال وتوسيطها */
    .stTextInput > div > div > input {
        background-color: #0a1a15 !important;
        color: white !important;
        border: 1px solid #1a4d3c !important;
        border-radius: 8px !important;
    }
    .auth-container { max-width: 400px; margin: auto; padding: 20px; background: #0a1a15; border-radius: 15px; border: 1px solid #50c87833; }
    
    /* بطاقات الأطباء */
    .doc-card { 
        background: linear-gradient(145deg, #0a1a15, #0d261e); 
        padding: 20px; border-radius: 12px; 
        border-right: 5px solid #50c878; 
        margin-bottom: 15px;
        transition: 0.3s;
    }
    .emergency-card { border-right-color: #e63946; background: #1a0a0a; }

    /* الأزرار */
    .stButton>button { 
        background: linear-gradient(135deg, #1a4d3c 0%, #50c878 100%); 
        color: white; border: none; border-radius: 8px; font-weight: bold; 
    }
    .secondary-btn button { background: transparent !important; color: #50c878 !important; border: 1px solid #50c878 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إدارة قاعدة البيانات ---
DB_NAME = "al_doctor_emerald.db"
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
    conn.commit()
    conn.close()

init_db()

# --- 3. بيانات التشخيص (20 حالة) وأطباء بغداد ---
DIAGNOSTIC_DATA = {
    "ألم ضاغط في الصدر": {"diag": "اشتباه بنوبة قلبية", "spec": "أمراض القلب", "em": True},
    "صعوبة في الكلام وتنميل": {"diag": "اشتباه بجلطة دماغية", "spec": "مخ وأعصاب", "em": True},
    "ألم أسفل البطن جهة اليمين": {"diag": "اشتباه زائدة دودية", "spec": "جراحة عامة", "em": True},
    "ضيق تنفس حاد": {"diag": "أزمة تنفسية حادة", "spec": "صدرية", "em": True},
    "اصفرار الجلد والعينين": {"diag": "يرقان/التهاب كبد", "spec": "باطنية", "em": False},
    "تبول متكرر وعطش": {"diag": "ارتفاع سكر الدم", "spec": "غدد صماء", "em": False},
    "صداع نصفي مزمن": {"diag": "شقيقة (Migraine)", "spec": "جملة عصبية", "em": False},
    "حكة وطفح جلدي": {"diag": "حساسية جلدية", "spec": "جلدية", "em": False},
    "ألم أذن مفاجئ": {"diag": "التهاب الأذن الوسطى", "spec": "أنف وأذن", "em": False},
    "ألم أسفل الظهر حاد": {"diag": "انزلاق غضروفي", "spec": "مفاصل", "em": False},
    "حزن مستمر وخمول": {"diag": "اكتئاب", "spec": "طب نفسي", "em": False},
    "تساقط شعر وتعب": {"diag": "نقص فيتامينات/غدة", "spec": "غدد صماء", "em": False},
    "ألم لثة ونزيف": {"diag": "التهاب لثة", "spec": "أسنان", "em": False},
    "حرقة معدة مستمرة": {"diag": "ارتجاع مريئي", "spec": "جهاز هضمي", "em": False},
    "تورم في المفاصل": {"diag": "روماتزم", "spec": "مفاصل", "em": False},
    "تأخر نطق للأطفال": {"diag": "اضطراب نمو", "spec": "أطفال", "em": False},
    "طنين أذن مستمر": {"diag": "ضغط أذن", "spec": "أنف وأذن", "em": False},
    "رعشة في اليدين": {"diag": "جهاز عصبي", "spec": "مخ وأعصاب", "em": False},
    "ضعف في الرؤية": {"diag": "قصر/بعد نظر", "spec": "عيون", "em": False},
    "سعال جاف طويل": {"diag": "تحسس روي", "spec": "صدرية", "em": False}
}

DOCTORS_BAGHDAD = [
    {"name": "د. مصطفى الجادر", "spec": "أمراض القلب", "area": "المنصور", "lat": 33.325, "lon": 44.348},
    {"name": "د. رنا الحديثي", "spec": "جلدية", "area": "الكرادة", "lat": 33.300, "lon": 44.420},
    {"name": "مستشفى ابن الهيثم", "spec": "عيون", "area": "الرصافة", "lat": 33.315, "lon": 44.410},
    {"name": "د. ياسر الأعظمي", "spec": "مخ وأعصاب", "area": "الأعظمية", "lat": 33.365, "lon": 44.380},
    {"name": "د. هدى الكاظمي", "spec": "أطفال", "area": "الكاظمية", "lat": 33.380, "lon": 44.340}
]

# --- 4. المنطق الوظيفي ---
if "view" not in st.session_state: st.session_state.view = "login"

def check_username(u):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username=?', (u,))
    res = c.fetchone()
    conn.close()
    return res

# --- 5. واجهات العرض ---

st.markdown('<div class="classic-logo">Al Doctor</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-logo">PREMIUM MEDICAL ASSISTANCE</div>', unsafe_allow_html=True)

# واجهة الدخول
if st.session_state.view == "login":
    with st.container():
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        st.subheader("تسجيل الدخول")
        u = st.text_input("اسم المستخدم", placeholder="User123")
        p = st.text_input("كلمة المرور", type="password", placeholder="**")
        if st.button("دخول للنظام"):
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            hp = hashlib.sha256(p.encode()).hexdigest()
            c.execute('SELECT * FROM users WHERE username=? AND password=?', (u, hp))
            if c.fetchone():
                st.session_state.user = u
                st.session_state.view = "app"
                st.rerun()
            else: st.error("عذراً، البيانات غير صحيحة")
        
        st.write("---")
        st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
        if st.button("لا تملك حساب؟ سجل الآن"):
            st.session_state.view = "signup"
            st.rerun()
        st.markdown('</div></div>', unsafe_allow_html=True)

# واجهة التسجيل
elif st.session_state.view == "signup":
    with st.container():
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        st.subheader("عضوية جديدة")
        nu = st.text_input("اختر اسم المستخدم")
        np = st.text_input("كلمة السر", type="password")
        if st.button("تأكيد التسجيل"):
            if check_username(nu):
                st.error("⚠️ هذا الاسم مأخوذ مسبقاً! انتبه واختر اسماً آخر.")
            elif nu and np:
                conn = sqlite3.connect(DB_NAME)
                c = conn.cursor()
                hp = hashlib.sha256(np.encode()).hexdigest()
                c.execute('INSERT INTO users VALUES (?,?)', (nu, hp))
                conn.commit()
                conn.close()
                st.success("تم بنجاح! جاري الانتقال...")
                st.session_state.view = "login"
                st.rerun()
        if st.button("العودة للخلف", key="back"):
            st.session_state.view = "login"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# واجهة التطبيق الرئيسية
elif st.session_state.view == "app":
    col_main, col_side = st.columns([2, 1])
    
    with col_side:
        st.markdown(f"### طاب يومك، {st.session_state.user}")
        symptoms = st.multiselect("ما هي الأعراض؟", list(DIAGNOSTIC_DATA.keys()))
        loc = get_geolocation() # تحديد تلقائي
        
        if st.button("بدء الفحص الزمردي"):
            if symptoms and loc:
                st.session_state.active_diag = symptoms
                st.session_state.u_loc = loc
            else: st.warning("يرجى اختيار الأعراض وتفعيل الموقع")

    with col_main:
        if "active_diag" in st.session_state:
            u_lat = st.session_state.u_loc['coords']['latitude']
            u_lon = st.session_state.u_loc['coords']['longitude']
            
            is_emergency = any(DIAGNOSTIC_DATA[s]["em"] for s in st.session_state.active_diag)
            specs = [DIAGNOSTIC_DATA[s]["spec"] for s in st.session_state.active_diag]
            
            st.success(f"التشخيص المتوقع: {DIAGNOSTIC_DATA[st.session_state.active_diag[0]]['diag']}")
            
            # فلترة الأطباء
            results = []
            for d in DOCTORS_BAGHDAD:
                dist = math.sqrt((u_lat - d['lat'])*2 + (u_lon - d['lon'])*2) * 111
                if d['spec'] in specs or is_emergency:
                    d['dist'] = dist
                    results.append(d)
            
            results.sort(key=lambda x: x['dist'])
            
            for doc in results:
                is_em = "emergency-card" if is_emergency else ""
                next_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
                
                st.markdown(f"""
                <div class="doc-card {is_em}">
                    <div style="display:flex; justify-content:space-between">
                        <b style="color:#50c878; font-size:18px;">{doc['name']}</b>
                        <span>📍 {doc['area']}</span>
                    </div>
                    <p>الاختصاص: {doc['spec']} | المسافة: {doc['dist']:.1f} كم</p>
                    <hr style="opacity:0.1">
                    <small>أقرب موعد حجز متاح: <b>{next_date} الساعة 10:00 صباحاً</b></small>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"تأكيد الحجز مع {doc['name']}", key=doc['name']):
                    st.balloons()
                    st.success("تم تثبيت الموعد بنجاح.")

    if st.sidebar.button("خروج"):
        st.session_state.view = "login"
        st.rerun()
