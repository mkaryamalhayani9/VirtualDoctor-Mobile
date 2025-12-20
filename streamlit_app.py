import streamlit as st
import sqlite3
import hashlib
import math
import random
from streamlit_js_eval import get_geolocation

# --- 1. التصميم البصري (رجوع الخط الفخم وتنسيق المواعيد) ---
st.set_page_config(page_title="Al Doctor AI", layout="wide")

st.markdown(r'''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Tajawal:wght@400;700&display=swap');
    * { font-family: 'Tajawal', sans-serif; direction: rtl; }
    .stApp { background-color: #050505; color: #e0e0e0; }
    
    /* رجوع خط اسم الموقع المميز */
    .classic-logo { 
        font-family: 'Playfair Display', serif; color: #40E0D0; 
        text-align: center; font-size: 50px; margin-bottom: 10px;
    }
    
    .auth-box { max-width: 400px; margin: auto; padding: 25px; background-color: #0d0d0d; border-radius: 15px; border: 1px solid rgba(64, 224, 208, 0.2); }
    
    .doc-card { 
        background-color: #0d0d0d; padding: 20px; border-radius: 15px; 
        border-right: 6px solid #40E0D0; margin-bottom: 20px; 
        border: 1px solid rgba(255,255,255,0.05);
    }
    
    /* تنسيق المواعيد المتاحة والمحجوزة */
    .slot-taken { background-color: #222; color: #555; padding: 8px; border-radius: 5px; text-align: center; text-decoration: line-through; border: 1px solid #333; font-size: 12px; }
    .slot-avail { background-color: #1d4e4a; color: #40E0D0; padding: 8px; border-radius: 5px; text-align: center; border: 1px solid #40E0D0; font-size: 12px; font-weight: bold; }
    
    .stButton>button { background: linear-gradient(135deg, #1d4e4a 0%, #40E0D0 100%); color: #000 !important; font-weight: bold; border-radius: 8px; }
    </style>
    ''', unsafe_allow_html=True)

# --- 2. محرك البيانات والتشخيصات (25 حالة) ---
def init_db():
    conn = sqlite3.connect("al_doctor_final.db")
    conn.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
    conn.commit()
    conn.close()

init_db()

SYMPTOMS_DB = {
    "ألم صدر حاد": {"spec": "قلبية", "urgency": 10, "diag": "اشتباه ذبحة"},
    "ثقل كلام وتدلي وجه": {"spec": "جملة عصبية", "urgency": 10, "diag": "سكتة دماغية"},
    "ضيق تنفس وازرقاق": {"spec": "صدرية", "urgency": 9, "diag": "فشل تنفسي"},
    "ألم أسفل البطن يمين": {"spec": "جراحة عامة", "urgency": 8, "diag": "التهاب زائدة"},
    "فقدان رؤية مفاجئ": {"spec": "عيون", "urgency": 9, "diag": "انفصال شبكية"},
    "صداع نصفي شديد": {"spec": "جملة عصبية", "urgency": 6, "diag": "شقيقة"},
    "عطش وتبول متكرر": {"spec": "غدد صماء", "urgency": 5, "diag": "سكري"},
    "ألم مفاجئ بالخاصرة": {"spec": "مسالك بولية", "urgency": 8, "diag": "مغص كلوي"},
    "طفح جلدي قشري": {"spec": "جلدية", "urgency": 3, "diag": "صدفية"},
    "طنين ودوار": {"spec": "أذن وحنجرة", "urgency": 5, "diag": "مرض منيير"},
    "نزيف لثة": {"spec": "أسنان", "urgency": 4, "diag": "التهاب لثة"},
    "خمول مستمر": {"spec": "غدد صماء", "urgency": 4, "diag": "خمول درقية"},
    "ألم مفاصل صباحي": {"spec": "مفاصل", "urgency": 5, "diag": "روماتويد"},
    "حرقة خلف القص": {"spec": "جهاز هضمي", "urgency": 4, "diag": "ارتجاع مريئي"},
    "رعشة باليدين": {"spec": "جملة عصبية", "urgency": 6, "diag": "باركنسون"},
    "سعال مستمر": {"spec": "صدرية", "urgency": 5, "diag": "حساسية"},
    "ألم خصية مفاجئ": {"spec": "مسالك", "urgency": 9, "diag": "التواء خصية"},
    "تورم ساق مؤلم": {"spec": "أوعية دموية", "urgency": 8, "diag": "جلطة وريدية"},
    "حزن وفقدان أمل": {"spec": "طبيب نفسي", "urgency": 5, "diag": "اكتئاب"},
    "تأخر نطق الطفل": {"spec": "أطفال", "urgency": 4, "diag": "اضطراب نمو"},
    "نزيف أنف حاد": {"spec": "أذن وحنجرة", "urgency": 7, "diag": "رعاف"},
    "تشنج رقبة وحرارة": {"spec": "باطنية", "urgency": 10, "diag": "سحايا"},
    "ألم حاد بالتبول": {"spec": "مسالك", "urgency": 5, "diag": "التهاب مجاري"},
    "اصفرار العين": {"spec": "باطنية/كبد", "urgency": 7, "diag": "التهاب كبد"},
    "كسر عظمي": {"spec": "عظام", "urgency": 9, "diag": "كسر"}
}

