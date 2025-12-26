import streamlit as st
import math
import random
import pandas as pd
from streamlit_js_eval import get_geolocation

# --- 1. التصميم البصري (الهوية البصرية النهائية) ---
st.set_page_config(page_title="AI Doctor 🩺", layout="wide")

st.markdown(r'''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    * { font-family: 'Tajawal', sans-serif; direction: rtl; }
    .stApp { background-color: #050505; color: #e0e0e0; }
    .classic-logo { color: #40E0D0; text-align: center; font-size: 45px; font-weight: bold; margin-bottom: 5px; }
    .auth-box { max-width: 500px; margin: auto; padding: 25px; background-color: #0d0d0d; border-radius: 15px; border: 1px solid rgba(64, 224, 208, 0.2); text-align: right; }
    .doc-card { background-color: #0d0d0d; padding: 20px; border-radius: 15px; border-right: 6px solid #40E0D0; margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.05); }
    .success-ticket { background: linear-gradient(135deg, #1d4e4a 0%, #0d0d0d 100%); border: 2px solid #40E0D0; padding: 25px; border-radius: 20px; text-align: center; margin-bottom: 30px; border-style: dashed; }
    .slot-taken { background-color: #1a1a1a; color: #555; padding: 8px; border-radius: 5px; text-align: center; text-decoration: line-through; border: 1px solid #333; font-size: 12px; }
    .emergency-box { background-color: #4a0000; color: #ff4b4b; padding: 20px; border-radius: 10px; border: 2px solid #ff4b4b; text-align: center; font-size: 20px; font-weight: bold; margin-bottom: 20px; animation: blinker 1.2s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.4; } }
    .stButton>button { background: linear-gradient(135deg, #1d4e4a 0%, #40E0D0 100%) !important; color: #000 !important; font-weight: bold; border-radius: 8px; width: 100%; height: 45px; }
    input { text-align: right; direction: rtl; }
    </style>
    ''', unsafe_allow_html=True)

# --- 2. محرك البيانات (24 عرضاً طبياً) ---
SYMPTOMS_DB = {
    "ألم صدر حاد": {"spec": "قلبية", "urgency": 10, "diag": "اشتباه ذبحة صدرية"},
    "ثقل كلام وتدلي وجه": {"spec": "جملة عصبية", "urgency": 10, "diag": "اشتباه سكتة دماغية"},
    "ضيق تنفس وازرقاق": {"spec": "صدرية", "urgency": 9, "diag": "فشل تنفسي حاد"},
    "ألم أسفل البطن يمين": {"spec": "جراحة عامة", "urgency": 8, "diag": "التهاب زائدة"},
    "فقدان رؤية مفاجئ": {"spec": "عيون", "urgency": 9, "diag": "انفصال شبكية"},
    "تشنج رقبة وحرارة": {"spec": "باطنية", "urgency": 10, "diag": "اشتباه التهاب سحايا"},
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
    "تورم ساق مؤلم": {"spec": "أوعية دموية", "urgency": 8, "diag": "جلطة وريدية"},
    "حزن وفقدان أمل": {"spec": "طبيب نفسي", "urgency": 5, "diag": "اكتئاب"},
    "تأخر نطق الطفل": {"spec": "أطفال", "urgency": 4, "diag": "اضطراب نمو"},
    "نزيف أنف حاد": {"spec": "أذن وحنجرة", "urgency": 7, "diag": "رعاف"},
    "ألم حاد بالتبول": {"spec": "مسالك بولية", "urgency": 5, "diag": "التهاب مجاري"},
    "اصفرار العين": {"spec": "باطنية/كبد", "urgency": 7, "diag": "التهاب كبد"},
    "كسر عظمي": {"spec": "عظام", "urgency": 9, "diag": "كسر عظمي"}
}

# --- 3. قاعدة الأطباء ---
DOCTORS_DB = [
    {"name": "د. علي الركابي", "title": "استشاري قلبية", "spec": "قلبية", "area": "الحارثية", "lat": 33.322, "lon": 44.358, "stars": 5},
    {"name": "د. محمد الزيدي", "title": "أخصائي قلب وقسطرة", "spec": "قلبية", "area": "المنصور", "lat": 33.324, "lon": 44.345, "stars": 5},
    {"name": "د. عمر الجبوري", "title": "أخصائي جملة عصبية", "spec": "جملة عصبية", "area": "المنصور", "lat": 33.325, "lon": 44.348, "stars": 5},
    {"name": "د. ياسمين طه", "title": "أخصائية جراحة العيون", "spec": "عيون", "area": "الجادرية", "lat": 33.280, "lon": 44.390, "stars": 5},
    {"name": "د. مريم القيسي", "title": "استشارية مفاصل", "spec": "مفاصل", "area": "الكرادة", "lat": 33.313, "lon": 44.429, "stars": 4},
    {"name": "د. ليث الحسيني", "title": "أخصائي صدرية", "spec": "صدرية", "area": "شارع فلسطين", "lat": 33.345, "lon": 44.430, "stars": 5}
]

