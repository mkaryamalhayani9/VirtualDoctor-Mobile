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
    st.error(f"❌ خطأ اتصال")

# --- 2. وظيفة اكتشاف الموقع ---
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

# --- 3. التصميم CSS المطور (تنسيق التذكرة والوصف) ---
st.set_page_config(page_title="AI Doctor 🩺", layout="centered")
st.markdown(r'''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    
    .stApp { 
        direction: rtl; text-align: right; background-color: #050505; color: #e0e0e0; font-family: 'Tajawal', sans-serif;
    }

    /* تنسيق وصف الذكاء الاصطناعي المرتب */
    .ai-res-box { 
        background: rgba(64, 224, 208, 0.05); padding: 20px; border-radius: 15px; border-right: 5px solid #40E0D0; 
        line-height: 1.8; font-size: 16px; margin-bottom: 20px; 
    }
    .ai-label { color: #40E0D0; font-weight: bold; margin-left: 5px; }

    /* تصميم التذكرة المقطع (Ticket Style) */
    .ticket {
        background: #111; border: 2px dashed #40E0D0; padding: 30px; border-radius: 20px; 
        position: relative; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.5); margin: 20px 0;
    }
    .ticket::before, .ticket::after {
        content: ''; position: absolute; top: 50%; width: 30px; height: 30px;
        background: #050505; border-radius: 50%; transform: translateY(-50%);
    }
    .ticket::before { left: -17px; border-right: 2px dashed #40E0D0; }
    .ticket::after { right: -17px; border-left: 2px dashed #40E0D0; }

    .doc-card { 
        background: #0d0d0d; padding: 20px; border-radius: 15px; border: 1px solid #222; margin-bottom: 15px; 
    }
    
    .emergency-alert { 
        color: #FF4B4B; border: 2px solid #FF4B4B; padding: 12px; border-radius: 10px; 
        background: rgba(255, 75, 75, 0.1); font-weight: bold; text-align: center; margin: 15px 0; 
    }
    
    .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; height: 45px; }
    </style>
    ''', unsafe_allow_html=True)

# --- 4. قاعدة بيانات الأطباء ---
DATA = {
    "أطباء": [
        {"n": "د. علي الركابي", "s": "قلبية", "a": "الحارثية", "lat": 33.3222, "lon": 44.3585, "stars": 5, "slots": {"04:00 PM": True, "05:00 PM": False, "06:00 PM": True}, "phone": "07701234567"},
        {"n": "د. سارة الجبوري", "s": "قلبية", "a": "المنصور", "lat": 33.3251, "lon": 44.3482, "stars": 4, "slots": {"06:00 PM": True, "07:30 PM": False}, "phone": "07801112223"},
        {"n": "د. حيدر السلطاني", "s": "باطنية", "a": "اليرموك", "lat": 33.3121, "lon": 44.3610, "stars": 5, "slots": {"03:00 PM": True, "04:00 PM": False, "05:00 PM": True}, "phone": "07712312312"},
        {"n": "د. طه العسكري", "s": "باطنية", "a": "حي الجامعة", "lat": 33.3330, "lon": 44.3280, "stars": 4, "slots": {"08:00 PM": True, "09:00 PM": False}, "phone": "07801212123"}
    ]
}

def calculate_dist(lat1, lon1, lat2, lon2):
    return math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2) * 111.13

if 'step' not in st.session_state: st.session_state.step = 1

# --- المرحلة 1: الدخول ---
if st.session_state.step == 1:
    st.markdown('<div style="text-align:center;"><h1 style="color:#40E0D0;">AI Doctor 🩺</h1></div>', unsafe_allow_html=True)
    u_loc = detect_user_location_by_ip()
    st.session_state.detected_location = u_loc
    st.markdown(f'<div style="background:rgba(64,224,208,0.1); padding:15px; border-radius:15px; border:1px solid #40E0D0; text-align:center; max-width:400px; margin: 0 auto 10px auto;">📍 موقعك الحالي: {u_loc["city"]}</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; font-size:12px; color:#888;">النظام استشاري ذكي ولا يغني عن زيارة الطبيب</p>', unsafe_allow_html=True)
    
    name = st.text_input("الأسم الكامل")
    phone = st.text_input("رقم الهاتف")
    if st.button("دخول النظام"):
        if name and phone:
            st.session_state.p_info = {"name": name, "phone": phone}
            st.session_state.step = 2
            st.rerun()

