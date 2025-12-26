import streamlit as st
import math
import pandas as pd
from streamlit_js_eval import get_geolocation

# --- 1. التصميم (AI Doctor 🩺) ---
st.set_page_config(page_title="AI Doctor 🩺", layout="wide")

st.markdown(r'''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    * { font-family: 'Tajawal', sans-serif; direction: rtl; }
    .stApp { background-color: #050505; color: #e0e0e0; }
    .welcome-text { color: #40E0D0; text-align: center; font-size: 38px; font-weight: bold; margin-bottom: 25px; }
    .auth-box { max-width: 500px; margin: auto; padding: 30px; background: #0d0d0d; border-radius: 20px; border: 1px solid #40E0D0; }
    .emergency-box { background: linear-gradient(90deg, #800000 0%, #ff0000 100%); color: white; padding: 20px; border-radius: 12px; text-align: center; font-weight: bold; font-size: 22px; border: 2px solid white; margin-bottom: 20px; box-shadow: 0 0 15px #ff0000; }
    .doc-card { background-color: #0d0d0d; padding: 20px; border-radius: 15px; border-right: 6px solid #40E0D0; margin-bottom: 15px; border: 1px solid rgba(255,255,255,0.05); }
    .stars { color: #FFD700; font-size: 20px; }
    .success-page { text-align: center; padding: 40px; background: #0d0d0d; border-radius: 20px; border: 2px solid #40E0D0; margin-top: 20px; }
    .stButton>button { background: linear-gradient(135deg, #1d4e4a 0%, #40E0D0 100%) !important; color: #000 !important; font-weight: bold; border-radius: 8px; width: 100%; height: 48px; }
    </style>
    ''', unsafe_allow_html=True)

