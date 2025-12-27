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

# --- 2. اكتشاف الموقع تلقائياً ---
def detect_user_location_by_ip():
    try:
        response = requests.get('https://ipapi.co/json/', timeout=5).json()
        return {
            "city": response.get("city", "بغداد"),
            "region": response.get("region", "العراق"),
            "lat": response.get("latitude", 33.3152),
            "lon": response.get("longitude", 44.3661)
        }
    except:
        return {"city": "بغداد", "region": "اليرموك", "lat": 33.3152, "lon": 44.3661}

# --- 3. التصميم CSS المطور للمحاذاة والبطاقات ---
st.set_page_config(page_title="AI DR Baghdad", layout="centered")
st.markdown(r'''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    
    /* ضبط الاتجاه العام لليمين */
    .main, .stApp { 
        direction: rtl; 
        text-align: right; 
        background-color: #050505; 
        color: #e0e0e0; 
    }
    * { font-family: 'Tajawal', sans-serif; }

    /* تنبيه الموقع */
    .location-banner { background: rgba(64, 224, 208, 0.1); padding: 12px; border-radius: 10px; border: 1px solid #40E0D0; color: #40E0D0; font-weight: bold; text-align: center; margin-bottom: 5px; }
    .legal-disclaimer { font-size: 12px; color: #888; text-align: center; margin-bottom: 25px; }

    /* بطاقة الطبيب */
    .doc-card { 
        background: #0d0d0d; 
        padding: 20px; 
        border-radius: 15px; 
        border: 1px solid #333; 
        margin-bottom: 25px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .recommend-badge { background: #40E0D0; color: black; padding: 2px 10px; border-radius: 20px; font-size: 11px; font-weight: bold; margin-bottom: 10px; display: inline-block; }
    .emergency-alert { color: #FF0000; font-weight: bold; font-size: 18px; border: 2px solid #FF0000; padding: 10px; border-radius: 8px; display: block; margin: 15px 0; text-align: center; }
    .star-color { color: #FFD700; font-size: 14px; }
    
    /* صفحة النجاح */
    .success-panel { border: 2px solid #40E0D0; padding: 40px; border-radius: 25px; background: rgba(64, 224, 208, 0.05); text-align: center; }
    
    /* تحسين شكل المدخلات */
    .stTextInput input, .stTextArea textarea { text-align: right; direction: rtl; }
    </style>
    ''', unsafe_allow_html=True)

# --- 4. قاعدة البيانات الموسعة ---
DATA = {
    "أطباء": [
        {"n": "د. علي الركابي", "s": "قلبية", "a": "الحارثية", "lat": 33.3222, "lon": 44.3585, "stars": 5, "slots": {"04:00 PM": True, "05:00 PM": False}, "phone": "07701234567"},
        {"n": "د. سارة الجبوري", "s": "قلبية", "a": "المنصور", "lat": 33.3251, "lon": 44.3482, "stars": 4, "slots": {"06:00 PM": True, "07:30 PM": True}, "phone": "07801112223"},
        {"n": "د. حيدر السلطاني", "s": "باطنية", "a": "اليرموك", "lat": 33.3121, "lon": 44.3610, "stars": 5, "slots": {"03:00 PM": True, "04:00 PM": False}, "phone": "07712312312"},
        {"n": "د. مريم القيسي", "s": "مفاصل", "a": "الكرادة", "lat": 33.3135, "lon": 44.4291, "stars": 5, "slots": {"05:00 PM": True, "06:00 PM": False}, "phone": "07901231234"},
        {"n": "د. طه العسكري", "s": "باطنية", "a": "حي الجامعة", "lat": 33.3330, "lon": 44.3280, "stars": 4, "slots": {"08:00 PM": True}, "phone": "07801212123"}
    ]
}

def calculate_dist(lat1, lon1, lat2, lon2):
    return math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2) * 111.13

if 'step' not in st.session_state: st.session_state.step = 1

# --- المرحلة 1: الدخول ---
if st.session_state.step == 1:
    st.markdown("<h1 style='text-align:center; color:#40E0D0;'>AI Doctor 🩺", unsafe_allow_html=True)
    
    with st.spinner("جاري اكتشاف الموقع..."):
        user_loc = detect_user_location_by_ip()
        st.session_state.detected_location = user_loc

    st.markdown(f'<div class="location-banner">📍 موقعك المكتشف: {user_loc["city"]} - {user_loc["region"]}</div>', unsafe_allow_html=True)
    st.markdown('<div class="legal-disclaimer">⚠️ تنبيه: هذا الموقع استشاري ذكي ولا يغني عن استشارة الطبيب المختص.</div>', unsafe_allow_html=True)
    
    name = st.text_input("الأسم الكامل")
    phone = st.text_input("رقم الهاتف")
    age = st.number_input("العمر", min_value=1, max_value=120, value=25)
    
    if st.button("دخول النظام"):
        if name and phone:
            st.session_state.p_info = {"name": name, "phone": phone, "age": age}
            st.session_state.step = 2
            st.rerun()

