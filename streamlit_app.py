import streamlit as st
import math
import random
import pandas as pd
from streamlit_js_eval import get_geolocation

# --- 1. الهوية البصرية والتصميم (خرائط مدمجة وألوان متناسقة) ---
st.set_page_config(page_title="AI Doctor 🩺", layout="wide")

st.markdown(r'''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    * { font-family: 'Tajawal', sans-serif; direction: rtl; }
    .stApp { background-color: #050505; color: #e0e0e0; }
    .classic-logo { color: #40E0D0; text-align: center; font-size: 35px; font-weight: bold; margin-bottom: 20px; }
    .doc-card { 
        background-color: #0d0d0d; padding: 15px; border-radius: 15px; 
        border-right: 6px solid #40E0D0; margin-bottom: 20px; 
        border: 1px solid rgba(255,255,255,0.05); 
    }
    [data-testid="stMap"] { height: 200px !important; border-radius: 12px; margin: 10px 0; }
    .stars { color: #FFD700; font-size: 16px; margin-bottom: 5px; }
    .distance-tag { 
        background: rgba(64, 224, 208, 0.1); color: #40E0D0; 
        padding: 4px 10px; border-radius: 20px; font-size: 13px; font-weight: bold; 
    }
    .stButton>button { 
        background: linear-gradient(135deg, #1d4e4a 0%, #40E0D0 100%) !important; 
        color: #000 !important; font-weight: bold; border-radius: 8px; width: 100%; height: 40px; 
    }
    .slot-taken { 
        background-color: #1a1a1a; color: #444; padding: 8px; border-radius: 5px; 
        text-align: center; text-decoration: line-through; border: 1px solid #222; font-size: 11px; 
    }
    .success-ticket { 
        background: linear-gradient(135deg, #1d4e4a 0%, #0d0d0d 100%); 
        border: 2px dashed #40E0D0; padding: 25px; border-radius: 20px; text-align: center; 
    }
    </style>
    ''', unsafe_allow_html=True)

# --- 2. قاعدة بيانات الأطباء (تعدد الاختصاصات لضمان القرب) ---
DOCTORS_DB = [
    {"name": "د. علي الركابي", "title": "استشاري قلبية", "spec": "قلبية", "area": "الحارثية", "lat": 33.322, "lon": 44.358, "stars": 5},
    {"name": "د. محمد الزيدي", "title": "أخصائي قلب وقسطرة", "spec": "قلبية", "area": "المنصور", "lat": 33.324, "lon": 44.345, "stars": 5},
    {"name": "د. سامر الحديثي", "title": "جراحة قلب", "spec": "قلبية", "area": "الكرادة", "lat": 33.315, "lon": 44.420, "stars": 4},
    {"name": "د. ياسمين طه", "title": "أخصائية عيون", "spec": "عيون", "area": "الجادرية", "lat": 33.280, "lon": 44.390, "stars": 5},
    {"name": "د. لؤي الخفاجي", "title": "استشاري ليزك", "spec": "عيون", "area": "اليرموك", "lat": 33.300, "lon": 44.330, "stars": 5},
    {"name": "د. سارة الصراف", "title": "طب العيون العام", "spec": "عيون", "area": "الاعظمية", "lat": 33.360, "lon": 44.380, "stars": 4},
    {"name": "د. عمر الجبوري", "title": "جملة عصبية", "spec": "جملة عصبية", "area": "المنصور", "lat": 33.325, "lon": 44.348, "stars": 5},
    {"name": "د. حيدر القزويني", "title": "جراحة دماغ", "spec": "جملة عصبية", "area": "الحارثية", "lat": 33.321, "lon": 44.357, "stars": 5},
    {"name": "د. مريم القيسي", "title": "استشارية مفاصل", "spec": "مفاصل", "area": "الكرادة", "lat": 33.313, "lon": 44.429, "stars": 4},
    {"name": "د. ليث الحسيني", "title": "أخصائي صدرية", "spec": "صدرية", "area": "شارع فلسطين", "lat": 33.345, "lon": 44.430, "stars": 5},
    {"name": "د. نور الدليمي", "title": "أمراض التنفس", "spec": "صدرية", "area": "العطيفية", "lat": 33.352, "lon": 44.368, "stars": 4}
]