# --- 4. المنطق التشغيلي ---
if "view" not in st.session_state: st.session_state.view = "login"
if "booked" not in st.session_state: st.session_state.booked = None

def get_safe_dist(u_loc, d_lat, d_lon):
    lat1, lon1 = 33.333, 44.400 
    try:
        if u_loc and 'coords' in u_loc and u_loc['coords']:
            lat1 = u_loc['coords'].get('latitude') or lat1
            lon1 = u_loc['coords'].get('longitude') or lon1
        return round(math.sqrt((lat1-d_lat)*2 + (lon1-d_lon)*2) * 111, 1)
    except: return 4.5

st.markdown('<div class="classic-logo">Welcome to AI Doctor 🩺</div>', unsafe_allow_html=True)

if st.session_state.view == "login":
    st.markdown('<div class="auth-box">', unsafe_allow_html=True)
    name = st.text_input("الأسم الكامل")
    age = st.number_input("العمر", 1, 100)
    pwd = st.text_input("الباسورد", type="password")
    if st.button("دخول للنظام"):
        if name and pwd:
            st.session_state.user = {"name": name, "age": age}
            st.session_state.view = "app"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.view == "app":
    u_loc = get_geolocation()
    
    # بطاقة الحجز المرتبة
    if st.session_state.booked:
        b = st.session_state.booked
        st.markdown(f'''
            <div class="success-ticket">
                <h2 style="color:#40E0D0; margin-bottom:10px;">✅ تم الحجز بنجاح</h2>
                <p style="font-size:18px;">المريض: <b>{st.session_state.user['name']}</b></p>
                <div style="background:rgba(64,224,208,0.1); padding:15px; border-radius:10px; margin:15px 0;">
                    <p>الطبيب: <b>{b['doc']}</b></p>
                    <p>الموعد: <span style="color:#40E0D0; font-weight:bold;">الساعة {b['time']}</span></p>
                    <p>العنوان: {b['area']}</p>
                </div>
                <small style="color:#888;">يرجى إبراز هذه التذكرة عند وصولك للعيادة</small>
            </div>
        ''', unsafe_allow_html=True)
        if st.button("إغلاق التذكرة والعودة"):
            st.session_state.booked = None; st.rerun()
        st.divider()

    selected = st.multiselect("اختر الأعراض التي تشعر بها الآن:", list(SYMPTOMS_DB.keys()))
    if st.button("بدء الفحص الذكي"):
        if selected: st.session_state.active_s = selected

    if "active_s" in st.session_state:
        main_s = max(st.session_state.active_s, key=lambda s: SYMPTOMS_DB[s]['urgency'])
        info = SYMPTOMS_DB[main_s]
        
        if info['urgency'] >= 10:
            st.markdown(f'<div class="emergency-box">🚨 حالة طوارئ: {info["diag"]} - توجه للمشفى!</div>', unsafe_allow_html=True)
        
        st.success(f"🤖 التشخيص المتوقع: {info['diag']}")
        
        matched = [d for d in DOCTORS_DB if d['spec'] == info['spec']]
        for d in matched:
            dist = get_safe_dist(u_loc, d['lat'], d['lon'])
            with st.container():
                st.markdown(f'''
                    <div class="doc-card">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <span style="color:#40E0D0; font-size:20px; font-weight:bold;">{d['name']}</span>
                                <div style="color:#888;">{d['title']} - {d['area']}</div>
                            </div>
                            <div style="text-align:left; color:#40E0D0;">📏 {dist} كم</div>
                        </div>
                ''', unsafe_allow_html=True)
                
                st.map(pd.DataFrame({'lat': [d['lat']], 'lon': [d['lon']]}), zoom=13)
                
                st.write("🕒 الأوقات المتاحة اليوم:")
                cols = st.columns(5)
                times = ["3:00", "3:30", "4:00", "4:30", "5:00"]
                for i, t in enumerate(times):
                    random.seed(d['name'] + t)
                    if random.choice([True, False, False]):
                        cols[i].markdown(f'<div class="slot-taken">{t} 🔒</div>', unsafe_allow_html=True)
                    else:
                        if cols[i].button(t, key=f"{d['name']}_{t}"):
                            st.session_state.booked = {"doc": d['name'], "time": t, "area": d['area']}
                            st.balloons(); st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
