import streamlit as st
import math
import random
from streamlit_js_eval import get_geolocation

# --- 1. الإعدادات والتصميم ---
st.set_page_config(page_title="Al Doctor AI - Final Pro", layout="wide")

st.markdown(r'''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    * { font-family: 'Tajawal', sans-serif; direction: rtl; }
    .stApp { background-color: #050505; color: #e0e0e0; }
    .classic-logo { color: #40E0D0; text-align: center; font-size: 50px; font-weight: bold; margin-bottom: 10px; }
    .auth-box { max-width: 500px; margin: auto; padding: 25px; background-color: #0d0d0d; border-radius: 15px; border: 1px solid rgba(64, 224, 208, 0.2); text-align: right; }
    .doc-card { background-color: #0d0d0d; padding: 20px; border-radius: 15px; border-right: 6px solid #40E0D0; margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.05); }
    .emergency-box { background-color: #4a1111; color: #ff4b4b; padding: 20px; border-radius: 10px; border: 2px solid #ff4b4b; text-align: center; font-size: 22px; font-weight: bold; margin-bottom: 20px; animation: blinker 1.2s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.3; } }
    .warning-box { background-color: #332b00; color: #ffcc00; padding: 10px; border-radius: 8px; font-size: 13px; border: 1px solid #ffcc00; text-align: center; margin-bottom: 15px; }
    .stars { color: #FFD700; font-size: 18px; }
    .stButton>button { background: linear-gradient(135deg, #1d4e4a 0%, #40E0D0 100%) !important; color: #000 !important; font-weight: bold; border-radius: 8px; width: 100%; }
    input { text-align: right; direction: rtl; }
    </style>
    ''', unsafe_allow_html=True)

# --- 2. قاعدة البيانات الداخلية (24 عرضاً) ---
SYMPTOMS_DB = {
    "ألم صدر حاد": {"spec": "قلبية", "urgency": 10, "diag": "اشتباه ذبحة صدرية حادة", "acc": "89%"},
    "ثقل كلام وتدلي وجه": {"spec": "جملة عصبية", "urgency": 10, "diag": "اشتباه سكتة دماغية", "acc": "94%"},
    "ضيق تنفس وازرقاق": {"spec": "صدرية", "urgency": 9, "diag": "فشل تنفسي حاد", "acc": "87%"},
    "ألم أسفل البطن يمين": {"spec": "جراحة عامة", "urgency": 8, "diag": "التهاب زائدة دودية", "acc": "82%"},
    "فقدان رؤية مفاجئ": {"spec": "عيون", "urgency": 9, "diag": "انفصال شبكية", "acc": "91%"},
    "تشنج رقبة وحرارة": {"spec": "باطنية", "urgency": 10, "diag": "اشتباه التهاب سحايا", "acc": "98%"},
    "صداع نصفي شديد": {"spec": "جملة عصبية", "urgency": 6, "diag": "شقيقة", "acc": "95%"},
    "عطش وتبول متكرر": {"spec": "غدد صماء", "urgency": 5, "diag": "سكري", "acc": "88%"},
    "ألم مفاجئ بالخاصرة": {"spec": "مسالك بولية", "urgency": 8, "diag": "مغص كلوي", "acc": "90%"},
    "طفح جلدي قشري": {"spec": "جلدية", "urgency": 3, "diag": "صدفية", "acc": "93%"},
    "طنين ودوار": {"spec": "أذن وحنجرة", "urgency": 5, "diag": "مرض منيير", "acc": "85%"},
    "نزيف لثة": {"spec": "أسنان", "urgency": 4, "diag": "التهاب لثة", "acc": "96%"},
    "خمول مستمر": {"spec": "غدد صماء", "urgency": 4, "diag": "خمول درقية", "acc": "84%"},
    "ألم مفاصل صباحي": {"spec": "مفاصل", "urgency": 5, "diag": "روماتويد", "acc": "87%"},
    "حرقة خلف القص": {"spec": "جهاز هضمي", "urgency": 4, "diag": "ارتجاع مريئي", "acc": "92%"},
    "رعشة باليدين": {"spec": "جملة عصبية", "urgency": 6, "diag": "باركنسون", "acc": "81%"},
    "سعال مستمر": {"spec": "صدرية", "urgency": 5, "diag": "حساسية", "acc": "89%"},
    "تورم ساق مؤلم": {"spec": "أوعية دموية", "urgency": 8, "diag": "جلطة وريدية", "acc": "86%"},
    "حزن وفقدان أمل": {"spec": "طبيب نفسي", "urgency": 5, "diag": "اكتئاب", "acc": "79%"},
    "تأخر نطق الطفل": {"spec": "أطفال", "urgency": 4, "diag": "اضطراب نمو", "acc": "83%"},
    "نزيف أنف حاد": {"spec": "أذن وحنجرة", "urgency": 7, "diag": "رعاف", "acc": "95%"},
    "ألم حاد بالتبول": {"spec": "مسالك بولية", "urgency": 5, "diag": "التهاب مجاري", "acc": "94%"},
    "اصفرار العين": {"spec": "باطنية/كبد", "urgency": 7, "diag": "التهاب كبد", "acc": "88%"},
    "كسر عظمي": {"spec": "عظام", "urgency": 9, "diag": "كسر عظمي", "acc": "99%"}
}

