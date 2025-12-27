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

# --- 2. وظيفة الموقع ---
def detect_user_location_by_ip():
    try:
        response = requests.get('https://ipapi.co/json/', timeout=5).json()
        return {
            "city": response.get("city", "بغداد"),
            "region": response.get("region", "تحديد تلقائي"),
            "lat": response.get("latitude", 33.3152),
            "lon": response.get("longitude", 44.3661)
        }
    except:
        return {"city": "بغداد", "region": "اليرموك", "lat": 33.3152, "lon": 44.3661}

# --- 3. التصميم CSS (تحديث شامل للخطوط والمحاذاة) ---
st.set_page_config(page_title="AI Doctor", layout="centered")
st.markdown(r'''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');
    * { font-family: 'Tajawal', sans-serif; direction: rtl; }
    .stApp { background-color: #050505; color: #e0e0e0; }
    
    .main-title { text-align: center; color: #40E0D0; font-weight: 700; margin-bottom: 20px; }
    .welcome-text { text-align: center; color: #ffffff; font-size: 24px; margin-bottom: 25px; }
    .user-name { color: #40E0D0; font-weight: bold; }
    
    .location-banner { background: rgba(64, 224, 208, 0.05); padding: 12px; border-radius: 10px; border: 1px dashed #40E0D0; color: #40E0D0; text-align: center; margin-bottom: 10px; }
    .disclaimer-box { background: rgba(255, 255, 255, 0.02); border-right: 4px solid #f1c40f; padding: 15px; border-radius: 8px; font-size: 0.85rem; color: #bbb; margin-bottom: 20px; text-align: right; }
    
    .emergency-alert { color: #FF4B4B; font-weight: bold; border: 1px solid #FF4B4B; padding: 8px; border-radius: 8px; background: rgba(255, 75, 75, 0.1); display: block; margin: 10px 0; }
    
    .doc-card { background: #0f0f0f; padding: 20px; border-radius: 15px; border: 1px solid #222; margin-top: 25px; position: relative; }
    .doc-info { margin-bottom: 15px; }
    .spec-tag { background: #40E0D0; color: #000; padding: 2px 8px; border-radius: 5px; font-size: 12px; font-weight: bold; margin-left: 10px; }
    .star-rating { color: #f1c40f; font-size: 14px; }
    
    /* تنسيق أزرار المواعيد الأفقية */
    div.stButton > button { width: 100%; border-radius: 8px; font-size: 12px; }
    </style>
    ''', unsafe_allow_html=True)

# --- 4. قاعدة البيانات (مواعيد محددة 3-8) ---
DATA = {
    "أطباء": [
        {"n": "د. علي الركابي", "s": "قلبية", "a": "الحارثية", "lat": 33.3222, "lon": 44.3585, "stars": 5, "slots": {"03:00 PM": True, "04:30 PM": False, "06:00 PM": True, "07:30 PM": True}, "phone": "07701234567"},
        {"n": "د. سارة الجبوري", "s": "قلبية", "a": "المنصور", "lat": 33.3251, "lon": 44.3482, "stars": 4, "slots": {"03:30 PM": True, "05:00 PM": True, "06:30 PM": False, "08:00 PM": True}, "phone": "07801112223"},
        {"n": "د. مريم القيسي", "s": "مفاصل", "a": "الكرادة", "lat": 33.3135, "lon": 44.4291, "stars": 5, "slots": {"04:00 PM": True, "05:30 PM": True, "07:00 PM": False}, "phone": "07901231234"},
        {"n": "د. طه العسكري", "s": "باطنية", "a": "اليرموك", "lat": 33.3121, "lon": 44.3610, "stars": 3, "slots": {"03:00 PM": False, "05:00 PM": True, "07:00 PM": True}, "phone": "07801212123"}
    ]
}

def calculate_dist(lat1, lon1, lat2, lon2):
    return math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2) * 111.13

if 'step' not in st.session_state: st.session_state.step = 1

# --- المرحلة 1: الدخول ---
if st.session_state.step == 1:
    st.markdown("<h1 class='main-title'>AI Doctor 🩺</h1>", unsafe_allow_html=True)
    
    with st.spinner("جاري تحديد موقعك تلقائياً..."):
        user_loc = detect_user_location_by_ip()
        st.session_state.detected_location = user_loc

    st.markdown(f'<div class="location-banner">📍 موقعك الحالي: {user_loc["city"]} - {user_loc["region"]}</div>', unsafe_allow_html=True)
    
    st.markdown('''<div class="disclaimer-box">⚠️ <b>تنبيه استشاري:</b> هذا النظام هو أداة مساعدة تعمل بالذكاء الاصطناعي لتوجيهك، ولا يعتبر بديلاً عن الفحص الطبي المباشر.</div>''', unsafe_allow_html=True)
    
    name = st.text_input("الأسم الكامل")
    phone = st.text_input("رقم الهاتف")
    
    if st.button("دخول النظام", use_container_width=True):
        if name and phone:
            st.session_state.p_info = {"name": name, "phone": phone}
            st.session_state.step = 2
            st.rerun()
        else:
            st.error("يرجى إكمال البيانات")