# --- المرحلة 2: التحليل والتشخيص ---
elif st.session_state.step == 2:
    st.markdown(f">AI DR ⛑️</h1>. {st.session_state.p_info['name']}</h3>", unsafe_allow_html=True)
    text = st.text_area("اشرح حالتك الصحية بالتفصيل:")

    if st.button("بدء تحليل الذكاء الاصطناعي"):
        with st.spinner("جاري تحليل الأعراض..."):
            u_loc = st.session_state.detected_location
            prompt = (f"حلل في سطرين فقط: '{text}'. المريض في {u_loc['city']}. "
                      f"اذكر الاختصاص بالنسب المئوية، التشخيص، وإذا كانت الحالة خطيرة أضف كلمة (🔴 حالة طارئة).")
            response = model.generate_content(prompt)
            st.session_state.diag_res = response.text
            
            st.session_state.spec = "باطنية"
            for s in ["قلبية", "باطنية", "جملة عصبية", "مفاصل"]:
                if s in response.text: st.session_state.spec = s; break
            st.session_state.diag_ready = True

    if st.session_state.get('diag_ready'):
        final_text = st.session_state.diag_res.replace("حالة طارئة", '<span class="emergency-alert">🔴 حالة طارئة</span>')
        st.markdown(f'<div style="background:#111; padding:20px; border-radius:15px; border-right:6px solid #40E0D0; margin-bottom:30px; text-align:right;">{final_text}</div>', unsafe_allow_html=True)
        
        # فلترة وترتيب الأطباء
        u_lat, u_lon = st.session_state.detected_location['lat'], st.session_state.detected_location['lon']
        matches = [d for d in DATA["أطباء"] if d['s'] == st.session_state.spec]
        for d in matches: d['d_km'] = calculate_dist(u_lat, u_lon, d['lat'], d['lon'])
        sorted_docs = sorted(matches, key=lambda x: x['d_km'])

        st.write("### 👨‍⚕️ الأطباء المرشحون لحالتك:")
        for idx, d in enumerate(sorted_docs):
            with st.container():
                is_best = '<div class="recommend-badge">⭐ الأقرب لموقعك</div>' if idx == 0 else ""
                st.markdown(f'''
                    <div class="doc-card">
                        {is_best}
                        <div style="font-size:20px; color:#40E0D0; font-weight:bold;">{d['n']}</div>
                        <div style="color:#aaa; font-size:14px;">اختصاص: {d['s']} | الموقع: {d['a']}</div>
                        <div class="star-color">التقييم: {"★" * d['stars']}</div>
                        <div style="font-size:13px; margin-top:5px;">📍 يبعد عنك مسافة {d['d_km']:.1f} كم</div>
                    </div>
                ''', unsafe_allow_html=True)
                
                # عرض المواعيد بشكل شبكة
                cols = st.columns(3)
                for i, (slot, is_open) in enumerate(d['slots'].items()):
                    with cols[i % 3]:
                        if is_open:
                            if st.button(f"✅ {slot}", key=f"b-{d['n']}-{slot}"):
                                st.session_state.selected_doc = d
                                st.session_state.final_time = slot
                                st.session_state.step = 3
                                st.rerun()
                        else:
                            st.button(f"🔒 {slot}", key=f"l-{d['n']}-{slot}", disabled=True)
                st.markdown("<br>", unsafe_allow_html=True)

# --- المرحلة 3: صفحة النجاح ---
elif st.session_state.step == 3:
    st.markdown(f'''
        <div class="success-panel">
            <h1 style="color:#40E0D0;">تم تأكيد الحجز ✅</h1>
            <p>المريض: <b>{st.session_state.p_info['name']}</b></p>
            <hr style="border:0.1px solid #333; width:70%; margin:20px auto;">
            <div style="text-align:right; display:inline-block; line-height:2;">
                <p>👨‍⚕️ <b>الطبيب:</b> {st.session_state.selected_doc['n']}</p>
                <p>⏰ <b>الموعد:</b> {st.session_state.final_time}</p>
                <p>📍 <b>العنوان:</b> {st.session_state.selected_doc['a']}</p>
                <p>📞 <b>للتواصل:</b> <span style="color:#40E0D0;">{st.session_state.selected_doc['phone']}</span></p>
            </div>
            <br><br>
            <h3 style="color:#40E0D0;">نتمنى لكم تمام الصحة والسلامة 💐</h3>
        </div>
    ''', unsafe_allow_html=True)
    if st.button("العودة للرئيسية"):
        st.session_state.step = 1
        st.rerun()
