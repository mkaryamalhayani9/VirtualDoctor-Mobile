import streamlit as st
import math
import random
import pandas as pd
from streamlit_js_eval import get_geolocation

# --- 1. التصميم البصري (ستايل احترافي) ---
st.set_page_config(page_title="Al Doctor AI - Baghdad", layout="wide")

st.markdown(r'''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    * { font-family: 'Tajawal', sans-serif; direction: rtl; }
    .stApp { background-color: #050505; color: #e0e0e0; }
    .classic-logo { font-size: 45px; color: #40E0D0; text-align: center; font-weight: bold; padding: 10px; }
    .auth-box { max-width: 400px; margin: auto; padding: 25px; background-color: #0d0d0d; border-radius: 15px; border: 1px solid #40E0D0; }
    .doc-card { background-color: #111; padding: 18px; border-radius: 12px; border-right: 6px solid #40E0D0; margin-bottom: 15px; border: 1px solid #222; }
    .emergency-box { background-color: #440000; color: #ff8888; padding: 15px; border-radius: 10px; border: 1px solid #ff0000; text-align: center; font-weight: bold; }
    .stButton>button { background: linear-gradient(90deg, #1d4e4a, #40E0D0) !important; color: #000 !important; font-weight: bold; border: none; }
    </style>
    ''', unsafe_allow_html=True)

# --- 2. إدارة الجلسة (الدخول المباشر) ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --- 3. قاعدة بيانات الأعراض ---
SYMPTOMS_DB = {
    "ألم صدر حاد": {"spec": "قلبية", "urgency": 10, "diag": "اشتباه ذبحة"},
    "ثقل كلام وتدلي وجه": {"spec": "جملة عصبية", "urgency": 10, "diag": "سكتة دماغية"},
    "ألم أسفل البطن يمين": {"spec": "جراحة عامة", "urgency": 8, "diag": "التهاب زائدة"},
    "خمول مستمر": {"spec": "باطنية", "urgency": 4, "diag": "خمول درقية أو فقر دم"},
    "صداع نصفي شديد": {"spec": "جملة عصبية", "urgency": 6, "diag": "شقيقة"},
    "ضيق تنفس": {"spec": "صدرية", "urgency": 9, "diag": "أزمة تنفسية"}
}

# --- 4. قاعدة بيانات الأطباء (موسعة في بغداد) ---
DOCTORS_DB = [
    {"name": "د. علي الركابي", "spec": "قلبية", "area": "الحارثية", "lat": 33.322, "lon": 44.358, "exp": "18 سنة"},
    {"name": "د. عمر الجبوري", "spec": "جملة عصبية", "area": "المنصور", "lat": 33.325, "lon": 44.348, "exp": "14 سنة"},
    {"name": "د. سارة لؤي", "spec": "جلدية", "area": "زيونة", "lat": 33.332, "lon": 44.455, "exp": "9 سنوات"},
    {"name": "د. مريم القيسي", "spec": "مفاصل", "area": "الكرادة", "lat": 33.313, "lon": 44.429, "exp": "11 سنة"},
    {"name": "د. ليث الحسيني", "spec": "صدرية", "area": "شارع فلسطين", "lat": 33.345, "lon": 44.430, "exp": "12 سنة"},
    {"name": "د. نادر كمال", "spec": "جراحة عامة", "area": "اليرموك", "lat": 33.300, "lon": 44.340, "exp": "20 سنة"},
    {"name": "د. حيدر العبيدي", "spec": "قلبية", "area": "الجادرية", "lat": 33.280, "lon": 44.390, "exp": "15 سنة"},
    {"name": "د. زينب حسن", "spec": "باطنية", "area": "الشعب", "lat": 33.400, "lon": 44.420, "exp": "10 سنوات"},
    {"name": "د. مصطفى الوائلي", "spec": "جراحة عامة", "area": "العطيفية", "lat": 33.350, "lon": 44.370, "exp": "13 سنة"}
]

# --- 5. منطق واجهة الدخول المباشر ---
if not st.session_state.logged_in:
    st.markdown('<div class="classic-logo">Al Doctor</div>', unsafe_allow_html=True)
    st.markdown('<div class="auth-box">', unsafe_allow_html=True)
    st.subheader("دخول سريع للمريض")
    name = st.text_input("الأسم (اختياري)")
    phone = st.text_input("رقم الهاتف للتواصل")
    if st.button("دخول فوري ➔"):
        st.session_state.logged_in = True
        st.session_state.username = name if name else "مستخدم"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- 6. واجهة التطبيق الرئيسية ---
else:
    # جلب الموقع
    user_location = get_geolocation()
    u_lat = user_location['coords']['latitude'] if user_location else 33.312
    u_lon = user_location['coords']['longitude'] if user_location else 44.432

    st.markdown(f'<h3 style="text-align:right;">أهلاً بك، {st.session_state.username} 👋</h3>', unsafe_allow_html=True)
    
    # اختيار الأعراض
    selected_s = st.multiselect("حدد الأعراض التي تعاني منها:", list(SYMPTOMS_DB.keys()))
    
    if selected_s:
        # تحديد الحالة الأكثر خطورة
        main_s = max(selected_s, key=lambda x: SYMPTOMS_DB[x]['urgency'])
        info = SYMPTOMS_DB[main_s]
        
        st.write("---")
        
        # تنبيه الطوارئ
        if info['urgency'] >= 8:
            st.markdown(f'<div class="emergency-box">🚨 حالة طارئة: {info["diag"]} <br> توجه فوراً لأقرب طبيب أو مستشفى!</div>', unsafe_allow_html=True)
        else:
            st.info(f"التحليل الأولي: احتمال {info['diag']}")
            
        st.caption("⚠️ ملاحظة: هذا التشخيص استرشادي ولا يغني عن الفحص السريري من قبل الطبيب.")

        # عرض الأطباء المتوافقين مع التخصص
        st.subheader(f"أطباء تخصص {info['spec']} القريبين منك:")
        
        relevant_docs = [d for d in DOCTORS_DB if d['spec'] == info['spec']]
        
        # ترتيب حسب المسافة
        for d in relevant_docs:
            dist = round(math.sqrt((u_lat-d['lat'])*2 + (u_lon-d['lon'])*2) * 111, 1)
            d['current_dist'] = dist
        
        relevant_docs.sort(key=lambda x: x['current_dist'])

        for d in relevant_docs:
            st.markdown(f'''
            <div class="doc-card">
                <div style="display:flex; justify-content:space-between;">
                    <span style="color:#40E0D0; font-size:19px; font-weight:bold;">{d['name']}</span>
                    <span style="font-size:13px; color:#888;">📍 {d['area']}</span>
                </div>
                <div style="margin-top:5px; font-size:14px;">🎓 الخبرة: {d['exp']} | 🛣️ يبعد عنك: {d['current_dist']} كم</div>
            </div>
            ''', unsafe_allow_html=True)
            
            if st.button(f"حجز موعد سريع مع {d['name']}", key=d['name']):
                st.balloons()
                st.success(f"تم حجز طلبك مع عيادة {d['name']}. سيتم التواصل معك عبر الرقم {phone}")

    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.logged_in = False
        st.rerun()