SYMPTOMS_DB = {
    "ألم صدر حاد": {"spec": "قلبية", "diag": "اشتباه ذبحة صدرية"},
    "فقدان رؤية مفاجئ": {"spec": "عيون", "diag": "مشكلة في الشبكية"},
    "ضيق تنفس": {"spec": "صدرية", "diag": "أزمة تنفسية"},
    "ثقل كلام": {"spec": "جملة عصبية", "diag": "اشتباه سكتة"},
    "ألم مفاصل": {"spec": "مفاصل", "diag": "التهاب مفاصل"}
}

# --- 3. المنطق التشغيلي ---
if "view" not in st.session_state: st.session_state.view = "login"
if "booked" not in st.session_state: st.session_state.booked = None

def get_dist(u_loc, d_lat, d_lon):
    u_lat, u_lon = 33.333, 44.400 # افتراضي لمركز بغداد
    try:
        if u_loc and 'coords' in u_loc:
            u_lat = u_loc['coords'].get('latitude', u_lat)
            u_lon = u_loc['coords'].get('longitude', u_lon)
        return round(math.sqrt((u_lat-d_lat)*2 + (u_lon-d_lon)*2) * 111, 1)
    except: return 5.0

st.markdown('<div class="classic-logo">AI Doctor 🩺</div>', unsafe_allow_html=True)

if st.session_state.view == "login":
    st.markdown('<div class="auth-box">', unsafe_allow_html=True)
    name = st.text_input("الأسم الكامل")
    age = st.number_input("العمر", 1, 100, 25)
    pwd = st.text_input("الباسورد", type="password")
    if st.button("دخول للنظام"):
        if name and pwd:
            st.session_state.user = {"name": name, "age": age}
            st.session_state.view = "app"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.view == "app":
    u_loc = get_geolocation()
    
    if st.session_state.booked:
        b = st.session_state.booked
        st.markdown(f'''
            <div class="success-ticket">
                <h2 style="color:#40E0D0;">✅ تم الحجز بنجاح</h2>
                <p>المريض: <b>{st.session_state.user['name']}</b></p>
                <div style="background:rgba(64,224,208,0.1); padding:15px; border-radius:10px; margin:15px 0;">
                    <p>الطبيب: <b>{b['doc']}</b></p>
                    <p>الموعد: <b>{b['time']}</b> | المكان: <b>{b['area']}</b></p>
                </div>
            </div>
        ''', unsafe_allow_html=True)
        if st.button("حجز جديد"): st.session_state.booked = None; st.rerun()
        st.divider()

    selected = st.multiselect("اختر أعراضك:", list(SYMPTOMS_DB.keys()))
    if selected:
        info = SYMPTOMS_DB[selected[0]]
        st.success(f"🤖 التشخيص المتوقع: {info['diag']}")
        
        # تصفية وفرز حسب المسافة
        matched = [d for d in DOCTORS_DB if d['spec'] == info['spec']]
        for d in matched: d['dist'] = get_dist(u_loc, d['lat'], d['lon'])
        matched = sorted(matched, key=lambda x: x['dist'])

        st.info(f"📍 تم العثور على {len(matched)} أطباء في تخصص {info['spec']}:")

        for d in matched:
            with st.container():
                st.markdown(f'''
                    <div class="doc-card">
                        <div style="display:flex; justify-content:space-between; align-items:start;">
                            <div>
                                <span style="color:#40E0D0; font-size:20px; font-weight:bold;">{d['name']}</span>
                                <div class="stars">{"⭐"*d['stars']}</div>
                                <div style="color:#888;">{d['title']} - {d['area']}</div>
                            </div>
                            <div class="distance-tag">📏 {d['dist']} كم</div>
                        </div>
                ''', unsafe_allow_html=True)
                
                # خريطة مدمجة صغيرة
                st.map(pd.DataFrame({'lat': [d['lat']], 'lon': [d['lon']]}), zoom=14)
                
                # أزرار الحجز
                cols = st.columns(5)
                for i, t in enumerate(["3:00", "3:30", "4:00", "4:30", "5:00"]):
                    random.seed(d['name'] + t)
                    if random.choice([True, False, False]):
                        cols[i].markdown(f'<div class="slot-taken">{t}</div>', unsafe_allow_html=True)
                    else:
                        if cols[i].button(t, key=f"{d['name']}_{t}"):
                            st.session_state.booked = {"doc": d['name'], "time": t, "area": d['area']}
                            st.balloons(); st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
