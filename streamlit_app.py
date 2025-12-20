import streamlit as st
import sqlite3
import hashlib
import math
import random
from streamlit_js_eval import get_geolocation

# --- 1. التصميم البصري (إصلاح الـ Syntax Error) ---
st.set_page_config(page_title="Al Doctor AI", layout="wide")

# استخدمنا r''' لمنع السيرفر من قراءة العلامات بشكل خاطئ
st.markdown(r'''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    * { font-family: 'Tajawal', sans-serif; direction: rtl; }
    .stApp { background-color: #050505; color: #e0e0e0; }
    .classic-logo { color: #40E0D0; text-align: center; font-size: 35px; font-weight: bold; margin-bottom: 20px; }
    .auth-box { max-width: 380px; margin: auto; padding: 20px; background-color: #0d0d0d; border-radius: 12px; border: 1px solid rgba(64, 224, 208, 0.2); }
    .doc-card { 
        background-color: #0d0d0d; padding: 18px; border-radius: 15px; 
        border-right: 5px solid #40E0D0; margin-bottom: 15px; 
        border-top: 1px solid rgba(255,255,255,0.05); border-bottom: 1px solid rgba(255,255,255,0.05);
        max-width: 600px; margin-left: auto; margin-right: auto;
    }
    .doc-name { color: #40E0D0; font-size: 20px; font-weight: bold; }
    .doc-meta { font-size: 13px; color: #888; margin-top: 4px; }
    .rating { color: #FFD700; font-size: 14px; }
    .slot-btn-taken { border: 1px solid #333; color: #444; text-decoration: line-through; padding: 5px; border-radius: 5px; font-size: 11px; text-align: center; }
    .stButton>button { background: linear-gradient(135deg, #1d4e4a 0%, #40E0D0 100%); color: #000 !important; font-weight: bold; border-radius: 8px; width: 100%; }
    </style>
    ''', unsafe_allow_html=True)

# --- 2. إدارة البيانات ---
def init_db():
    conn = sqlite3.connect("al_doctor_v13.db")
    conn.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
    conn.commit()
    conn.close()

init_db()

SYMPTOMS_DB = {
    "ألم صدر حاد": {"spec": "قلبية", "urgency": 10, "diag": "اشتباه ذبحة"},
    "صداع مفاجئ": {"spec": "جملة عصبية", "urgency": 7, "diag": "ضغط شرياني"},
    "ألم مفاصل": {"spec": "مفاصل", "urgency": 4, "diag": "روماتويد"},
    "طفح جلدي": {"spec": "جلدية", "urgency": 3, "diag": "إكزيما"},
    "ضيق تنفس": {"spec": "صدرية", "urgency": 9, "diag": "نوبة ربو"},
    "ألم خاصرة": {"spec": "مسالك بولية", "urgency": 8, "diag": "مغص كلوي"},
    "طنين أذن": {"spec": "أذن وحنجرة", "urgency": 5, "diag": "التهاب داخلي"}
}

DOCTORS_DB = [
    {"name": "د. علي الركابي", "title": "استشاري أمراض القلب", "exp": "20 سنة", "rating": "⭐ 4.9", "spec": "قلبية", "area": "الحارثية", "lat": 33.322, "lon": 44.358},
    {"name": "د. عمر الجبوري", "title": "أخصائي جملة عصبية", "exp": "15 سنة", "rating": "⭐ 4.8", "spec": "جملة عصبية", "area": "المنصور", "lat": 33.325, "lon": 44.348},
    {"name": "د. سارة لؤي", "title": "أخصائية جلدية", "exp": "12 سنة", "rating": "⭐ 4.7", "spec": "جلدية", "area": "زيونة", "lat": 33.332, "lon": 44.455},
    {"name": "د. مريم القيسي", "title": "استشارية مفاصل", "exp": "18 سنة", "rating": "⭐ 4.9", "spec": "مفاصل", "area": "الكرادة", "lat": 33.313, "lon": 44.429},
    {"name": "د. ليث الحسيني", "spec": "صدرية", "title": "أخصائي صدرية", "exp": "10 سنوات", "rating": "⭐ 4.6", "area": "شارع فلسطين", "lat": 33.345, "lon": 44.430}
]

