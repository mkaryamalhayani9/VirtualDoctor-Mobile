import streamlit as st
import sqlite3
import hashlib
import math
from datetime import datetime, time
from streamlit_js_eval import get_geolocation

# --- 1. التصميم البصري (فيروزي وأسود ملكي) ---
st.set_page_config(page_title="Al Doctor Premium", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Tajawal:wght@400;700&display=swap');
    * { font-family: 'Tajawal', sans-serif; direction: rtl; }
    .stApp { background: #050505; color: #e0e0e0; }
    .classic-logo { 
        font-family: 'Playfair Display', serif; color: #40E0D0; 
        text-align: center; font-size: 45px; margin-bottom: 5px;
    }
    .auth-box { 
        max-width: 380px; margin: auto; padding: 20px; 
        background: #0d0d0d; border-radius: 12px; border: 1px solid #40E0D033; 
    }
    .stTextInput > div > div > input, .stDateInput > div > div > input { 
        background-color: #121212 !important; color: #40E0D0 !important; text-align: center; border-radius: 8px; 
    }
    .doc-card { 
        background: #0d0d0d; padding: 20px; border-radius: 15px; 
        border-right: 6px solid #40E0D0; margin-bottom: 15px; border: 1px solid #ffffff05;
    }
    .stButton>button { 
        background: linear-gradient(135deg, #1d4e4a 0%, #40E0D0 100%); 
        color: #000 !important; font-weight: bold; width: 100%; border: none; border-radius: 8px;
    }
    .emergency-tag { background: #ff4b4b; color: white; padding: 4px 10px; border-radius: 5px; font-size: 12px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إدارة البيانات ---
def init_db():
    conn = sqlite3.connect("al_doctor_pro_v8.db")
    conn.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS appointments (id INTEGER PRIMARY KEY, user TEXT, doc TEXT, date TEXT, time TEXT)')
    conn.commit()
    conn.close()

init_db()

# --- 3. قاعدة البيانات الطبية (25 حالة) ---
MEDICAL_DB = {
    "ألم ضاغط حاد في الصدر": {"diag": "ذبحة صدرية", "prob": "94%", "spec": "اختصاصي أمراض القلب", "em": True},
    "ثقل في الكلام وتدلي الوجه": {"diag": "سكتة دماغية", "prob": "96%", "spec": "اختصاصي جملة عصبية", "em": True},
    "ألم أسفل البطن يميناً": {"diag": "التهاب الزائدة", "prob": "89%", "spec": "اختصاصي جراحة عامة", "em": True},
    "ضيق تنفس مع ازرقاق": {"diag": "فشل تنفسي حاد", "prob": "92%", "spec": "اختصاصي أمراض صدرية", "em": True},
    "صداع نصفي شديد": {"diag": "شقيقة حادة", "prob": "91%", "spec": "اختصاصي مخ وأعصاب", "em": False},
    "عطش شديد وتبول متكرر": {"diag": "سكري", "prob": "85%", "spec": "اختصاصي غدد صماء", "em": False},
    "ألم مفاجئ في الخاصرة": {"diag": "مغص كلوي", "prob": "88%", "spec": "اختصاصي مسالك بولية", "em": False},
    "طفح جلدي فضي": {"diag": "صدفية", "prob": "93%", "spec": "اختصاصي جلدية", "em": False},
    "طنين ودوار مستمر": {"diag": "مرض منيير", "prob": "82%", "spec": "اختصاصي أذن وحنجرة", "em": False},
    "نزيف لثة حاد": {"diag": "التهاب دواعم الأسنان", "prob": "95%", "spec": "طبيب أسنان اختصاص", "em": False},
    "خمول وتعب مزمن": {"diag": "خمول الغدة الدرقية", "prob": "87%", "spec": "اختصاصي غدد صماء", "em": False},
    "ألم مفاصل صباحي": {"diag": "روماتويد", "prob": "84%", "spec": "اختصاصي مفاصل", "em": False},
    "حرقة مريء مستمرة": {"diag": "ارتجاع مريئي", "prob": "90%", "spec": "اختصاصي جهاز هضمي", "em": False},
    "رعشة لا إرادية": {"diag": "اشتباه باركنسون", "prob": "78%", "spec": "اختصاصي جملة عصبية", "em": False},
    "سعال لأكثر من شهر": {"diag": "سعال تحسسي", "prob": "80%", "spec": "اختصاصي صدرية", "em": False},
    "فقدان رؤية مفاجئ": {"diag": "انفصال شبكية", "prob": "98%", "spec": "اختصاصي عيون", "em": True},
    "ألم خصية مفاجئ": {"diag": "التواء الخصية", "prob": "95%", "spec": "جراحة مسالك", "em": True},
    "تورم ساق مؤلم": {"diag": "جلطة وريدية", "prob": "82%", "spec": "جراحة أوعية", "em": True},
    "اكتئاب وحزن مستمر": {"diag": "اكتئاب حاد", "prob": "75%", "spec": "طبيب نفسي", "em": False},
    "تأخر نطق الطفل": {"diag": "اضطراب نمو", "prob": "70%", "spec": "اختصاصي أطفال", "em": False},
    "رعاف أنف حاد": {"diag": "نزيف وعائي", "prob": "90%", "spec": "أذن وحنجرة", "em": True},
    "تشنج رقبة وحرارة": {"diag": "اشتباه سحايا", "prob": "85%", "spec": "باطنية/طوارئ", "em": True},
    "ألم تبول شديد": {"diag": "التهاب مثانة", "prob": "92%", "spec": "مسالك بولية", "em": False},
    "اصفرار الجلد": {"diag": "التهاب كبد", "prob": "88%", "spec": "اختصاصي كبد", "em": False},
    "كسر عظمي ظاهر": {"diag": "كسر مضاعف", "prob": "100%", "spec": "اختصاصي عظام", "em": True}
}

DOCTORS = [
    {"id": 1, "name": "د. علي الركابي", "spec": "اختصاصي أمراض القلب", "area": "المنصور", "lat": 33.325, "lon": 44.348},
    {"name": "د. عمر الجبوري", "spec": "اختصاصي جملة عصبية", "area": "الحارثية", "lat": 33.322, "lon": 44.358},
    {"name": "د. مريم القيسي", "spec": "اختصاصي جراحة عامة", "area": "الكرادة", "lat": 33.300, "lon": 44.420},
    {"name": "د. سارة لؤي", "spec": "اختصاصي جلدية", "area": "زيونة", "lat": 33.332, "lon": 44.455},
    {"name": "مستشفى مدينة الطب", "spec": "طوارئ", "area": "باب المعظم", "lat": 33.350, "lon": 44.385},
]

# --- 4. المنطق الوظيفي ---
if "view" not in st.session_state: st.session_state.view = "login"

def calculate_dist(lat1, lon1, lat2, lon2):
    try: return math.sqrt((float(lat1)-float(lat2))*2 + (float(lon1)-float(lon2))*2) * 111
    except: return 999

st.markdown('<div class="classic-logo">Al Doctor</div>', unsafe_allow_html=True)

# واجهة الدخول والتسجيل
if st.session_state.view in ["login", "signup"]:
    st.markdown('<div class="auth-box">', unsafe_allow_html=True)
    u = st.text_input("اسم المستخدم")
    p = st.text_input("كلمة المرور", type="password")
    
    if st.session_state.view == "login":
        if st.button("دخول"):
            conn = sqlite3.connect("al_doctor_pro_v8.db")
            hp = hashlib.sha256(p.encode()).hexdigest()
            if conn.execute('SELECT * FROM users WHERE username=? AND password=?', (u, hp)).fetchone():
                st.session_state.user, st.session_state.view = u, "app"
                st.rerun()
            else: st.error("خطأ في البيانات")
        st.write("---")
        if st.button("حساب جديد"): st.session_state.view = "signup"; st.rerun()
    
    else: # Signup
        if st.button("تأكيد التسجيل والدخول"):
            conn = sqlite3.connect("al_doctor_pro_v8.db")
            try:
                hp = hashlib.sha256(p.encode()).hexdigest()
                conn.execute('INSERT INTO users VALUES (?,?)', (u, hp))
                conn.commit()
                st.session_state.user, st.session_state.view = u, "app"
                st.rerun()
            except: st.error("⚠️ هذا الاسم مأخوذ!")
        if st.button("رجوع"): st.session_state.view = "login"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# واجهة التطبيق
elif st.session_state.view == "app":
    st.sidebar.write(f"المستخدم: {st.session_state.user}")
    if st.sidebar.button("خروج"): st.session_state.view = "login"; st.rerun()

    st.markdown('<div class="auth-box" style="max-width:500px">', unsafe_allow_html=True)
    selected = st.selectbox("بماذا تشعر الآن؟", ["اختر الأعراض..."] + list(MEDICAL_DB.keys()))
    loc = get_geolocation()
    if st.button("بدء الفحص 🔍"):
        if selected != "اختر الأعراض..." and loc:
            st.session_state.case = selected
            st.session_state.loc = loc
    st.markdown('</div>', unsafe_allow_html=True)

    if "case" in st.session_state:
        u_lat = st.session_state.loc['coords']['latitude']
        u_lon = st.session_state.loc['coords']['longitude']
        case = MEDICAL_DB[st.session_state.case]
        
        st.markdown(f"""
        <div style="text-align:center; padding:15px; border:1px solid #40E0D033; border-radius:10px; margin-top:20px">
            <h3 style="color:#40E0D0">التشخيص: {case['diag']}</h3>
            <p>المطلوب: <b>{case['spec']}</b></p>
            {"<span class='emergency-tag'>⚠️ حالة طوارئ فورية</span>" if case['em'] else ""}
        </div>
        """, unsafe_allow_html=True)

        results = []
        for d in DOCTORS:
            dist = calculate_dist(u_lat, u_lon, d['lat'], d['lon'])
            match = 1 if d['spec'] == case['spec'] or d['spec'] == "طوارئ" else 0
            results.append({"d": d, "dist": dist, "match": match})
        results.sort(key=lambda x: (-x['match'], x['dist']))

        st.write("### حجز موعد دقيق:")
        for item in results:
            doc = item['d']
            with st.container():
                st.markdown(f"""
                <div class="doc-card">
                    <div style="display:flex; justify-content:space-between">
                        <b style="color:#40E0D0; font-size:18px">{doc['name']}</b>
                        <span>📍 {doc['area']} ({item['dist']:.1f} كم)</span>
                    </div>
                    <p style="font-size:14px">{doc['spec']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # اختيار التاريخ والوقت بدقة
                c1, c2 = st.columns(2)
                with c1: d_date = st.date_input("اختر التاريخ", key=f"date_{doc['name']}")
                with c2: d_time = st.time_input("اختر الساعة", time(10, 0), key=f"time_{doc['name']}")
                
                if st.button(f"تأكيد الحجز ليوم {d_date} الساعة {d_time}", key=f"btn_{doc['name']}"):
                    st.success(f"تم حجز موعدك مع {doc['name']} بنجاح. سنرسل لك تذكرة الحجز.")
                    st.balloons()
