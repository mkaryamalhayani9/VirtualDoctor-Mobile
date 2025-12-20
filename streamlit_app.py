import streamlit as st
import sqlite3
import hashlib
import math
import random
from datetime import datetime, timedelta
from streamlit_js_eval import get_geolocation

# --- 1. التصميم البصري الراقي ---
st.set_page_config(page_title="Al Doctor Premium", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Tajawal:wght@400;700&display=swap');
    * { font-family: 'Tajawal', sans-serif; direction: rtl; }
    .stApp { background: #050505; color: #e0e0e0; }
    .classic-logo { 
        font-family: 'Playfair Display', serif; 
        color: #40E0D0; text-align: center; font-size: 40px; margin-bottom: 20px;
    }
    .auth-box, .diag-box { 
        max-width: 380px; margin: auto; padding: 25px; 
        background: #0d0d0d; border-radius: 15px; 
        border: 1px solid #40E0D022; box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    .doc-card { 
        background: #0d0d0d; padding: 15px; border-radius: 10px; 
        border-right: 4px solid #40E0D0; margin-bottom: 12px;
        border: 1px solid #ffffff05; max-width: 550px; margin: auto;
    }
    .emergency-pulse {
        color: #ff4b4b; font-weight: bold; animation: pulse 1s infinite;
    }
    @keyframes pulse { 0% {opacity: 1;} 50% {opacity: 0.5;} 100% {opacity: 1;} }
    .stButton>button { 
        background: linear-gradient(135deg, #1d4e4a 0%, #40E0D0 100%); 
        color: #000 !important; border: none; font-weight: bold; width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. تهيئة البيانات والمواعيد ---
if "doctors" not in st.session_state:
    # توليد مواعيد وهمية عشوائية لكل طبيب
    def generate_slots():
        now = datetime.now()
        return [(now + timedelta(minutes=random.randint(10, 180))).strftime("%H:%M") for _ in range(3)]

    st.session_state.doctors = [
        {"id": 1, "name": "د. علي الركابي", "spec": "اختصاصي أمراض القلب", "area": "المنصور", "lat": 33.325, "lon": 44.348, "slots": sorted(generate_slots())},
        {"id": 2, "name": "د. عمر الجبوري", "spec": "اختصاصي جملة عصبية", "area": "الحارثية", "lat": 33.322, "lon": 44.358, "slots": sorted(generate_slots())},
        {"id": 3, "name": "د. مريم القيسي", "spec": "اختصاصي جراحة عامة", "area": "الكرادة", "lat": 33.300, "lon": 44.420, "slots": sorted(generate_slots())},
        {"id": 4, "name": "د. سارة لؤي", "spec": "اختصاصي جلدية", "area": "زيونة", "lat": 33.332, "lon": 44.455, "slots": sorted(generate_slots())},
        {"id": 5, "name": "مركز طوارئ بغداد", "spec": "طوارئ", "area": "باب المعظم", "lat": 33.350, "lon": 44.385, "slots": ["فوري"]},
    ]

# قاعدة البيانات الطبية
MEDICAL_DB = {
    "ألم حاد في الصدر": {"diag": "اشتباه ذبحة صدرية", "spec": "اختصاصي أمراض القلب", "em": True},
    "ضعف مفاجئ في النطق": {"diag": "اشتباه سكتة دماغية", "spec": "اختصاصي جملة عصبية", "em": True},
    "ألم أسفل البطن (يمين)": {"diag": "التهاب زائدة دودية", "spec": "اختصاصي جراحة عامة", "em": True},
    "طفح جلدي شديد": {"diag": "تحسس جلدي حاد", "spec": "اختصاصي جلدية", "em": False},
}

# --- 3. وظائف النظام ---
def get_db():
    conn = sqlite3.connect("al_doctor_v6.db")
    conn.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
    return conn

def calculate_dist(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat, dlon = math.radians(float(lat1)-float(lat2)), math.radians(float(lon1)-float(lon2))
    a = math.sin(dlat/2)*2 + math.cos(math.radians(float(lat1)))*math.cos(math.radians(float(lat2)))*math.sin(dlon/2)*2
    return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1-a)))

# --- 4. معالجة الصفحات ---
if "page" not in st.session_state: st.session_state.page = "login"

st.markdown('<div class="classic-logo">Al Doctor</div>', unsafe_allow_html=True)

# واجهة الدخول
if st.session_state.page == "login":
    st.markdown('<div class="auth-box">', unsafe_allow_html=True)
    u = st.text_input("اسم المستخدم")
    p = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        conn = get_db()
        hp = hashlib.sha256(p.encode()).hexdigest()
        if conn.execute('SELECT * FROM users WHERE username=? AND password=?', (u, hp)).fetchone():
            st.session_state.user = u
            st.session_state.page = "main"
            st.rerun()
        else: st.error("بيانات الدخول غير صحيحة")
    st.write("---")
    if st.button("إنشاء حساب جديد"): 
        st.session_state.page = "signup"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# واجهة التسجيل (حل مشكلة الاسم مأخوذ)
elif st.session_state.page == "signup":
    st.markdown('<div class="auth-box">', unsafe_allow_html=True)
    nu = st.text_input("اختر اسم مستخدم مميز")
    np = st.text_input("كلمة المرور", type="password")
    
    if nu: # فحص استباقي للاسم
        conn = get_db()
        if conn.execute('SELECT 1 FROM users WHERE username=?', (nu,)).fetchone():
            st.error("⚠️ هذا الاسم مأخوذ! يرجى إضافة أرقام أو تغيير الاسم.")
    
    if st.button("تأكيد التسجيل"):
        conn = get_db()
        try:
            hp = hashlib.sha256(np.encode()).hexdigest()
            conn.execute('INSERT INTO users VALUES (?,?)', (nu, hp))
            conn.commit()
            st.success("تم التسجيل بنجاح! توجه للدخول.")
            st.session_state.page = "login"
            st.rerun()
        except: st.error("حدث خطأ، ربما الاسم مأخوذ بالفعل.")
    if st.button("رجوع"):
        st.session_state.page = "login"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# الواجهة الرئيسية
elif st.session_state.page == "main":
    with st.container():
        st.markdown('<div class="diag-box">', unsafe_allow_html=True)
        selected = st.selectbox("بماذا تشعر الآن؟", ["اختر الأعراض..."] + list(MEDICAL_DB.keys()))
        loc = get_geolocation()
        if st.button("بدء الفحص 🔍"):
            if selected != "اختر الأعراض..." and loc:
                st.session_state.active_case = selected
                st.session_state.u_loc = loc
            else: st.warning("يرجى تفعيل الموقع واختيار الحالة")
        st.markdown('</div>', unsafe_allow_html=True)

    if "active_case" in st.session_state:
        u_lat = st.session_state.u_loc['coords']['latitude']
        u_lon = st.session_state.u_loc['coords']['longitude']
        case_info = MEDICAL_DB[st.session_state.active_case]
        
        if case_info['em']:
            st.markdown('<p class="emergency-pulse" style="text-align:center">⚠️ حالة طوارئ: الأولوية للأقرب موعداً</p>', unsafe_allow_html=True)
        
        # ترتيب الأطباء بناءً على منطق (الطوارئ vs المسافة)
        results = []
        for d in st.session_state.doctors:
            dist = calculate_dist(u_lat, u_lon, d['lat'], d['lon'])
            # ترتيب الحالات: إذا طوارئ، الطبيب الذي لديه موعد أقرب يأخذ أولوية أعلى
            is_correct_spec = (d['spec'] == case_info['spec'] or d['spec'] == "طوارئ")
            results.append({"d": d, "dist": dist, "spec_match": is_correct_spec})
        
        # فرز: الاختصاص أولاً، ثم المسافة
        results.sort(key=lambda x: (-x['spec_match'], x['dist']))

        st.write("### الأطباء المتاحون حالياً:")
        for item in results:
            doc = item['d']
            st.markdown(f"""
            <div class="doc-card">
                <div style="display:flex; justify-content:space-between">
                    <b style="color:#40E0D0">{doc['name']}</b>
                    <span style="font-size:12px">📍 {doc['area']} ({item['dist']:.1f} كم)</span>
                </div>
                <p style="font-size:13px; margin:5px 0;">{doc['spec']}</p>
                <div style="display:flex; gap:10px; margin-top:10px">
                    {" ".join([f'<span style="background:#1a1a1a; padding:3px 8px; border-radius:5px; border:1px solid #40E0D055; font-size:11px">🕒 {s}</span>' for s in doc['slots']])}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            chosen_slot = st.selectbox(f"اختر موعداً مع {doc['name']}:", doc['slots'], key=f"slot_{doc['id']}")
            if st.button(f"حجز موعد {chosen_slot}", key=f"btn_{doc['id']}"):
                st.balloons()
                st.success(f"تم حجز موعدك الساعة {chosen_slot} مع {doc['name']}. يرجى التوجه للعيادة.")

    if st.sidebar.button("خروج"):
        st.session_state.page = "login"
        st.rerun()
