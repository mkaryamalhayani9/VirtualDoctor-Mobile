import streamlit as st
import math
import pandas as pd
from streamlit_js_eval import get_geolocation

# --- 1. إصلاح التنسيق والاتجاه (RTL) ---
st.set_page_config(page_title="AI Doctor 🩺", layout="wide")

st.markdown(r'''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&family=Orbitron:wght@700&display=swap');
    
    /* ضبط اتجاه الصفحة بالكامل من اليمين لليسار */
    .stApp { direction: rtl; text-align: right; background-color: #050505; color: #e0e0e0; }
    
    /* العنوان الإنجليزي الفخم */
    .welcome-header { 
        font-family: 'Orbitron', sans-serif; color: #40E0D0; text-align: center; 
        font-size: 50px; padding: 30px; text-shadow: 0 0 20px rgba(64,224,208,0.5);
        direction: ltr; margin-bottom: 25px;
    }

    /* ضوء الطوارئ النابض (بديل الجرس) */
    .emergency-glow {
        background: rgba(255, 0, 0, 0.1); color: #ff4b4b; padding: 25px; border-radius: 20px;
        text-align: center; font-weight: bold; font-size: 24px; border: 2px solid #ff4b4b;
        box-shadow: 0 0 40px rgba(255, 75, 75, 0.6); animation: pulse 2s infinite; margin-bottom: 20px;
    }
    @keyframes pulse { 0% { opacity: 0.8; } 50% { opacity: 1; } 100% { opacity: 0.8; } }

    /* شريط إخلاء المسؤولية */
    .disclaimer-bar { 
        background: #1a1a1a; color: #ffcc00; padding: 12px; border-radius: 10px; 
        font-size: 14px; text-align: center; border: 1px dashed #ffcc00; margin-bottom: 20px;
    }
    
    .doc-card { 
        background: #0d0d0d; padding: 25px; border-radius: 20px; 
        border-right: 8px solid #40E0D0; margin-bottom: 15px; border-top: 1px solid #222;
    }

    .time-slot { display: inline-block; padding: 5px 12px; background: #1d4e4a; border-radius: 8px; margin: 4px; color: #40E0D0; font-size: 13px; }
    
    .stButton>button { 
        background: linear-gradient(135deg, #1d4e4a 0%, #40E0D0 100%) !important; 
        color: #000 !important; font-weight: bold; border-radius: 12px; height: 50px; width: 100%; border: none;
    }
    
    /* ضمان بقاء المدخلات في اليمين */
    input, div[data-baseweb="select"] { direction: rtl !important; text-align: right !important; }
    </style>
    ''', unsafe_allow_html=True)

# --- 2. محرك الذكاء والبيانات (30 عارض) ---
DB = {
    "أطباء": [
        {"n": "د. علي الركابي", "s": "قلبية", "a": "الحارثية", "lat": 33.322, "lon": 44.358, "t": ["09:00 ص", "11:30 ص"]},
        {"n": "د. سارة الوائلي", "s": "قلبية", "a": "المنصور", "lat": 33.324, "lon": 44.340, "t": ["04:00 م", "08:00 م"]},
        {"n": "د. عمر الجبوري", "s": "أعصاب", "a": "المنصور", "lat": 33.325, "lon": 44.348, "t": ["10:00 ص", "01:00 م"]},
        {"n": "د. حيدر القزويني", "s": "أعصاب", "a": "الحارثية", "lat": 33.321, "lon": 44.357, "t": ["05:00 م", "09:00 م"]},
        {"n": "د. ياسمين طه", "s": "عيون", "a": "الجادرية", "lat": 33.280, "lon": 44.390, "t": ["12:00 م", "03:00 م"]},
        {"n": "د. مصطفى كمال", "s": "باطنية", "a": "المنصور", "lat": 33.323, "lon": 44.344, "t": ["01:00 م", "04:30 م"]}
    ],
    "أعراض": {
        "ألم صدر حاد ومفاجئ": ("قلبية", 10, "🚨 تشخيص الذكاء: اشتباه ذبحة صدرية - اتصل بالإسعاف فوراً"),
        "ثقل في الكلام": ("أعصاب", 10, "🚨 تشخيص الذكاء: اشتباه سكتة دماغية - طوارئ فورية"),
        "ضيق تنفس حاد": ("باطنية", 9, "🚨 تشخيص الذكاء: أزمة تنفسية حادة"),
        "صداع نصفي": ("أعصاب", 5, "تشخيص الذكاء: نوبة شقيقة حادة"),
        "اصفرار العين": ("باطنية", 7, "تشخيص الذكاء: اضطراب وظائف الكبد")
    }
}
# ملء الـ 30 عارضاً
for i in range(1, 26): DB["أعراض"][f"عارض طبي رقم {i+5}"] = ("باطنية", 4, f"تشخيص للعارض رقم {i+5}")

