import streamlit as st
import math
import google.generativeai as genai
import requests

# --- 1. إعدادات الذكاء الاصطناعي ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        model = genai.GenerativeModel(models[0])
except Exception as e:
    st.error(f"❌ خطأ اتصال بالذكاء الاصطناعي: {e}")

# --- 2. وظيفة اكتشاف الموقع عبر الـ IP (بدون تدخل المريض) ---
def detect_user_location_by_ip():
    try:
        # الاتصال بخدمة تحديد الموقع عبر IP
        response = requests.get('https://ipapi.co/json/', timeout=5).json()
        return {
            "city": response.get("city", "بغداد"),
            "region": response.get("region", "تحديد تلقائي"),
            "lat": response.get("latitude", 33.3152),
            "lon": response.get("longitude", 44.3661)
        }
    except:
        # موقع افتراضي في حال فشل الاتصال (بغداد - اليرموك)
        return {"city": "بغداد", "region": "اليرموك", "lat": 33.3152, "lon": 44.3661}

# --- 3. التصميم CSS (الألوان والتنبيهات) ---
st.set_page_config(page_title="AI Doctor Baghdad", layout="centered")
st.markdown(r'''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    * { font-family: 'Tajawal', sans-serif; direction: rtl; }
    .stApp { background-color: #050505; color: #e0e0e0; }
    .location-banner { background: rgba(64, 224, 208, 0.1); padding: 15px; border-radius: 12px; border: 1px solid #40E0D0; color: #40E0D0; font-weight: bold; text-align: center; margin-bottom: 25px; }
    .emergency-alert { color: #FF0000; font-weight: bold; font-size: 20px; border: 2px solid #FF0000; padding: 5px 15px; border-radius: 8px; display: inline-block; margin: 10px 0; }
    .doc-card { background: #0d0d0d; padding: 20px; border-radius: 15px; border: 1px solid #333; margin-bottom: 15px; position: relative; }
    .recommend-badge { position: absolute; top: 10px; left: 10px; background: #40E0D0; color: black; padding: 2px 10px; border-radius: 20px; font-size: 11px; font-weight: bold; }
    .success-panel { border: 2px solid #40E0D0; padding: 40px; border-radius: 25px; background: rgba(64, 224, 208, 0.05); text-align: center; }
    </style>
    ''', unsafe_allow_html=True)

# --- 4. قاعدة البيانات (أطباء بغداد) ---
DATA = {
    "أطباء": [
        {"n": "د. علي الركابي", "s": "قلبية", "a": "الحارثية", "lat": 33.3222, "lon": 44.3585, "stars": 5, "slots": {"04:00 PM": True, "05:00 PM": False}, "phone": "07701234567"},
        {"n": "د. سارة الجبوري", "s": "قلبية", "a": "المنصور", "lat": 33.3251, "lon": 44.3482, "stars": 4, "slots": {"06:00 PM": True, "07:30 PM": True}, "phone": "07801112223"},
        {"n": "د. مريم القيسي", "s": "مفاصل", "a": "الكرادة", "lat": 33.3135, "lon": 44.4291, "stars": 5, "slots": {"05:00 PM": True}, "phone": "07901231234"},
        {"n": "د. طه العسكري", "s": "باطنية", "a": "اليرموك", "lat": 33.3121, "lon": 44.3610, "stars": 3, "slots": {"09:00 PM": True}, "phone": "07801212123"}
    ]
}

def calculate_dist(lat1, lon1, lat2, lon2):
    return math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2) * 111.13

if 'step' not in st.session_state: st.session_state.step = 1

# --- المرحلة 1: الدخول (اكتشاف الموقع تلقائياً) ---
if st.session_state.step == 1:
    st.markdown("<h1 style='text-align:center; color:#40E0D0;'>AI Doctor 🩺</h1>", unsafe_allow_html=True)
    
    # جلب الموقع من الـ IP فوراً
    with st.spinner("جاري اكتشاف موقعك تلقائياً..."):
        user_loc = detect_user_location_by_ip()
        st.session_state.detected_location = user_loc

    # عرض الموقع المكتشف في الأعلى
    st.markdown(f'''
        <div class="location-banner">
            📍 تم تحديد موقعك تلقائياً: {user_loc["city"]} - {user_loc["region"]}
        </div>
    ''', unsafe_allow_html=True)
    
    name = st.text_input("الأسم الكامل")
    phone = st.text_input("رقم الهاتف")
    age = st.number_input("العمر", min_value=1, max_value=120, value=25)
    
    if st.button("دخول النظام"):
        if name and phone:
            st.session_state.p_info = {"name": name, "phone": phone, "age": age}
            st.session_state.step = 2
            st.rerun()
        else:
            st.error("يرجى إكمال البيانات المطلوبة")

