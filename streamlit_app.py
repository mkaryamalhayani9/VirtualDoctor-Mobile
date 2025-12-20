import streamlit as st
import sqlite3
import hashlib
import math
from datetime import datetime, timedelta
from streamlit_js_eval import get_geolocation

# --- 1. التصميم البصري (أسود وفيروزي فخم) ---
st.set_page_config(page_title="Al Doctor", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Tajawal:wght@400;700&display=swap');
    
    * { font-family: 'Tajawal', sans-serif; direction: rtl; }
    .stApp { background: #050505; color: #e0e0e0; }
    
    .classic-logo { 
        font-family: 'Playfair Display', serif; 
        color: #40E0D0; /* فيروزي */
        text-align: center; font-size: 55px; margin-bottom: 0px;
        text-shadow: 0 0 15px rgba(64, 224, 208, 0.3);
    }
    .sub-logo { text-align: center; color: #777; font-size: 13px; margin-bottom: 35px; letter-spacing: 2px; }

    /* تصغير مربعات الإدخال وتوسيطها */
    .auth-box { max-width: 380px; margin: auto; padding: 25px; background: #0f0f0f; border-radius: 12px; border: 1px solid #40E0D033; }
    
    .stTextInput > div > div > input {
        background-color: #151515 !important;
        color: #40E0D0 !important;
        border: 1px solid #40E0D044 !important;
        text-align: center;
    }

    /* بطاقات الأطباء */
    .doc-card { 
        background: #0f0f0f; padding: 18px; border-radius: 10px; 
        border-right: 4px solid #40E0D0; margin-bottom: 12px;
        border-bottom: 1px solid #40E0D011;
    }
    .emergency-card { border-right-color: #ff4b4b; background: #1a0808; }

    /* الأزرار */
    .stButton>button { 
        background: linear-gradient(135deg, #1d4e4a 0%, #40E0D0 100%); 
        color: #000; border: none; border-radius: 5px; font-weight: bold; height: 3em;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إدارة قاعدة البيانات ---
DB_NAME = "al_doctor_v4.db"
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
    conn.commit()
    conn.close()

init_db()

# --- 3. البيانات الطبية (بغداد) ---
DIAG_DB = {
    "ألم في الصدر": {"diag": "اشتباه بنوبة قلبية", "spec": "أمراض القلب", "em": True},
    "ضيق تنفس": {"diag": "أزمة صدرية حادة", "spec": "صدرية", "em": True},
    "سعال جاف طويل": {"diag": "تحسس روي / التهاب قصبات", "spec": "صدرية", "em": False},
    "صداع شديد": {"diag": "شقيقة أو ضغط دم", "spec": "مخ وأعصاب", "em": False},
    "ألم أسفل الظهر": {"diag": "انزلاق غضروفي", "spec": "عظام ومفاصل", "em": False},
    "حكة وطفح": {"diag": "حساسية جلدية", "spec": "جلدية", "em": False},
    "عطش وتبول متكرر": {"diag": "اشتباه سكري", "spec": "غدد صماء", "em": False},
    "ألم في الأذن": {"diag": "التهاب الأذن", "spec": "أنف وأذن", "em": False}
}

DOCTORS = [
    {"name": "د. أحمد (المنصور)", "spec": "أمراض القلب", "lat": 33.325, "lon": 44.348},
    {"name": "د. ليلى (الكرادة)", "spec": "صدرية", "lat": 33.300, "lon": 44.420},
    {"name": "د. سامر (الحارثية)", "spec": "مخ وأعصاب", "lat": 33.322, "lon": 44.358},
    {"name": "د. زينة (زيونة)", "spec": "جلدية", "lat": 33.332, "lon": 44.455},
    {"name": "مركز طوارئ بغداد", "spec": "طوارئ", "lat": 33.310, "lon": 44.370}
]

# --- 4. منطق الأمان والحساب ---
if "page" not in st.session_state: st.session_state.page = "login"

def safe_distance(lat1, lon1, lat2, lon2):
    try:
        # حل مشكلة ValueError: التأكد من أن الإحداثيات ليست None
        if lat1 is None or lon1 is None: return 999
        return math.sqrt((float(lat1) - float(lat2))*2 + (float(lon1) - float(lon2))*2) * 111
    except: return 999

# --- 5. الواجهات ---

st.markdown('<div class="classic-logo">Al Doctor</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-logo">VIRTUAL MEDICAL ASSISTANT</div>', unsafe_allow_html=True)

# واجهة تسجيل الدخول
if st.session_state.page == "login":
    st.markdown('<div class="auth-box">', unsafe_allow_html=True)
    u = st.text_input("اسم المستخدم")
    p = st.text_input("كلمة المرور", type="password")
    if st.button("تسجيل الدخول"):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        hp = hashlib.sha256(p.encode()).hexdigest()
        c.execute('SELECT * FROM users WHERE username=? AND password=?', (u, hp))
        if c.fetchone():
            st.session_state.user = u
            st.session_state.page = "main"
            st.rerun()
        else: st.error("بيانات الدخول غير صحيحة")
    
    st.write("---")
    if st.button("إنشاء حساب جديد"):
        st.session_state.page = "signup"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# واجهة إنشاء الحساب
elif st.session_state.page == "signup":
    st.markdown('<div class="auth-box">', unsafe_allow_html=True)
    nu = st.text_input("اختر اسم مستخدم")
    np = st.text_input("اختر كلمة مرور", type="password")
    if st.button("تأكيد التسجيل"):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        try:
            hp = hashlib.sha256(np.encode()).hexdigest()
            c.execute('INSERT INTO users VALUES (?,?)', (nu, hp))
            conn.commit()
            st.success("تم التسجيل بنجاح!")
            st.session_state.page = "login"
            st.rerun()
        except sqlite3.IntegrityError:
            st.error("⚠️ هذا الاسم مأخوذ مسبقاً، يرجى اختيار اسم آخر.")
        conn.close()
    if st.button("العودة"):
        st.session_state.page = "login"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# الواجهة الرئيسية
elif st.session_state.page == "main":
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown(f"*مرحباً، {st.session_state.user}*")
        selected = st.multiselect("بماذا تشعر؟", list(DIAG_DB.keys()))
        # طلب الموقع تلقائياً
        loc_data = get_geolocation()
        
        if st.button("بدء الفحص الفيروزي"):
            if selected:
                st.session_state.diag_active = selected
                st.session_state.gps = loc_data
            else: st.warning("يرجى اختيار عرض واحد")

    with col2:
        if "diag_active" in st.session_state:
            # التحقق من الموقع لمنع الخطأ الذي ظهر في الصورة
            if not st.session_state.gps or 'coords' not in st.session_state.gps:
                st.error("📍 يرجى السماح للمتصفح بالوصول لموقعك (GPS) لتحديد الأطباء.")
            else:
                u_lat = st.session_state.gps['coords']['latitude']
                u_lon = st.session_state.gps['coords']['longitude']
                
                is_em = any(DIAG_DB[s]["em"] for s in st.session_state.diag_active)
                st.info(f"التشخيص المتوقع: {DIAG_DB[st.session_state.diag_active[0]]['diag']}")
                
                if is_em: st.error("🚨 حالة طوارئ! توجه لأقرب مستشفى.")

                # تصفية الأطباء حسب المسافة
                matched = []
                for d in DOCTORS:
                    dist = safe_distance(u_lat, u_lon, d['lat'], d['lon'])
                    d['dist'] = dist
                    matched.append(d)
                
                matched.sort(key=lambda x: x['dist'])
                
                for doc in matched:
                    is_em_style = "emergency-card" if is_em and (doc['spec'] == "أمراض القلب" or doc['spec'] == "طوار") else ""
                    st.markdown(f"""
                    <div class="doc-card {is_em_style}">
                        <div style="display:flex; justify-content:space-between; color:#40E0D0">
                            <b>{doc['name']}</b>
                            <span>📍 {doc['area'] if 'area' in doc else 'بغداد'}</span>
                        </div>
                        <div style="font-size:13px; margin-top:5px">
                            التخصص: {doc['spec']} | المسافة: {doc['dist']:.1f} كم
                        </div>
                        <div style="color:#777; font-size:11px; margin-top:8px">
                            أقرب حجز: غداً 10:00 صباحاً
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"حجز مع {doc['name']}", key=doc['name']):
                        st.success("تم تثبيت الموعد.")

    if st.sidebar.button("خروج"):
        st.session_state.page = "login"
        st.rerun()
