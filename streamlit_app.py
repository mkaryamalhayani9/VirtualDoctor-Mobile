import streamlit as st
import sqlite3
import hashlib
import math
import random
from streamlit_js_eval import get_geolocation

# --- 1. التصميم البصري (Al Doctor Classic Turquoise) ---
st.set_page_config(page_title="Al Doctor Premium", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Tajawal:wght@400;700&display=swap');
    * { font-family: 'Tajawal', sans-serif; direction: rtl; }
    .stApp { background: #050505; color: #e0e0e0; }
    .classic-logo { 
        font-family: 'Playfair Display', serif; 
        color: #40E0D0; text-align: center; font-size: 50px; 
        text-shadow: 0 0 20px rgba(64, 224, 208, 0.2); margin-bottom: 0px;
    }
    .sub-logo { text-align: center; color: #666; font-size: 12px; margin-bottom: 30px; letter-spacing: 3px; }
    
    /* تنسيق الحاوية والحقول (تصغير الحجم) */
    .auth-box { max-width: 350px; margin: auto; padding: 20px; background: #0a0a0a; border-radius: 10px; border: 1px solid #40E0D022; }
    .stTextInput > div > div > input { background-color: #0f0f0f !important; color: #40E0D0 !important; border: 1px solid #40E0D033 !important; text-align: center; border-radius: 5px; }
    
    /* بطاقة الطبيب */
    .doc-card { background: #0d0d0d; padding: 15px; border-radius: 8px; border-right: 4px solid #40E0D0; margin-bottom: 10px; border: 1px solid #ffffff05; }
    .emergency-tag { background: #ff4b4b; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; }
    
    /* الزر الفيروزي */
    .stButton>button { 
        background: linear-gradient(135deg, #1d4e4a 0%, #40E0D0 100%); 
        color: #000 !important; border: none; font-weight: bold; border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إدارة قاعدة البيانات ---
DB_NAME = "al_doctor_pro.db"
def init_db():
    conn = sqlite3.connect(DB_NAME)
    conn.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
    conn.close()

init_db()

# --- 3. محرك التشخيص (نسب الاحتمالية + أسباب الطوارئ + التخصص) ---
MEDICAL_ENGINE = {
    "ألم ضاغط حاد في الصدر": {"diag": "ذبحة صدرية غير مستقرة", "prob": "92%", "spec": "طبيب أمراض القلب", "em": True, "reason": "خطر انسداد الشرايين وتوقف عضلة القلب المفاجئ."},
    "ثقل في الكلام وتدلي الوجه": {"diag": "سكتة دماغية إقفارية", "prob": "95%", "spec": "طبيب جملة عصبية", "em": True, "reason": "نقص التروية الدموية للدماغ يتطلب تدخلاً فورياً لمنع الشلل."},
    "ألم أسفل البطن الأيمن": {"diag": "التهاب الزائدة الدودية", "prob": "85%", "spec": "جراح عام", "em": True, "reason": "خطر انفجار الزائدة وتسببها بالتهاب البريتون التسممي."},
    "ضيق تنفس مع صفير حاد": {"diag": "نوبة ربو حادة", "prob": "88%", "spec": "طبيب أمراض صدرية", "em": True, "reason": "تضيق حاد في الممرات الهوائية يهدد بالاختناق."},
    "عطش شديد مع غثيان": {"diag": "الحماض الكيتوني السكري", "prob": "75%", "spec": "طبيب غدد صماء", "em": True, "reason": "ارتفاع حاد في حموضة الدم بسبب السكر قد يؤدي للغيبوبة."},
    "ألم مفاجئ في الخاصرة": {"diag": "مغص كلوي (حصى)", "prob": "80%", "spec": "طبيب مسالك بولية", "em": False, "reason": "انسداد مؤقت في الحالب يسبب ألمًا شديدًا."},
    "خمول مستمر ويأس": {"diag": "اكتئاب سريري", "prob": "70%", "spec": "طبيب نفسي", "em": False, "reason": "اضطراب كيميائي في الدماغ يؤثر على الوظائف اليومية."},
    "طفح جلدي قشري محمر": {"diag": "صدفية جلدية", "prob": "85%", "spec": "طبيب جلدية", "em": False, "reason": "سرعة دوران خلايا الجلد بسبب خلل مناعي."},
    "سعال جاف لأكثر من شهر": {"diag": "تحسس قصبي مزمن", "prob": "75%", "spec": "طبيب صدرية", "em": False, "reason": "التهاب مزمن غير عدوائي في القصبات الهوائية."},
    "ألم أسفل الظهر مع تنميل": {"diag": "انزلاق غضروفي", "prob": "82%", "spec": "طبيب مفاصل وعظام", "em": False, "reason": "ضغط القرص الغضروفي على جذور الأعصاب الوركية."},
}

DOCTORS_BAGHDAD = [
    {"name": "د. علي الركابي", "spec": "طبيب أمراض القلب", "area": "المنصور", "lat": 33.325, "lon": 44.348},
    {"name": "د. عمر الجبوري", "spec": "طبيب جملة عصبية", "area": "الحارثية", "lat": 33.322, "lon": 44.358},
    {"name": "د. مريم القيسي", "spec": "جراح عام", "area": "الكرادة", "lat": 33.300, "lon": 44.420},
    {"name": "د. سارة لؤي", "spec": "طبيب جلدية", "area": "زيونة", "lat": 33.332, "lon": 44.455},
    {"name": "مستشفى مدينة الطب", "spec": "طوارئ", "area": "باب المعظم", "lat": 33.350, "lon": 44.385},
    {"name": "د. ليث الحسيني", "spec": "طبيب غدد صماء", "area": "شارع فلسطين", "lat": 33.345, "lon": 44.430},
    {"name": "د. نور الدين", "spec": "طبيب مفاصل وعظام", "area": "الجادرية", "lat": 33.280, "lon": 44.390},
]

# --- 4. المنطق الوظيفي ---
if "app_state" not in st.session_state: st.session_state.app_state = "login"

def calculate_dist(lat1, lon1, lat2, lon2):
    try: return math.sqrt((float(lat1)-float(lat2))*2 + (float(lon1)-float(lon2))*2) * 111
    except: return 999

# --- 5. الواجهات ---
st.markdown('<div class="classic-logo">Al Doctor</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-logo">PREMIUM HEALTHCARE ASSISTANCE</div>', unsafe_allow_html=True)

# واجهة تسجيل الدخول
if st.session_state.app_state == "login":
    st.markdown('<div class="auth-box">', unsafe_allow_html=True)
    u = st.text_input("اسم المستخدم", placeholder="User123")
    p = st.text_input("كلمة المرور", type="password", placeholder="••••")
    if st.button("دخول"):
        conn = sqlite3.connect(DB_NAME)
        hp = hashlib.sha256(p.encode()).hexdigest()
        if conn.execute('SELECT * FROM users WHERE username=? AND password=?', (u, hp)).fetchone():
            st.session_state.user = u
            st.session_state.app_state = "main"
            st.rerun()
        else: st.error("عذراً، تأكد من بياناتك")
    st.write("---")
    if st.button("حساب جديد"): 
        st.session_state.app_state = "signup"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# واجهة التسجيل (حل مشكلة الاسم مأخوذ)
elif st.session_state.app_state == "signup":
    st.markdown('<div class="auth-box">', unsafe_allow_html=True)
    nu = st.text_input("اختر اسم مستخدم")
    np = st.text_input("اختر كلمة مرور", type="password")
    if st.button("تأكيد التسجيل"):
        conn = sqlite3.connect(DB_NAME)
        try:
            hp = hashlib.sha256(np.encode()).hexdigest()
            conn.execute('INSERT INTO users VALUES (?,?)', (nu, hp))
            conn.commit()
            st.success("تم بنجاح! يمكنك الدخول.")
            st.session_state.app_state = "login"
            st.rerun()
        except sqlite3.IntegrityError:
            st.error("⚠️ هذا الاسم مأخوذ مسبقاً! انتبه واختر اسماً آخر.")
    if st.button("العودة"): 
        st.session_state.app_state = "login"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# الواجهة الرئيسية
elif st.session_state.app_state == "main":
    col_input, col_display = st.columns([1, 2])
    
    with col_input:
        st.markdown(f"*مرحباً بك، {st.session_state.user}*")
        selected_s = st.multiselect("صف حالتك بدقة:", list(MEDICAL_ENGINE.keys()))
        location = get_geolocation() # تحديد تلقائي للموقع
        
        if st.button("بدء الفحص 🔍"): # تم تعديل النص هنا بناءً على طلبك
            if selected_s and location:
                st.session_state.active_diag = selected_s
                st.session_state.user_loc = location
            else: st.warning("يرجى تفعيل الـ GPS واختيار عرض واحد على الأقل")

    with col_display:
        if "active_diag" in st.session_state:
            u_lat = st.session_state.user_loc['coords']['latitude']
            u_lon = st.session_state.user_loc['coords']['longitude']
            
            # عرض تفاصيل التشخيص الأول
            primary = st.session_state.active_diag[0]
            data = MEDICAL_ENGINE[primary]
            
            st.markdown(f"""
            <div style="background:#0f0f0f; padding:20px; border-radius:12px; border:1px solid #40E0D022">
                <h2 style="color:#40E0D0; margin:0;">التشخيص: {data['diag']}</h2>
                <p style="margin:5px 0;">نسبة الاحتمالية: <b style="color:#40E0D0">{data['prob']}</b></p>
                <hr style="opacity:0.1">
                <p><b>التخصص المطلوب:</b> {data['spec']}</p>
                <p><b>السبب الطبي:</b> {data['reason']}</p>
                {"<span class='emergency-tag'>⚠️ حالة طوارئ - توجه فوراً</span>" if data['em'] else ""}
            </div>
            """, unsafe_allow_html=True)
            
            # فرز الأطباء
            doc_results = []
            for d in DOCTORS_BAGHDAD:
                dist = calculate_dist(u_lat, u_lon, d['lat'], d['lon'])
                # أولوية التخصص المطابق
                priority = 2 if d['spec'] == data['spec'] else (1 if d['spec'] == "طوارئ" else 0)
                doc_results.append({"doc": d, "dist": dist, "priority": priority})
            
            doc_results.sort(key=lambda x: (-x['priority'], x['dist']))
            
            st.write("---")
            st.subheader("الأطباء المقترحون في بغداد:")
            for item in doc_results:
                doc = item['doc']
                st.markdown(f"""
                <div class="doc-card">
                    <div style="display:flex; justify-content:space-between">
                        <b style="color:#40E0D0">{doc['name']}</b>
                        <span>📍 {doc['area']}</span>
                    </div>
                    <div style="font-size:13px; opacity:0.8">
                        {doc['spec']} | يبعد عنك: {item['dist']:.1f} كم
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"تأكيد الموعد مع {doc['name']}", key=doc['name']):
                    st.success(f"تم حجز موعدك مع {doc['name']} بنجاح.")

    if st.sidebar.button("تسجيل خروج"):
        st.session_state.app_state = "login"
        st.rerun()