# --- المرحلة 2: التشخيص وتحليل الطوارئ ---
elif st.session_state.step == 2:
    st.markdown(f"<h3> أهلاً بك AI DR ⛑️<{st.session_state.p_info['name']}</h3>", unsafe_allow_html=True)
    text = st.text_area("اشرح حالتك الصحية باختصار:")

    if st.button("بدء التحليل"):
        with st.spinner("جاري تحليل الحالة ومطابقة المواقع..."):
            u_loc = st.session_state.detected_location
            prompt = (
                f"حلل في سطرين فقط: '{text}'. المريض يتواجد حالياً في {u_loc['city']}/{u_loc['region']}. "
                f"اذكر الاختصاص بالنسب المئوية، التشخيص، وإذا كانت الحالة خطيرة أضف كلمة (🔴 حالة طارئة) بوضوح."
            )
            response = model.generate_content(prompt)
            st.session_state.diag_res = response.text
            
            # تحديد الاختصاص
            st.session_state.spec = "باطنية"
            for s in ["قلبية", "باطنية", "جملة عصبية", "مفاصل"]:
                if s in response.text: st.session_state.spec = s; break
            st.session_state.diag_ready = True

    if st.session_state.get('diag_ready'):
        # تحويل "حالة طارئة" إلى تنبيه أحمر
        final_text = st.session_state.diag_res.replace("حالة طارئة", '<span class="emergency-alert">🔴 حالة طارئة</span>')
        st.markdown(f'<div style="background:#111; padding:20px; border-radius:15px; border-right:6px solid #40E0D0;">{final_text}</div>', unsafe_allow_html=True)
        
        # عرض الأطباء بناءً على الموقع المكتشف سلفاً
        u_lat, u_lon = st.session_state.detected_location['lat'], st.session_state.detected_location['lon']
        matches = [d for d in DATA["أطباء"] if d['s'] == st.session_state.spec]
        for d in matches: d['d_km'] = calculate_dist(u_lat, u_lon, d['lat'], d['lon'])
        sorted_docs = sorted(matches, key=lambda x: x['d_km'])

        st.write("### الأطباء المتاحون في منطقتك:")
        for idx, d in enumerate(sorted_docs):
            is_best = "⭐ الأقرب لموقعك المكتشف" if idx == 0 else ""
            st.markdown(f'''
                <div class="doc-card">
                    <span class="recommend-badge">{is_best}</span>
                    <b style="font-size:20px; color:#40E0D0;">{d['n']}</b><br>
                    <small>الاختصاص: {d['s']} | الموقع: {d['a']}</small><br>
                    <span>يبعد {d['d_km']:.1f} كم عنك 📍</span>
                </div>
            ''', unsafe_allow_html=True)
            
            # عرض المواعيد (مفتوحة ومغلقة)
            cols = st.columns(len(d['slots']))
            for i, (slot, is_open) in enumerate(d['slots'].items()):
                if is_open:
                    if cols[i].button(f"✅ {slot}", key=f"b-{d['n']}-{slot}"):
                        st.session_state.selected_doc = d
                        st.session_state.final_time = slot
                        st.session_state.step = 3
                        st.rerun()
                else:
                    cols[i].button(f"🔒 {slot}", key=f"l-{d['n']}-{slot}", disabled=True)

# --- المرحلة 3: صفحة النجاح (أنيقة ورصينة) ---
elif st.session_state.step == 3:
    st.markdown(f'''
        <div class="success-panel">
            <h1 style="color:#40E0D0; margin-bottom:15px;">تم الحجز بنجاح ✅</h1>
            <p style="font-size:18px;">المريض: <b>{st.session_state.p_info['name']}</b></p>
            <hr style="border:0.5px solid #333; width:60%; margin: 20px auto;">
            <div style="text-align:right; display:inline-block; line-height:2;">
                <p>👨‍⚕️ <b>الطبيب المختص:</b> {st.session_state.selected_doc['n']}</p>
                <p>⏰ <b>وقت الحجز:</b> {st.session_state.final_time}</p>
                <p>📍 <b>العنوان:</b> {st.session_state.selected_doc['a']}</p>
                <p>📞 <b>للتواصل والاستفسار:</b> <span style="color:#40E0D0;">{st.session_state.selected_doc['phone']}</span></p>
            </div>
            <br><br>
            <h3 style="color:#40E0D0;">نتمنى لك الصحة والسلامة التامة 💐</h3>
        </div>
    ''', unsafe_allow_html=True)
    if st.button("إغلاق والعودة"):
        st.session_state.step = 1
        st.rerun()