# --- 3. الوظائف الرياضية (إصلاح الـ ValueError) ---
def safe_dist(u_loc, d_lat, d_lon):
    try:
        # التأكد من وجود البيانات قبل الحساب
        if not u_loc or 'coords' not in u_loc: return 0.0
        lat1 = float(u_loc['coords']['latitude'])
        lon1 = float(u_loc['coords']['longitude'])
        # معادلة بسيطة للمسافة
        d = math.sqrt((lat1 - d_lat)*2 + (lon1 - d_lon)*2) * 111
        return round(d, 1)
    except:
        return 0.0

# --- 4. التحكم في الجلسة والواجهات ---
if "view" not in st.session_state: st.session_state.view = "login"

st.markdown('<div class="classic-logo">Al Doctor</div>', unsafe_allow_html=True)

if st.session_state.view in ["login", "signup"]:
    st.markdown('<div class="auth-box">', unsafe_allow_html=True)
    u = st.text_input("اسم المستخدم")
    p = st.text_input("كلمة المرور", type="password")
    
    if st.session_state.view == "login":
        if st.button("دخول"):
            conn = sqlite3.connect("al_doctor_v13.db")
            hp = hashlib.sha256(p.encode()).hexdigest()
            if conn.execute('SELECT * FROM users WHERE username=? AND password=?', (u, hp)).fetchone():
                st.session_state.user, st.session_state.view = u, "app"
                st.rerun()
            else: st.error("خطأ في البيانات")
        if st.button("حساب جديد"): st.session_state.view = "signup"; st.rerun()
    else:
        if st.button("تأكيد التسجيل"):
            if u and p:
                conn = sqlite3.connect("al_doctor_v13.db")
                try:
                    hp = hashlib.sha256(p.encode()).hexdigest()
                    conn.execute('INSERT INTO users VALUES (?,?)', (u, hp))
                    conn.commit()
                    st.session_state.user, st.session_state.view = u, "app"
                    st.rerun()
                except: st.error("الاسم مأخوذ!")
        if st.button("رجوع"): st.session_state.view = "login"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.view == "app":
    st.sidebar.write(f"المستخدم: {st.session_state.user}")
    if st.sidebar.button("خروج"): st.session_state.view = "login"; st.rerun()

    user_location = get_geolocation()
    
    st.markdown('<div class="auth-box" style="max-width:500px">', unsafe_allow_html=True)
    selected = st.multiselect("الأعراض:", list(SYMPTOMS_DB.keys()))
    if st.button("بحث عن طبيب"):
        if selected: st.session_state.active_s = selected
        else: st.warning("اختر الأعراض")
    st.markdown('</div>', unsafe_allow_html=True)

    if "active_s" in st.session_state:
        main_s = max(st.session_state.active_s, key=lambda s: SYMPTOMS_DB[s]['urgency'])
        info = SYMPTOMS_DB[main_s]
        
        st.write("---")
        st.info(f"التشخيص: {info['diag']} | التخصص: {info['spec']}")

        # فرز الأطباء
        doc_results = []
        for d in DOCTORS_DB:
            distance = safe_dist(user_location, d['lat'], d['lon'])
            match = 1 if d['spec'] == info['spec'] else 0
            doc_results.append({"d": d, "dist": distance, "match": match})
        
        doc_results.sort(key=lambda x: (-x['match'], x['dist']))

        for res in doc_results:
            d = res['d']
            st.markdown(f'''
            <div class="doc-card">
                <div style="display:flex; justify-content:space-between">
                    <span class="doc-name">{d['name']}</span>
                    <span class="rating">{d['rating']}</span>
                </div>
                <div class="doc-meta">{d['title']}</div>
                <div class="doc-meta">المنطقة: {d['area']} | يبعد: {res['dist']} كم</div>
            </div>
            ''', unsafe_allow_html=True)
            
            # مواعيد مبسطة (إصلاح مشكلة الأزرار)
            t_cols = st.columns(4)
            slots = ["04:30", "05:00", "05:30", "06:00"]
            for i, t in enumerate(slots):
                with t_cols[i]:
                    if st.button(t, key=f"{d['name']}_{t}"):
                        st.success(f"تم الحجز مع {d['name']} الساعة {t}")
                        st.balloons()