DOCTORS_DB = [
    {"name": "د. علي الركابي", "title": "استشاري قلبية", "spec": "قلبية", "area": "الحارثية", "lat": 33.322, "lon": 44.358},
    {"name": "د. عمر الجبوري", "title": "أخصائي جملة عصبية", "spec": "جملة عصبية", "area": "المنصور", "lat": 33.325, "lon": 44.348},
    {"name": "د. سارة لؤي", "title": "أخصائية جلدية", "spec": "جلدية", "area": "زيونة", "lat": 33.332, "lon": 44.455},
    {"name": "د. مريم القيسي", "title": "استشارية مفاصل", "spec": "مفاصل", "area": "الكرادة", "lat": 33.313, "lon": 44.429},
    {"name": "د. ليث الحسيني", "title": "أخصائي صدرية", "spec": "صدرية", "area": "شارع فلسطين", "lat": 33.345, "lon": 44.430}
]

# --- 3. الوظائف ---
if "view" not in st.session_state: st.session_state.view = "login"

def safe_dist(u_loc, d_lat, d_lon):
    try:
        lat1, lon1 = u_loc['coords']['latitude'], u_loc['coords']['longitude']
        return round(math.sqrt((lat1-d_lat)*2 + (lon1-d_lon)*2) * 111, 1)
    except: return 0.0

st.markdown('<div class="classic-logo">Al Doctor</div>', unsafe_allow_html=True)

# واجهة الدخول (بدون تنبيه "الاسم مأخوذ")
if st.session_state.view == "login":
    st.markdown('<div class="auth-box">', unsafe_allow_html=True)
    u = st.text_input("اسم المستخدم")
    p = st.text_input("كلمة المرور", type="password")
    if st.button("دخول / تسجيل"):
        if u and p:
            conn = sqlite3.connect("al_doctor_final.db")
            hp = hashlib.sha256(p.encode()).hexdigest()
            # محاولة إدخال مستخدم جديد، إذا موجود أصلاً يسوي تسجيل دخول عادي
            try:
                conn.execute('INSERT INTO users VALUES (?,?)', (u, hp))
                conn.commit()
            except: pass # إذا موجود مسبقاً، يكمل طبيعي
            st.session_state.user, st.session_state.view = u, "app"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.view == "app":
    user_location = get_geolocation()
    st.markdown('<div class="auth-box" style="max-width:500px">', unsafe_allow_html=True)
    selected = st.multiselect("حدد الأعراض (يمكنك اختيار أكثر من واحد):", list(SYMPTOMS_DB.keys()))
    if st.button("ابحث عن الطبيب الأقرب 🔍"):
        if selected: st.session_state.active_s = selected
    st.markdown('</div>', unsafe_allow_html=True)

    if "active_s" in st.session_state:
        main_s = max(st.session_state.active_s, key=lambda s: SYMPTOMS_DB[s]['urgency'])
        info = SYMPTOMS_DB[main_s]
        st.write("---")
        st.info(f"التحليل: {info['diag']} | التخصص المطلوب: {info['spec']}")

        # فرز الأطباء
        results = []
        for d in DOCTORS_DB:
            dist = safe_dist(user_location, d['lat'], d['lon'])
            match = 100 if d['spec'] == info['spec'] else 0
            results.append({"d": d, "dist": dist, "match": match})
        results.sort(key=lambda x: (-x['match'], x['dist']))

        for res in results:
            d = res['d']
            st.markdown(f'''
            <div class="doc-card">
                <div style="display:flex; justify-content:space-between">
                    <span style="color:#40E0D0; font-size:20px; font-weight:bold;">{d['name']}</span>
                    <span style="font-size:12px;">📍 {d['area']} ({res['dist']} كم)</span>
                </div>
                <div style="color:#888; font-size:14px; margin-bottom:10px;">{d['title']}</div>
            ''', unsafe_allow_html=True)
            
            # عرض المواعيد المتاحة والمحجوزة
            st.write("جدول مواعيد اليوم:")
            t_cols = st.columns(5)
            # توليد مواعيد وهمية ثابتة لكل طبيب
            random.seed(d['name'])
            slots = ["4:00", "4:30", "5:00", "5:30", "6:00"]
            for i, t in enumerate(slots):
                is_taken = random.choice([True, False])
                with t_cols[i]:
                    if is_taken:
                        st.markdown(f'<div class="slot-taken">محجوز 🔒</div>', unsafe_allow_html=True)
                    else:
                        if st.button(f"{t} ✅", key=f"{d['name']}_{t}"):
                            st.success(f"تم الحجز الساعة {t}")
            st.markdown('</div>', unsafe_allow_html=True)