# --- 2. قاعدة البيانات (30 عرض + أطباء) ---
SYMPTOMS_DB = {
    "ألم صدر حاد ومفاجئ": {"spec": "قلبية", "urg": 10, "diag": "🔔 تنبيه طوارئ: اشتباه ذبحة صدرية - اتصل بالإسعاف فوراً"},
    "صعوبة في الكلام أو ثقل": {"spec": "جملة عصبية", "urg": 10, "diag": "🔔 تنبيه طوارئ: اشتباه سكتة دماغية - توجه للمستشفى"},
    "ضيق تنفس وازرقاق": {"spec": "صدرية", "urg": 10, "diag": "🔔 تنبيه طوارئ: فشل تنفسي حاد"},
    "ألم بطن يمين حاد": {"spec": "جراحة عامة", "urg": 9, "diag": "🚨 طوارئ: اشتباه التهاب زائدة دودية"},
    "فقدان رؤية مفاجئ": {"spec": "عيون", "urg": 9, "diag": "🚨 طوارئ: انفصال شبكية أو إصابة حادة"},
    "كسر عظمي واضح": {"spec": "عظام", "urg": 9, "diag": "🚨 طوارئ: كسر عظمي يحتاج تثبيت فوري"},
    "صداع نصفي شديد": {"spec": "جملة عصبية", "urg": 5, "diag": "التشخيص: نوبة شقيقة حادة"},
    "عطش وتبول متكرر": {"spec": "غدد صماء", "urg": 5, "diag": "التشخيص: اشتباه اضطراب سكر الدم"},
    "ألم كلوي حاد": {"spec": "مسالك بولية", "urg": 8, "diag": "التشخيص: مغص كلوي (حصى الكلى)"},
    "طفح جلدي وحكة": {"spec": "جلدية", "urg": 4, "diag": "التشخيص: تحسس جلدي أو اكزيما"},
    "طنين ودوار": {"spec": "أذن وحنجرة", "urg": 5, "diag": "التشخيص: دوار دهليزي بالأذن"},
    "نزيف لثة": {"spec": "أسنان", "urg": 4, "diag": "التشخيص: التهاب أنسجة اللثة"},
    "خمول دائم": {"spec": "غدد صماء", "urg": 4, "diag": "التشخيص: خمول الغدة الدرقية"},
    "ألم مفاصل": {"spec": "مفاصل", "urg": 5, "diag": "التشخيص: التهاب مفاصل روماتيزمي"},
    "حرقة معدة": {"spec": "جهاز هضمي", "urg": 4, "diag": "التشخيص: ارتجاع مريئي"},
    "رعشة يد": {"spec": "جملة عصبية", "urg": 6, "diag": "التشخيص: اضطراب حركي عصبي"},
    "سعال جاف": {"spec": "صدرية", "urg": 5, "diag": "التشخيص: تحسس قصبي"},
    "تورم ساق": {"spec": "أوعية دموية", "urg": 8, "diag": "🚨 تنبيه: اشتباه جلطة وريدية"},
    "حزن واكتئاب": {"spec": "نفسية", "urg": 5, "diag": "التشخيص: أعراض اكتئاب سريري"},
    "تأخر نطق": {"spec": "أطفال", "urg": 4, "diag": "التشخيص: اضطراب نمو لغوي"},
    "نزيف أنف": {"spec": "أذن وحنجرة", "urg": 7, "diag": "التشخيص: رعاف حاد"},
    "ألم تبول": {"spec": "مسالك بولية", "urg": 5, "diag": "التشخيص: التهاب مجاري بولية"},
    "اصفرار عين": {"spec": "باطنية/كبد", "urg": 7, "diag": "التشخيص: التهاب كبد فيروسي"},
    "جفاف عين": {"spec": "عيون", "urg": 3, "diag": "التشخيص: جفاف ملتحمة العين"},
    "تساقط شعر": {"spec": "جلدية", "urg": 4, "diag": "التشخيص: ضعف بصيلات الشعر"},
    "غازات وانتفاخ": {"spec": "جهاز هضمي", "urg": 3, "diag": "التشخيص: قولون عصبي"},
    "تنميل أطراف": {"spec": "جملة عصبية", "urg": 5, "diag": "التشخيص: اعتلال أعصاب طرفية"},
    "نقص فيتامينات": {"spec": "باطنية", "urg": 4, "diag": "التشخيص: فقر دم أو نقص تغذية"},
    "ألم أذن": {"spec": "أذن وحنجرة", "urg": 5, "diag": "التشخيص: التهاب أذن وسطى"},
    "حرارة مرتفعة": {"spec": "باطنية", "urg": 7, "diag": "التشخيص: عدوى فيروسية (حمى)"}
}

DOCTORS_DB = [
    {"name": "د. علي الركابي", "spec": "قلبية", "area": "الحارثية", "lat": 33.322, "lon": 44.358, "stars": 5},
    {"name": "د. محمد الزيدي", "spec": "قلبية", "area": "المنصور", "lat": 33.324, "lon": 44.345, "stars": 5},
    {"name": "د. عمر الجبوري", "spec": "جملة عصبية", "area": "المنصور", "lat": 33.325, "lon": 44.348, "stars": 5},
    {"name": "د. حيدر القزويني", "spec": "جملة عصبية", "area": "الحارثية", "lat": 33.321, "lon": 44.357, "stars": 5},
    {"name": "د. ياسمين طه", "spec": "عيون", "area": "الجادرية", "lat": 33.280, "lon": 44.390, "stars": 5},
    {"name": "د. لؤي الخفاجي", "spec": "عيون", "area": "اليرموك", "lat": 33.300, "lon": 44.330, "stars": 5},
    {"name": "د. مريم القيسي", "spec": "مفاصل", "area": "الكرادة", "lat": 33.313, "lon": 44.429, "stars": 5},
    {"name": "د. حسن الهاشمي", "spec": "مسالك بولية", "area": "الحارثية", "lat": 33.320, "lon": 44.355, "stars": 5}
]

# --- 3. المنطق (Step-by-Step) ---
if "step" not in st.session_state: st.session_state.step = "login"