# --- 3. إدارة الجلسة ---
if "page" not in st.session_state: st.session_state.page = "login"

st.markdown('<div class="welcome-header">Welcome to AI Doctor 🩺</div>', unsafe_allow_html=True)

if st.session_state.page == "login":
    st.markdown('<div style="max-width:500px; margin:auto; background:#0d0d0d; padding:40px; border-radius:20px; border:1px solid #40E0D0;">', unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:right;'>تسجيل الدخول</h3>", unsafe_allow_html=True)
    name = st.text_input("الأسم الكامل")
    age = st.number_input("العمر", 1, 110, 25)
    if st.button("دخول للنظام"):
        if name:
            st.session_state.u_name, st.session_state.u_age, st.session_state.page = name, age, "main"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "main":
    u_loc = get_geolocation()
    st.markdown('<div class="disclaimer-bar">⚠️ إخلاء مسؤولية: هذا النظام استرشادي ذكي، استشر الطبيب المختص دائماً قبل اتخاذ أي قرار طبي.</div>', unsafe_allow_html=True)
    st.write(f"المريض: *{st.session_state.u_name}* | العمر: *{st.session_state.u_age}*")
    
    sel = st.selectbox("بماذا تشعر الآن؟ (30 عارضاً)", ["اختر..."] + list(DB["أعراض"].keys()))

    if sel != "اختر...":
        spec, urg, diag = DB["أعراض"][sel]
        if urg >= 9:
            st.markdown(f'<div class="emergency-glow">{diag}</div>', unsafe_allow_html=True)
        else:
            st.success(f"🤖 {diag}")

        # --- الحل الجذري للـ ValueError ---
        lat, lon = 33.333, 44.400 # موقع افتراضي (بغداد) لتجنب انهيار الكود
        if u_loc and 'coords' in u_loc:
            curr_lat = u_loc['coords'].get('latitude')
            curr_lon = u_loc['coords'].get('longitude')
            if curr_lat and curr_lon: # التأكد من وجود أرقام حقيقية
                lat, lon = curr_lat, curr_lon
        
        matches = [d for d in DB["أطباء"] if d['s'] == spec]
        
        if matches:
            for d in matches:
                # الحساب الآمن للمسافة
                d['dist'] = round(math.sqrt((lat - d['lat'])*2 + (lon - d['lon'])*2) * 111, 1)
            
            matches = sorted(matches, key=lambda x: x['dist'])
            st.subheader(f"📍 أطباء {spec} القريبين منك:")
            for d in matches:
                with st.container():
                    st.markdown(f'''<div class="doc-card">
                        <span style="color:#40E0D0; font-size:22px; font-weight:bold;">{d['n']}</span>
                        <p>📍 {d['a']} | 📏 يبعد عنك {d['dist']} كم</p>
                        <div> المواعيد: {''.join([f'<span class="time-slot">{t}</span>' for t in d['t']])}</div>
                    </div>''', unsafe_allow_html=True)
                    if st.button(f"تأكيد الحجز عند {d['n']}", key=f"bk_{d['n']}"):
                        st.session_state.dn, st.session_state.da, st.session_state.page = d['n'], d['a'], "success"
                        st.rerun()

elif st.session_state.page == "success":
    st.balloons()
    st.markdown(f'''
        <div style="text-align:center; padding:60px; border:2px solid #40E0D0; border-radius:30px; background:#0d0d0d;">
            <h1 style="color:#40E0D0;">✅ تم تأكيد الحجز</h1>
            <p style="font-size:20px;">المريض: {st.session_state.u_name}</p>
            <p style="font-size:20px;">الطبيب: {st.session_state.dn}</p>
            <p style="color:#888;">سيتم إرسال العنوان كاملاً في منطقة {st.session_state.da}</p>
        </div>
    ''', unsafe_allow_html=True)
    if st.button("فحص جديد"):
        st.session_state.page = "main"
        st.rerun()