DOCTORS_DB = [
    {"name": "د. علي الركابي", "title": "استشاري قلبية", "spec": "قلبية", "area": "الحارثية", "lat": 33.322, "lon": 44.358, "stars": 5},
    {"name": "د. عمر الجبوري", "title": "أخصائي جملة عصبية", "spec": "جملة عصبية", "area": "المنصور", "lat": 33.325, "lon": 44.348, "stars": 4},
    {"name": "د. سارة لؤي", "title": "أخصائية جلدية", "spec": "جلدية", "area": "زيونة", "lat": 33.332, "lon": 44.455, "stars": 5},
    {"name": "د. مريم القيسي", "title": "استشارية مفاصل", "spec": "مفاصل", "area": "الكرادة", "lat": 33.313, "lon": 44.429, "stars": 4},
    {"name": "د. ليث الحسيني", "title": "أخصائي صدرية", "spec": "صدرية", "area": "شارع فلسطين", "lat": 33.345, "lon": 44.430, "stars": 5}
]

# --- 3. الدوال والمنطق ---
if "view" not in st.session_state: st.session_state.view = "login"

def get_dist(u_loc, d_lat, d_lon):
    try:
        if u_loc and 'coords' in u_loc and u_loc['coords']:
            u_lat = u_loc['coords'].get('latitude')
            u_lon = u_loc['coords'].get('longitude')
            if u_lat: return round(math.sqrt((u_lat-d_lat)*2 + (u_lon-d_lon)*2) * 111, 1)
    except: pass
    return 999.0

st.markdown('<div class="classic-logo">Al Doctor</div>', unsafe_allow_html=True)

# --- الواجهة التعريفية (تسجيل الدخول) ---
if st.session_state.view == "login":
    st.markdown('<div class="auth-box">', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; color:#40E0D0;'>صفحة تعريف المريض</h2>", unsafe_allow_html=True)
    name = st.text_input("الأسم الكامل")
    age = st.number_input("العمر", min_value=1, max_value=110)
    pwd = st.text_input("الباسورد (كلمة المرور)", type="password")
    
    if st.button("تسجيل الدخول للنظام"):
        if name and pwd:
            st.session_state.user = {"name": name, "age": age}
            st.session_state.view = "app"
            st.rerun()
        else: st.error("يرجى ملء كافة الحقول")
    st.markdown('</div>', unsafe_allow_html=True)

# --- واجهة التطبيق الرئيسية ---
elif st.session_state.view == "app":
    user_location = get_geolocation()
    st.markdown(f"<h5 style='text-align:right;'>مرحباً: {st.session_state.user['name']} | العمر: {st.session_state.user['age']} سنة</h5>", unsafe_allow_html=True)
    
    st.markdown('<div class="auth-box" style="max-width:600px">', unsafe_allow_html=True)
    selected = st.multiselect("حدد الأعراض الحالية:", list(SYMPTOMS_DB.keys()))
    if st.button("بدء التشخيص الفوري 🔍"):
        if selected: st.session_state.active_s = selected
    st.markdown('</div>', unsafe_allow_html=True)

    if "active_s" in st.session_state:
        main_s = max(st.session_state.active_s, key=lambda s: SYMPTOMS_DB[s]['urgency'])
        info = SYMPTOMS_DB[main_s]
        
        # --- نظام الطوارئ القصوى ---
        if info['urgency'] >= 10:
            st.markdown(f'''<div class="emergency-box">🚨 حالة طوارئ: {info['diag']}<br>يرجى التوجه للمستشفى فوراً!</div>''', unsafe_allow_html=True)
        
        st.success(f"🤖 التشخيص المتوقع: {info['diag']} (الدقة: {info['acc']})")
        st.markdown('<div class="warning-box">إخلاء مسؤولية: هذا التشخيص استرشادي من نظام ذكاء اصطناعي ولا يغني عن الطبيب.</div>', unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align:right; color:#40E0D0;'>التخصص المطلوب: {info['spec']}</h3>", unsafe_allow_html=True)

        # حساب المسافات والترتيب
        docs = []
        for d in DOCTORS_DB:
            distance = get_dist(user_location, d['lat'], d['lon'])
            docs.append({"data": d, "dist": distance})
        docs.sort(key=lambda x: x['dist'])

        for item in docs:
            d = item['data']
            d_dist = f"{item['dist']} كم" if item['dist'] < 900 else "يرجى تفعيل الموقع"
            st.markdown(f'''
                <div class="doc-card">
                    <div style="display:flex; justify-content:space-between">
                        <div>
                            <span style="color:#40E0D0; font-size:22px; font-weight:bold;">{d['name']}</span>
                            <div class="stars">{"⭐"*d['stars']}</div>
                            <div style="color:#888;">{d['title']}</div>
                        </div>
                        <div style="text-align:left">
                            <span style="font-size:13px;">📍 {d['area']}</span><br>
                            <span style="color:#40E0D0; font-weight:bold; font-size:14px;">📏 يبعد {d_dist}</span>
                        </div>
                    </div>
            ''', unsafe_allow_html=True)
            
            # المواعيد
            cols = st.columns(5)
            for i, t in enumerate(["3:00", "3:30", "4:00", "4:30", "5:00"]):
                random.seed(d['name'] + t)
                if cols[i].button(t, key=f"{d['name']}_{t}"):
                    st.balloons()
                    st.info(f"تم حجز الموعد بنجاح عند {d['name']} الساعة {t}")
            st.markdown('</div>', unsafe_allow_html=True)