st.markdown('<div class="welcome-text">Welcome to AI Doctor 🩺</div>', unsafe_allow_html=True)

# الخطوة 1: الدخول (الاسم والعمر)
if st.session_state.step == "login":
    st.markdown('<div class="auth-box">', unsafe_allow_html=True)
    st.subheader("تسجيل بيانات المريض")
    p_name = st.text_input("الأسم الكامل")
    p_age = st.number_input("العمر", 1, 100, 25)
    if st.button("دخول للنظام"):
        if p_name:
            st.session_state.p_name, st.session_state.p_age, st.session_state.step = p_name, p_age, "main"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# الخطوة 2: الشاشة الرئيسية (البحث والتشخيص)
elif st.session_state.step == "main":
    u_loc = get_geolocation()
    st.write(f"المريض: *{st.session_state.p_name}* | العمر: *{st.session_state.p_age}*")
    
    sel = st.selectbox("بماذا تشعر؟ (قائمة الـ 30 عرضاً)", ["اختر..."] + list(SYMPTOMS_DB.keys()))

    if sel != "اختر...":
        case = SYMPTOMS_DB[sel]
        if case['urg'] >= 9:
            st.markdown(f'<div class="emergency-box">{case["diag"]}</div>', unsafe_allow_html=True)
        else:
            st.success(f"🤖 {case['diag']}")

        # معالجة الموقع بذكاء لمنع ValueError
        u_lat, u_lon = 33.333, 44.400 # موقع افتراضي
        if u_loc and 'coords' in u_loc:
            lt, ln = u_loc['coords'].get('latitude'), u_loc['coords'].get('longitude')
            if lt is not None and ln is not None: u_lat, u_lon = lt, ln
        
        matched = [d for d in DOCTORS_DB if d['spec'] == case['spec']]
        for d in matched:
            d['dist'] = round(math.sqrt((u_lat - d['lat'])*2 + (u_lon - d['lon'])*2) * 111, 1)
        
        matched = sorted(matched, key=lambda x: x['dist'])

        st.subheader("📍 الأطباء المتوفرون (مرتبون حسب القرب):")
        for d in matched:
            with st.container():
                st.markdown(f'''<div class="doc-card">
                    <span style="color:#40E0D0; font-size:22px; font-weight:bold;">{d['name']}</span>
                    <div class="stars">{"⭐"*d['stars']}</div>
                    <p>📍 {d['area']} | 📏 يبعد {d['dist']} كم</p></div>''', unsafe_allow_html=True)
                
                if st.checkbox(f"عرض الخريطة لـ {d['name']} 🗺️", key=f"m_{d['name']}"):
                    st.map(pd.DataFrame({'lat': [d['lat']], 'lon': [d['lon']]}), zoom=14)
                
                if st.button(f"تأكيد الحجز عند {d['name']}", key=f"b_{d['name']}"):
                    st.session_state.doc, st.session_state.area, st.session_state.step = d['name'], d['area'], "success"
                    st.rerun()

# الخطوة 3: صفحة النجاح المنفصلة
elif st.session_state.step == "success":
    st.balloons()
    st.markdown(f'''
        <div class="success-page">
            <h1 style="color:#40E0D0;">✅ تم الحجز بنجاح</h1>
            <p style="font-size:22px;">عزيزي <b>{st.session_state.p_name}</b>، تم تأكيد موعدك.</p>
            <hr style="border-color:#40E0D0;">
            <p style="font-size:20px;">الطبيب: <b>{st.session_state.doc}</b></p>
            <p style="font-size:20px;">المنطقة: <b>{st.session_state.area}</b></p>
            <p style="color:#888;">يرجى مراجعة العيادة خلال الساعة القادمة.</p>
        </div>
    ''', unsafe_allow_html=True)
    if st.button("بدء فحص جديد"):
        st.session_state.step = "main"
        st.rerun()
