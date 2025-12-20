import streamlit as st
import sqlite3
import hashlib
import math
import random
from datetime import datetime, timedelta
from streamlit_js_eval import get_geolocation

# --- 1. التصميم البصري ---
st.set_page_config(page_title="AI Doctor Baghdad Pro", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    * { font-family: 'Tajawal', sans-serif; direction: rtl; }
    .stApp { background: #0e1117; color: #ffffff; }
    .portal-box { max-width: 600px; margin: auto; padding: 30px; background: #1a1c23; border-radius: 20px; border: 1px solid #00d2ff55; box-shadow: 0 10px 25px rgba(0,0,0,0.3); }
    .doc-card { background: #252932; padding: 20px; border-radius: 15px; border-right: 8px solid #00d2ff; margin-bottom: 15px; }
    .emergency-card { border-right-color: #ff4b4b; background: #2d1b1b; }
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; font-weight: bold; transition: 0.3s; }
    .link-btn { background: none; border: none; color: #00d2ff; text-decoration: underline; cursor: pointer; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. قاعدة البيانات ---
def init_db():
    conn = sqlite3.connect("baghdad_health_v3.db")
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS bookings (username TEXT, doctor TEXT, date TEXT, time TEXT)')
    conn.commit()
    conn.close()

init_db()

# --- 3. البيانات الطبية (20 تشخيص مفصل) ---
MEDICAL_DB = {
    "ألم شديد في الصدر يمتد للفك": {"diag": "نوبة قلبية حادة (احتشاء)", "spec": "أمراض القلب", "emergency": True},
    "ضيق تنفس مع ازرقاق الشفاه": {"diag": "فشل تنفسي حاد", "spec": "طوارئ/صدرية", "emergency": True},
    "تنميل نصف الوجه وعدم القدرة على الابتسام": {"diag": "اشتباه جلطة دماغية", "spec": "مخ وأعصاب", "emergency": True},
    "خمول شديد مع اصفرار العين": {"diag": "التهاب كبد فيروسي", "spec": "باطنية/كبد", "emergency": False},
    "ألم حاد في الجانب الأيمن السفلي للبطن": {"diag": "اشتباه التهاب الزائدة الدودية", "spec": "جراحة عامة", "emergency": True},
    "عطش شديد وتبول ليلي متكرر": {"diag": "داء السكري (نوع أول أو ثاني)", "spec": "غدد صماء", "emergency": False},
    "صداع نصفي مع رؤية خطوط متعرجة": {"diag": "شقيقة مع هالة (Migraine)", "spec": "جملة عصبية", "emergency": False},
    "حكة شديدة وبقع حمراء دائرية": {"diag": "إكزيما أو فطريات جلدية", "spec": "جلدية", "emergency": False},
    "ألم عند التبول مع ألم في الخاصرة": {"diag": "التهاب مجاري بولية أو حصى", "spec": "مسالك بولية", "emergency": False},
    "طنين في الأذن مع فقدان توازن": {"diag": "مرض منيير (الأذن الداخلية)", "spec": "أنف وأذن وحنجرة", "emergency": False},
    "كآبة مستمرة وفقدان الرغبة في الأنشطة": {"diag": "اضطراب اكتئاب حاد", "spec": "طب نفسي", "emergency": False},
    "ألم وتورم في مفصل الإبهام": {"diag": "داء النقرس", "spec": "مفاصل", "emergency": False},
    "سعال جاف مستمر لأكثر من 3 أسابيع": {"diag": "تحسس قصبي أو اشتباه سل", "spec": "أمراض صدرية", "emergency": False},
    "نزيف لثة متكرر ورائحة فم كريهة": {"diag": "التهاب دواعم الأسنان", "spec": "أسنان", "emergency": False},
    "تأخر في النطق عند الطفل (3 سنوات)": {"diag": "اضطراب طيف توحد أو ضعف سمع", "spec": "أطفال", "emergency": False},
    "رعشة في اليدين عند السكون": {"diag": "اشتباه بمرض باركنسون", "spec": "مخ وأعصاب", "emergency": False},
    "تساقط شعر شديد مع تعب وبرودة": {"diag": "خمول الغدة الدرقية", "spec": "غدد صماء", "emergency": False},
    "ألم حاد في الركبة عند الصعود": {"diag": "سوفان أو تمزق غضروفي", "spec": "عظام", "emergency": False},
    "حرقة خلف عظمة القص (المعدة)": {"diag": "ارتجاع مريئي حاد", "spec": "جهاز هضمي", "emergency": False},
    "صعوبة في التركيز ونسيان متكرر": {"diag": "بداية ألزهايمر أو نقص فيتامينات", "spec": "شيخوخة/أعصاب", "emergency": False}
}

DOCTORS_LIST = [
    {"name": "د. زيد (المنصور)", "spec": "أمراض القلب", "lat": 33.325, "lon": 44.348},
    {"name": "د. هند (الكرادة)", "spec": "جلدية", "lat": 33.300, "lon": 44.420},
    {"name": "مستشفى اليرموك (الطوارئ)", "spec": "طوارئ/صدرية", "lat": 33.310, "lon": 44.370},
    {"name": "د. باسم (الحارثية)", "spec": "مخ وأعصاب", "lat": 33.322, "lon": 44.358},
    {"name": "د. منى (شارع فلسطين)", "spec": "غدد صماء", "lat": 33.345, "lon": 44.430},
    {"name": "د. ليث (زيونة)", "spec": "مسالك بولية", "lat": 33.332, "lon": 44.455}
]

# --- 4. المنطق المساعد ---
def get_dist(lat1, lon1, lat2, lon2):
    return math.sqrt((lat1 - lat2)*2 + (lon1 - lon2)*2) * 111

def get_next_available_slot():
    # افتراضاً: المواعيد المتاحة تبدأ من غدٍ الساعة 10 صباحاً
    next_day = datetime.now() + timedelta(days=random.randint(1, 3))
    return next_day.strftime("%Y-%m-%d"), f"{random.randint(10, 18)}:00"

# --- 5. إدارة التنقل (التبديل التلقائي) ---
if "page" not in st.session_state: st.session_state.page = "login"
if "user" not in st.session_state: st.session_state.user = None

def switch_page(page_name):
    st.session_state.page = page_name
    st.rerun()

# --- 6. الواجهات ---

# واجهة تسجيل الدخول
if st.session_state.page == "login":
    st.markdown('<div class="portal-box">', unsafe_allow_html=True)
    st.header("تسجيل الدخول")
    u = st.text_input("اسم المستخدم")
    p = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        conn = sqlite3.connect("baghdad_health_v3.db")
        c = conn.cursor()
        hp = hashlib.sha256(p.encode()).hexdigest()
        c.execute('SELECT * FROM users WHERE username=? AND password=?', (u, hp))
        if c.fetchone():
            st.session_state.user = u
            switch_page("main")
        else: st.error("خطأ في البيانات")
        conn.close()
    st.write("ليس لديك حساب؟")
    if st.button("اضغط هنا لإنشاء حساب جديد"): switch_page("signup")
    st.markdown('</div>', unsafe_allow_html=True)

# واجهة التسجيل
elif st.session_state.page == "signup":
    st.markdown('<div class="portal-box">', unsafe_allow_html=True)
    st.header("إنشاء حساب جديد")
    nu = st.text_input("اختر اسم مستخدم")
    np = st.text_input("اختر كلمة مرور", type="password")
    if st.button("تأكيد التسجيل"):
        conn = sqlite3.connect("baghdad_health_v3.db")
        c = conn.cursor()
        try:
            hp = hashlib.sha256(np.encode()).hexdigest()
            c.execute('INSERT INTO users VALUES (?,?)', (nu, hp))
            conn.commit()
            st.success("تم التسجيل! يمكنك الآن الدخول.")
            switch_page("login")
        except: st.error("الاسم مأخوذ! اختر اسماً آخر.")
        conn.close()
    if st.button("العودة لتسجيل الدخول"): switch_page("login")
    st.markdown('</div>', unsafe_allow_html=True)

# الواجهة الرئيسية (التشخيص والحجز)
elif st.session_state.page == "main":
    st.title(f"مرحباً {st.session_state.user} - عيادة بغداد الذكية")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### اختر الأعراض")
        symptoms = st.multiselect("وصف الحالة:", list(MEDICAL_DB.keys()))
        loc = get_geolocation() # يتحدد تلقائياً
        
        if st.button("بدء التحليل الفوري 🔍"):
            if not symptoms: st.warning("اختر عرضاً أولاً")
            elif not loc: st.error("📍 يرجى تفعيل الموقع!")
            else:
                st.session_state.diag_results = symptoms
                st.session_state.user_loc = loc

    if "diag_results" in st.session_state:
        with col2:
            u_lat = st.session_state.user_loc['coords']['latitude']
            u_lon = st.session_state.user_loc['coords']['longitude']
            
            is_em = any(MEDICAL_DB[s]["emergency"] for s in st.session_state.diag_results)
            target_specs = [MEDICAL_DB[s]["spec"] for s in st.session_state.diag_results]
            
            st.subheader("التشخيص والأطباء المتاحون")
            
            # عرض الأطباء
            matched_docs = []
            for d in DOCTORS_LIST:
                dist = get_dist(u_lat, u_lon, d['lat'], d['lon'])
                score = 1 if d['spec'] in target_specs else 0
                if is_em and (d['spec'] == "أمراض القلب" or d['spec'] == "طوارئ/صدرية"): score = 2
                
                if score > 0 or is_em:
                    d['dist'] = dist
                    d['score'] = score
                    matched_docs.append(d)
            
            matched_docs.sort(key=lambda x: (-x['score'], x['dist']))
            
            for doc in matched_docs:
                type_class = "emergency-card" if doc['score'] >= 2 else ""
                date, time_slot = get_next_available_slot()
                
                with st.container():
                    st.markdown(f"""
                    <div class="doc-card {type_class}">
                        <h4>{doc['name']}</h4>
                        <p>الاختصاص: {doc['spec']} | 📍 المسافة: {doc['dist']:.1f} كم</p>
                        <p style="color:#00d2ff"><b>أقرب موعد متاح: {date} الساعة {time_slot}</b></p>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"حجز موعد مع {doc['name']}", key=doc['name']):
                        st.success(f"تم حجز موعدك بنجاح يوم {date} الساعة {time_slot}")

    if st.sidebar.button("تسجيل خروج"):
        st.session_state.user = None
        switch_page("login")
