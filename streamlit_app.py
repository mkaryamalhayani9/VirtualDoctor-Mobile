import streamlit as st
import math
import pandas as pd
from streamlit_js_eval import get_geolocation

# --- 1. التصميم البصري (AI Doctor 🩺) ---
st.set_page_config(page_title="AI Doctor 🩺", layout="wide")

st.markdown(r'''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    * { font-family: 'Tajawal', sans-serif; direction: rtl; }
    .stApp { background-color: #050505; color: #e0e0e0; }
    .classic-logo { color: #40E0D0; text-align: center; font-size: 45px; font-weight: bold; margin-bottom: 25px; }
    .emergency-alert { background-color: #4a0000; color: #ff4b4b; padding: 20px; border-radius: 12px; border: 2px solid #ff4b4b; text-align: center; font-size: 20px; font-weight: bold; margin-bottom: 20px; }
    .doc-card { background-color: #0d0d0d; padding: 20px; border-radius: 15px; border-right: 6px solid #40E0D0; margin-bottom: 15px; border: 1px solid rgba(255,255,255,0.05); }
    .stars { color: #FFD700; font-size: 20px; margin-bottom: 5px; display: block; }
    .distance-tag { background: rgba(64, 224, 208, 0.1); color: #40E0D0; padding: 4px 12px; border-radius: 20px; font-size: 13px; font-weight: bold; }
    .stButton>button { background: linear-gradient(135deg, #1d4e4a 0%, #40E0D0 100%) !important; color: #000 !important; font-weight: bold; border-radius: 8px; width: 100%; height: 45px; }
    </style>
    ''', unsafe_allow_html=True)

# --- 2. قاعدة البيانات الكاملة (24 عرض + الأطباء) ---
SYMPTOMS_DB = {
    "ألم صدر حاد": {"spec": "قلبية", "urgency": 10, "diag": "اشتباه ذبحة صدرية - طوارئ"},
    "ثقل كلام وتدلي وجه": {"spec": "جملة عصبية", "urgency": 10, "diag": "اشتباه سكتة دماغية - طوارئ"},
    "ضيق تنفس وازرقاق": {"spec": "صدرية", "urgency": 10, "diag": "فشل تنفسي حاد - طوارئ"},
    "ألم أسفل البطن يمين": {"spec": "جراحة عامة", "urgency": 8, "diag": "التهاب زائدة دودية"},
    "فقدان رؤية مفاجئ": {"spec": "عيون", "urgency": 9, "diag": "انفصال شبكية - طوارئ عيون"},
    "تشنج رقبة وحرارة": {"spec": "باطنية", "urgency": 10, "diag": "اشتباه التهاب سحايا"},
    "صداع نصفي شديد": {"spec": "جملة عصبية", "urgency": 5, "diag": "نوبة شقيقة"},
    "عطش وتبول متكرر": {"spec": "غدد صماء", "urgency": 5, "diag": "اشتباه مرض السكري"},
    "ألم مفاجئ بالخاصرة": {"spec": "مسالك بولية", "urgency": 8, "diag": "مغص كلوي حاد"},
    "طفح جلدي قشري": {"spec": "جلدية", "urgency": 3, "diag": "حالة جلدية (صدفية/اكزيما)"},
    "طنين ودوار": {"spec": "أذن وحنجرة", "urgency": 5, "diag": "دوار الدهليز المتوسطة"},
    "نزيف لثة": {"spec": "أسنان", "urgency": 4, "diag": "التهابات لثة حادة"},
    "خمول مستمر": {"spec": "غدد صماء", "urgency": 4, "diag": "كسل الغدة الدرقية"},
    "ألم مفاصل صباحي": {"spec": "مفاصل", "urgency": 5, "diag": "روماتويد أو التهاب مفاصل"},
    "حرقة خلف القص": {"spec": "جهاز هضمي", "urgency": 4, "diag": "ارتجاع مريئي حاد"},
    "رعشة باليدين": {"spec": "جملة عصبية", "urgency": 6, "diag": "اضطرابات حركية عصبية"},
    "سعال مستمر": {"spec": "صدرية", "urgency": 5, "diag": "تحسس قصبي أو ربو"},
    "تورم ساق مؤلم": {"spec": "أوعية دموية", "urgency": 8, "diag": "اشتباه جلطة وريدية (DVT)"},
    "حزن وفقدان أمل": {"spec": "طبيب نفسي", "urgency": 5, "diag": "أعراض اكتئاب"},
    "تأخر نطق الطفل": {"spec": "أطفال", "urgency": 4, "diag": "اضطرابات نمو وتطور"},
    "نزيف أنف حاد": {"spec": "أذن وحنجرة", "urgency": 7, "diag": "رعاف شديد"},
    "ألم حاد بالتبول": {"spec": "مسالك بولية", "urgency": 5, "diag": "التهاب المجاري البولية"},
    "اصفرار العين": {"spec": "باطنية/كبد", "urgency": 7, "diag": "اشتباه التهاب كبد فيروسي"},
    "كسر عظمي": {"spec": "عظام", "urgency": 9, "diag": "كسر أو رض حاد"}
}