# --- المرحلة 2: التشخيص وعرض الأطباء ---
elif st.session_state.step == 2:
    st.markdown(f'<div class="welcome-text">Welcome to <span style="color:#40E0D0;">AI Doctor</span> ⛑️<br><span class="user-name">{st.session_state.p_info["name"]}</span></div>', unsafe_allow_html=True)
    
    text = st.text_area("اشرح حالتك الصحية باختصار:", placeholder="مثال: ألم شديد في المفاصل مع حرارة...")

    if st.button("بدء التحليل", use_container_width=True):
        with st.spinner("جاري التحليل ومطابقة الأطباء الأنسب..."):
            prompt = (
                f"حلل في سطرين فقط: '{text}'. اذكر التشخيص المبدئي بنسبة مئوية. "
                f"ثم حدد الطبيب الأنسب من حيث (القرب، التقييم، وتوفر الوقت). "
                f"إذا كانت الحالة خطرة أضف (🔴 حالة طارئة)."
            )
            response = model.generate_content(prompt)
            st.session_state.diag_res = response.text
            
            st.session_state.spec = "باطنية"
            for s in ["قلبية", "باطنية", "مفاصل"]:
                if s in response.text: st.session_state.spec = s; break
            st.session_state.diag_ready = True

    if st.session_state.get('diag_ready'):
        final_text = st.session_state.diag_res.replace("حالة طارئة", '<span class="emergency-alert">🔴 حالة طارئة - توجه للمشفى فوراً</span>')
        st.markdown(f'<div style="background:#111; padding:20px; border-radius:15px; border-right:5px solid #40E0D0; line-height:1.6;">{final_text}</div>', unsafe_allow_html=True)
        
        st.write("---")
        st.subheader("الأطباء المتاحون (الأقرب والأعلى تقييماً):")

        u_lat, u_lon = st.session_state.detected_location['lat'], st.session_state.detected_location['lon']
        matches = [d for d in DATA["أطباء"] if d['s'] == st.session_state.spec]
        for d in matches: d['d_km'] = calculate_dist(u_lat, u_lon, d['lat'], d['lon'])
        sorted_docs = sorted(matches, key=lambda x: (-x['stars'], x['d_km']))

        for d in sorted_docs:
            with st.container():
                st.markdown(f'''
                    <div class="doc-card">
                        <div class="doc-info">
                            <b style="font-size:18px; color:#40E0D0;">{d['n']}</b> <span class="spec-tag">{d['s']}</span>
                            <div class="star-rating">{"⭐" * d['stars']} | يبعد {d['d_km']:.1f} كم عنك</div>
                            <div style="font-size:13px; color:#888;">📍 {d['a']}</div>
                        </div>
                    </div>
                ''', unsafe_allow_html=True)
                
                # عرض المواعيد أفقياً
                slots = d['slots']
                cols = st.columns(len(slots))
                for i, (slot, is_open) in enumerate(slots.items()):
                    if is_open:
                        if cols[i].button(f"✅ {slot}", key=f"b-{d['n']}-{slot}"):
                            st.session_state.selected_doc = d
                            st.session_state.final_time = slot
                            st.session_state.step = 3
                            st.rerun()
                    else:
                        cols[i].button(f"🔒 {slot}", key=f"l-{d['n']}-{slot}", disabled=True)

# --- المرحلة 3: صفحة النجاح ---
elif st.session_state.step == 3:
    st.markdown(f'''
        <div style="text-align:center; padding:40px; border:1px solid #40E0D0; border-radius:20px; background:rgba(64,224,208,0.02);">
            <h2 style="color:#40E0D0;">تم الحجز بنجاح ✅</h2>
            <p>المريض: <b>{st.session_state.p_info['name']}</b></p>
            <hr style="border:0.1px solid #333;">
            <p>👨‍⚕️ الطبيب: {st.session_state.selected_doc['n']}</p>
            <p>⏰ الوقت: {st.session_state.final_time}</p>
            <p>📍 العنوان: {st.session_state.selected_doc['a']}</p>
            <p>📞 للتواصل: {st.session_state.selected_doc['phone']}</p>
        </div>
    ''', unsafe_allow_html=True)
    if st.button("إغلاق والعودة", use_container_width=True):
        st.session_state.step = 1
        st.rerun()
