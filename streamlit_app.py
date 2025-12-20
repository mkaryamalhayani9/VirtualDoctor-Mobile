import streamlit as st
import sqlite3
import hashlib
import math
from streamlit_js_eval import get_geolocation

# --- 1. التصميم البصري الزمردي الكلاسيكي ---
st.set_page_config(page_title="Al Doctor Premium", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Tajawal:wght@400;700&display=swap');
    * { font-family: 'Tajawal', sans-serif; direction: rtl; }
    .stApp { background: #050505; color: #e0e0e0; }
    
    .classic-logo { 
        font-family: 'Playfair Display', serif; 
        color: #40E0D0; text-align: center; font-size: 45px; 
        text-shadow: 0 0 15px rgba(64, 224, 208, 0.2); margin-bottom: 25px;
    }

    /* تصغير مساحة الكتابة والحقول لتبدو أنيقة */
    .auth-box, .diag-box { 
        max-width: 380px; margin: auto; padding: 25px; 
        background: #0d0d0d; border-radius: 15px; 
        border: 1px solid #40E0D022; box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    
    .stTextInput > div > div > input { 
        background-color: #121212 !important; color: #40E0D0 !important; 
        border: 1px solid #40E0D033 !important; text-align: center; font-size: 14px;
    }

    .doc-card { 
        background: #0d0d0d; padding: 15px; border-radius: 10px; 
        border-right: 4px solid #40E0D0; margin-bottom: 12px;
        border: 1px solid #ffffff05; max-width: 500px; margin-right: auto; margin-left: auto;
    }
    
    .stButton>button { 
        background: linear-gradient(135deg, #1d4e4a 0%, #40E0D0 100%); 
        color: #000 !important; border: none; font-weight: bold; width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إدارة قاعدة البيانات ---
def init_db():
    conn = sqlite3.connect("al_doctor_final_v5.db")
    conn.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
    conn.close()

init_db()

# --- 3. قاعدة البيانات الطبية الموسعة (بغداد) ---
MEDICAL_DB = {
    "ألم ضاغط في الصدر": {"diag": "ذبحة صدرية", "prob": "94%", "spec": "اختصاصي أمراض القلب", "em": True, "reason": "احتمال انسداد شرياني"},
    "خدر في جهة واحدة من الجسم": {"diag": "سكتة دماغية", "prob": "96%", "spec": "اختصاصي جملة عصبية", "em": True, "reason": "توقف تدفق الدم للدماغ"},
    "ألم أسفل البطن جهة اليمين": {"diag": "التهاب الزائدة", "prob": "89%", "spec": "اختصاصي جراحة عامة", "em": True, "reason": "خطر الانفجار والتسمم"},
    "صداع نصفي شديد مع غثيان": {"diag": "شقيقة حادة", "prob": "91%", "spec": "اختصاصي مخ وأعصاب", "em": False, "reason": "اضطراب وعائي عصبي"},
    "تبول متكرر مع عطش وجفاف": {"diag": "سكري غير منتظم", "prob": "85%", "spec": "اختصاصي غدد صماء", "em": False, "reason": "اضطراب مستوى الأنسولين"},
    "ألم مفاجئ وشديد في الظهر": {"diag": "مغص كلوي", "prob": "88%", "spec": "اختصاصي مسالك بولية", "em": False, "reason": "انسداد مجرى البول بحصى"},
    "طفح جلدي قشري فضي": {"diag": "صدفية", "prob": "93%", "spec": "اختصاصي جلدية", "em": False, "reason": "خلل في المناعة الذاتية"},
    "صعوبة تنفس مع صفير": {"diag": "نوبة ربو", "prob": "90%", "spec": "اختصاصي أمراض صدرية", "em": True, "reason": "تضيق القصبات الهوائية"},
    "طنين مستمر ودوار": {"diag": "مرض منيير", "prob": "82%", "spec": "اختصاصي أذن وحنجرة", "em": False, "reason": "اضطراب سوائل الأذن الداخلية"},
    "ألم لثة حاد مع نزيف": {"diag": "التهاب الأنسجة الداعمة", "prob": "95%", "spec": "طبيب أسنان اختصاص لثة", "em": False, "reason": "عدوى بكتيرية عميقة"},
    "خمول وتعب مستمر": {"diag": "خمول الغدة الدرقية", "prob": "87%", "spec": "اختصاصي غدد صماء", "em": False, "reason": "نقص إفراز هرمون الثايروكسين"},
    "ألم مفاصل صباحي": {"diag": "روماتويد", "prob": "84%", "spec": "اختصاصي مفاصل وروماتزم", "em": False, "reason": "التهاب مناعي للمفاصل"},
    "حرقة خلف القص": {"diag": "ارتجاع مريئي", "prob": "90%", "spec": "اختصاصي جهاز هضمي", "em": False, "reason": "ضعف عضلة المريء العاصرة"},
    "رعشة غير إرادية": {"diag": "اشتباه باركنسون", "prob": "78%", "spec": "اختصاصي جملة عصبية", "em": False, "reason": "نقص مادة الدوبامين"},
    "سعال جاف لأكثر من شهر": {"diag": "سعال تحسسي", "prob": "80%", "spec": "اختصاصي أمراض صدرية", "em": False, "reason": "فرط تحسس الممرات الهوائية"}
}

DOCTORS_BAGHDAD = [
    {"name": "د. علي الركابي", "spec": "اختصاصي أمراض القلب", "area": "المنصور", "lat": 33.325, "lon": 44.348},
    {"name": "د. عمر الجبوري", "spec": "اختصاصي جملة عصبية", "area": "الحارثية", "lat": 33.322, "lon": 44.358},
    {"name": "د. مريم القيسي", "spec": "اختصاصي جراحة عامة", "area": "الكرادة", "lat": 33.300, "lon": 44.420},
    {"name": "د. سارة لؤي", "spec": "اختصاصي جلدية", "area": "زيونة", "lat": 33.332, "lon": 44.455},
    {"name": "مستشفى مدينة الطب", "spec": "طوارئ", "area": "باب المعظم", "lat": 33.350, "lon": 44.385},
    {"name": "د. ليث الحسيني", "spec": "اختصاصي غدد صماء", "area": "شارع فلسطين", "lat": 33.345, "lon": 44.430},
    {"name": "د. نور الدين", "spec": "اختصاصي مفاصل وروماتزم", "area": "الجادرية", "lat": 33.280, "lon": 44.390}
]

# --- 4. معالجة الصفحات ---
if "page" not in st.session_state: st.session_state.page = "login"

def calculate_dist(lat1, lon1, lat2, lon2):
    try:
        # Haversine formula لدقة الـ GPS في بغداد
        R = 6371.0 
        dlat = math.radians(float(lat1) - float(lat2))
        dlon = math.radians(float(lon1) - float(lon2))
        a = math.sin(dlat / 2)*2 + math.cos(math.radians(float(lat1))) * math.cos(math.radians(float(lat2))) * math.sin(dlon / 2)*2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c
    except: return 999

# --- 5. الواجهات ---
st.markdown('<div class="classic-logo">Al Doctor</div>', unsafe_allow_html=True)

if st.session_state.page == "login":
    st.markdown('<div class="auth-box">', unsafe_allow_html=True)
    u = st.text_input("اسم المستخدم")
    p = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        conn = sqlite3.connect("al_doctor_final_v5.db")
        hp = hashlib.sha256(p.encode()).hexdigest()
        if conn.execute('SELECT * FROM users WHERE username=? AND password=?', (u, hp)).fetchone():
            st.session_state.user = u
            st.session_state.page = "main"
            st.rerun()
        else: st.error("خطأ في البيانات")
    st.write("---")
    if st.button("إنشاء حساب"): 
        st.session_state.page = "signup"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "signup":
    st.markdown('<div class="auth-box">', unsafe_allow_html=True)
    nu = st.text_input("اسم المستخدم الجديد")
    np = st.text_input("كلمة المرور الجديدة", type="password")
    if st.button("تأكيد"):
        conn = sqlite3.connect("al_doctor_final_v5.db")
        try:
            hp = hashlib.sha256(np.encode()).hexdigest()
            conn.execute('INSERT INTO users VALUES (?,?)', (nu, hp))
            conn.commit()
            st.success("تم التسجيل!")
            st.session_state.page = "login"
            st.rerun()
        except: st.error("⚠️ هذا الاسم مأخوذ مسبقاً!")
    if st.button("رجوع"):
        st.session_state.page = "login"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "main":
    st.markdown(f"<p style='text-align:center'>طاب يومك {st.session_state.user}</p>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="diag-box">', unsafe_allow_html=True)
        selected = st.multiselect("اختر الأعراض:", list(MEDICAL_DB.keys()))
        loc = get_geolocation()
        if st.button("بدء الفحص 🔍"):
            if selected and loc:
                st.session_state.diag = selected
                st.session_state.u_loc = loc
            else: st.warning("يرجى اختيار الأعراض وتفعيل الموقع")
        st.markdown('</div>', unsafe_allow_html=True)

    if "diag" in st.session_state:
        u_lat = st.session_state.u_loc['coords']['latitude']
        u_lon = st.session_state.u_loc['coords']['longitude']
        
        info = MEDICAL_DB[st.session_state.diag[0]]
        
        st.write("---")
        st.markdown(f"""
        <div style="text-align:center; padding:15px; background:#0f0f0f; border-radius:10px; border:1px solid #40E0D033; max-width:600px; margin:auto">
            <h3 style="color:#40E0D0">التشخيص المحتمل: {info['diag']}</h3>
            <p>الاحتمالية: <b>{info['prob']}</b> | الطبيب: <b>{info['spec']}</b></p>
            <p style="font-size:12px; color:#888">{info['reason']}</p>
        </div>
        """, unsafe_allow_html=True)

        # ترتيب الأطباء
        results = []
        for d in DOCTORS_BAGHDAD:
            dist = calculate_dist(u_lat, u_lon, d['lat'], d['lon'])
            priority = 1 if d['spec'] == info['spec'] or d['spec'] == "طوارئ" else 0
            results.append({"d": d, "dist": dist, "p": priority})
        
        results.sort(key=lambda x: (-x['p'], x['dist']))
        
        st.write("### الأطباء المقترحون في بغداد:")
        for item in results:
            doc = item['d']
            st.markdown(f"""
            <div class="doc-card">
                <div style="display:flex; justify-content:space-between">
                    <b style="color:#40E0D0">{doc['name']}</b>
                    <span>📍 {doc['area']}</span>
                </div>
                <div style="font-size:12px">
                    {doc['spec']} | المسافة: {item['dist']:.2f} كم
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"تأكيد الموعد مع {doc['name']}", key=doc['name']):
                st.success(f"تم حجز موعدك بنجاح.")

    if st.sidebar.button("خروج"):
        st.session_state.page = "login"
        st.rerun()