# --- المرحلة 2: التحليل والأطباء ---
elif st.session_state.step == 2:
    st.markdown(f'<h3 style="text-align:right;">أهلاً بك م. {st.session_state.p_info["name"]} ⛑️</h3>', unsafe_allow_html=True)
    text = st.text_area("اشرح حالتك الصحية باختصار:")
    if st.button("بدء التحليل"):
        with st.spinner("جاري تحليل الأعراض..."):
            prompt = f"حلل الأعراض التالية بدقة في سطرين فقط: '{text}'. اذكر الاختصاص بالنسب والتشخيص المبدئي ومدى الخطورة."
            response = model.generate_content(prompt)
            st.session_state.diag_res = response.text
            st.session_state.spec = "باطنية"
            for s in ["قلبية", "باطنية", "جملة عصبية", "مفاصل"]:
                if s in response.text: st.session_state.spec = s; break
            st.session_state.diag_ready = True

    if st.session_state.get('diag_ready'):
        st.markdown(f'''<div class="ai-res-box"><span class="ai-label">🩺 التشخيص الذكي:</span><br>{st.session_state.diag_res}</div>''', unsafe_allow_html=True)

        if any(word in st.session_state.diag_res for word in ["طوارئ", "خطيرة", "فوري"]):
            st.markdown('<div class="emergency-alert">🚨 تنبيه: الحالة تستدعي تدخلاً طبياً فورياً</div>', unsafe_allow_html=True)

        u_lat, u_lon = st.session_state.detected_location['lat'], st.session_state.detected_location['lon']
        matches = [d for d in DATA["أطباء"] if d['s'] == st.session_state.spec]
        for d in matches: d['d_km'] = calculate_dist(u_lat, u_lon, d['lat'], d['lon'])
        sorted_docs = sorted(matches, key=lambda x: x['d_km'])

        st.write("### 👨‍⚕️ الأطباء المتوفرون:")
        for idx, d in enumerate(sorted_docs):
            badge = '<div style="background:#40E0D0; color:#000; padding:2px 10px; border-radius:10px; font-size:10px; display:inline-block; margin-bottom:5px;">⭐ الأقرب إليك</div>' if idx == 0 else ""
            st.markdown(f'''
                <div class="doc-card">
                    {badge}<br>
                    <b style="color:#40E0D0; font-size:20px;">{d['n']}</b><br>
                    <small>اختصاص {d['s']} | عيادة {d['a']}</small><br>
                    <span style="color:#FFD700;">{"★" * d['stars']}</span> | <small>يبعد {d['d_km']:.1f} كم</small>
                </div>
            ''', unsafe_allow_html=True)
            
            cols = st.columns(3)
            for i, (slot, is_open) in enumerate(d['slots'].items()):
                with cols[i % 3]:
                    if is_open:
                        if st.button(f"✅ {slot}", key=f"b-{d['n']}-{slot}"):
                            st.session_state.selected_doc, st.session_state.final_time, st.session_state.step = d, slot, 3
                            st.rerun()
                    else:
                        st.button(f"🔒 {slot}", key=f"l-{d['n']}-{slot}", disabled=True)
            st.write("---")

# --- المرحلة 3: صفحة التذكرة ---
elif st.session_state.step == 3:
    st.markdown(f'''
        <div class="ticket">
            <h2 style="color:#40E0D0; margin-top:0;">تأكيد الحجز بنجاح ✅</h2>
            <p style="font-size:18px;">المريض: <b>{st.session_state.p_info['name']}</b></p>
            <div style="border-top: 1px dashed #333; margin: 20px 0;"></div>
            <div style="text-align:right; display:inline-block; line-height:2.2;">
                <p>👨‍⚕️ <b>الطبيب:</b> {st.session_state.selected_doc['n']}</p>
                <p>⏰ <b>الموعد:</b> {st.session_state.final_time}</p>
                <p>📍 <b>العنوان:</b> عيادة {st.session_state.selected_doc['a']}</p>
                <p>📞 <b>للتواصل:</b> <span style="color:#40E0D0;">{st.session_state.selected_doc['phone']}</span></p>
            </div>
            <div style="border-top: 1px dashed #333; margin: 20px 0;"></div>
            <h4 style="color:#40E0D0; margin-bottom:0;">نتمنى لك السلامة التامة 💐</h4>
        </div>
    ''', unsafe_allow_html=True)
    if st.button("العودة للرئيسية"):
        st.session_state.step = 1
        st.rerun()