DOCTORS_DB = [
    {"name": "د. علي الركابي", "title": "استشاري قلبية", "spec": "قلبية", "area": "الحارثية", "lat": 33.322, "lon": 44.358, "stars": 5},
    {"name": "د. محمد الزيدي", "title": "أخصائي قلب وقسطرة", "spec": "قلبية", "area": "المنصور", "lat": 33.324, "lon": 44.345, "stars": 5},
    {"name": "د. عمر الجبوري", "title": "أخصائي جملة عصبية", "spec": "جملة عصبية", "area": "المنصور", "lat": 33.325, "lon": 44.348, "stars": 5},
    {"name": "د. حيدر القزويني", "title": "استشاري جراحة دماغ", "spec": "جملة عصبية", "area": "الحارثية", "lat": 33.321, "lon": 44.357, "stars": 5},
    {"name": "د. ياسمين طه", "title": "أخصائية جراحة عيون", "spec": "عيون", "area": "الجادرية", "lat": 33.280, "lon": 44.390, "stars": 5},
    {"name": "د. لؤي الخفاجي", "title": "استشاري ليزك", "spec": "عيون", "area": "اليرموك", "lat": 33.300, "lon": 44.330, "stars": 5},
    {"name": "د. مريم القيسي", "title": "استشارية مفاصل وروماتيزم", "spec": "مفاصل", "area": "الكرادة", "lat": 33.313, "lon": 44.429, "stars": 5}
]

# --- 3. تشغيل النظام ---
st.markdown('<div class="classic-logo">AI Doctor 🩺</div>', unsafe_allow_html=True)

u_loc = get_geolocation()

selected_symptom = st.selectbox("بماذا تشعر؟ (اختر من قائمة الـ 24 عرضاً)", ["اختر حالتك..."] + list(SYMPTOMS_DB.keys()))

if selected_symptom != "اختر حالتك...":
    case = SYMPTOMS_DB[selected_symptom]
    
    # تنبيه الطوارئ
    if case['urgency'] >= 9:
        st.markdown(f'<div class="emergency-alert">🚨 تنبيه طوارئ: {case["diag"]}</div>', unsafe_allow_html=True)
    else:
        st.success(f"🤖 التشخيص المتوقع: {case['diag']}")

    # البحث عن الأطباء المختصين وحساب المسافة
    matched_docs = [d for d in DOCTORS_DB if d['spec'] == case['spec']]
    
    u_lat, u_lon = 33.333, 44.400 # افتراضي بغداد
    if u_loc and 'coords' in u_loc:
        u_lat = u_loc['coords'].get('latitude', u_lat)
        u_lon = u_loc['coords'].get('longitude', u_lon)
    
    for d in matched_docs:
        d['dist'] = round(math.sqrt((u_lat-d['lat'])*2 + (u_lon-d['lon'])*2) * 111, 1)
    
    # ترتيب حسب القرب
    matched_docs = sorted(matched_docs, key=lambda x: x['dist'])

    st.subheader(f"📍 أطباء {case['spec']} المتاحين بالقرب منك:")

    for d in matched_docs:
        with st.container():
            st.markdown(f'''
                <div class="doc-card">
                    <div style="display:flex; justify-content:space-between;">
                        <div>
                            <span style="color:#40E0D0; font-size:22px; font-weight:bold;">{d['name']}</span>
                            <div class="stars">{"⭐"*d['stars']}</div>
                            <p style="margin:2px 0; color:#bbb;">{d['title']} - {d['area']}</p>
                        </div>
                        <div class="distance-tag">📏 {d['dist']} كم</div>
                    </div>
                </div>
            ''', unsafe_allow_html=True)
            
            # الخريطة الاختيارية (بناءً على طلبك لتقليل الزحام)
            show_map = st.checkbox(f"فتح خريطة الموقع لـ {d['name']} 🗺️", key=f"map_{d['name']}")
            if show_map:
                st.map(pd.DataFrame({'lat': [d['lat']], 'lon': [d['lon']]}), zoom=14)
            
            if st.button(f"تأكيد موعد الحجز عند {d['name']}", key=f"btn_{d['name']}"):
                st.balloons()
                st.success(f"تم الحجز بنجاح! الطبيب بانتظارك في عيادة {d['area']}.")
