[10:23 PM, 12/27/2025] M. K. Al-Hayani: import streamlit as st
import math
import google.generativeai as genai
import requests

# --- 1. إعدادات الصفحة والخطوط ---
st.set_page_config(page_title="AI Doctor", layout="centered")

# إضافة خط Cairo وتنسيقات CSS احترافية
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Cairo', sans-serif;
        direction: rtl;
        text-align: right;
    }
    
    .stApp {
        background-color: #0e1117;
    }

    /* تنسيق الحقول لتكون من اليمين لليسار */
    input, textarea {
        direction: rtl !important;
        text-align: right !important;
    }

    /* مركزية العناوين */
    .main-title {
        text-align: cent…
[10:33 PM, 12/27/2025] M. K. Al-Hayani: import streamlit as st
import math
import google.generativeai as genai
import requests

# --- إعدادات الصفحة ---
st.set_page_config(page_title="AI Doctor Baghdad", layout="centered")

# --- التنسيق الجمالي (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; }
    .stApp { background-color: #0b0e14; color: white; }
    
    /* صندوق التشخيص الأنيق */
    .diag-box {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-right: 5px solid #40E0D0;
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .wish-text { color: #40E0D0; font-weight: bold; font-size: 1.2rem; text-align: center; margin-top: 10px; }
    
    /* بطاقة الطبيب */
    .doctor-card {
        background: #1a1f26;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #333;
        margin-bottom: 10px;
    }
    .star-rating { color: #ffca28; font-size: 1.1rem; }
    .distance-tag { background: #40E0D022; color: #40E0D0; padding: 2px 8px; border-radius: 5px; font-size: 0.8rem; }
    </style>
""", unsafe_allow_html=True)

# --- وظائف حسابية وتقنية ---
def get_distance(lat1, lon1, lat2, lon2):
    return round(math.sqrt((lat1-lat2)**2 + (lon1-lon2)**2) * 111, 1)

def detect_user_location():
    try:
        r = requests.get('https://ipapi.co/json/', timeout=3).json()
        return {"city": r.get("city", "بغداد"), "lat": r.get("latitude", 33.3152), "lon": r.get("longitude", 44.3661)}
    except:
        return {"city": "بغداد", "lat": 33.3152, "lon": 44.3661}

def init_gemini():
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        return genai.GenerativeModel('gemini-1.5-flash')
    return None

# --- قاعدة بيانات الأطباء ---
DATA = {
    "أطباء": [
        {"n": "د. علي الركابي", "s": "قلبية", "a": "الحارثية", "lat": 33.3222, "lon": 44.3585, "stars": 5, "slots": {"04:00 PM": True, "05:00 PM": False}},
        {"n": "د. سارة الجبوري", "s": "قلبية", "a": "المنصور", "lat": 33.3251, "lon": 44.3482, "stars": 4, "slots": {"06:00 PM": True, "07:00 PM": True}},
        {"n": "د. حيدر السلطاني", "s": "باطنية", "a": "اليرموك", "lat": 33.3121, "lon": 44.3610, "stars": 5, "slots": {"03:00 PM": True, "04:00 PM": False}}
    ]
}

if 'step' not in st.session_state: st.session_state.step = 1
model = init_gemini()

# --- المرحلة 1: التنبيه والموقع ---
if st.session_state.step == 1:
    st.warning("⚠️ تنبيه: هذا الموقع افتراضي للذكاء الاصطناعي ولا يغني عن الاستشارة الطبية المتخصصة.")
    loc = detect_user_location()
    st.session_state.user_loc = loc
    st.markdown(f"<h1 style='text-align:center;'>AI Doctor 🩺</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center;'>📍 موقعك المكتشف: <b>{loc['city']}</b></p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        name = st.text_input("الأسم")
        phone = st.text_input("الهاتف")
        if st.button("بدء الفحص", use_container_width=True):
            if name and phone:
                st.session_state.p_info = {"name": name, "phone": phone}
                st.session_state.step = 2
                st.rerun()

# --- المرحلة 2: التحليل والنتائج ---
elif st.session_state.step == 2:
    st.markdown(f"### مرحباً بك، {st.session_state.p_info['name']}")
    text = st.text_area("اشرح ما تشعر به:")
    
    if st.button("تحليل الحالة", use_container_width=True):
        if model and text:
            with st.spinner("جاري تحليل الأعراض..."):
                prompt = f"حلل الحالة: '{text}'. اعطِ تشخيصاً محتملاً مع نسبة مئوية للدقة وسطرين شرح. اجعل الرد بصيغة: [التشخيص]: ... [النسبة]: %... [الشرح]: ..."
                res = model.generate_content(prompt).text
                st.session_state.diag_res = res
                st.session_state.spec = "قلبية" if any(x in res for x in ["قلب", "صدر", "تنفس"]) else "باطنية"
                st.session_state.ready = True

    if st.session_state.get('ready'):
        # عرض التشخيص بشكل أنيق
        st.markdown(f"""
            <div class="diag-box">
                {st.session_state.diag_res}
            </div>
            <div class="wish-text">نتمنى لك الشفاء العاجل يا {st.session_state.p_info['name']} ❤️</div>
        """, unsafe_allow_html=True)
        
        st.write("---")
        st.subheader("الأطباء المقترحون (الأقرب إليك أولاً):")
        
        # حساب المسافة وترتيب الأطباء
        u = st.session_state.user_loc
        matches = [d for d in DATA["أطباء"] if d['s'] == st.session_state.spec]
        for d in matches: d['dist'] = get_distance(u['lat'], u['lon'], d['lat'], d['lon'])
        matches.sort(key=lambda x: x['dist'])

        for d in matches:
            with st.container():
                st.markdown(f"""
                    <div class="doctor-card">
                        <span class="star-rating">{'⭐' * d['stars']}</span>
                        <b style="font-size:1.1rem;">{d['n']}</b> <span class="distance-tag">{d['dist']} كم بعيداً</span><br>
                        <small>📍 {d['a']} | اختصاص {d['s']}</small>
                    </div>
                """, unsafe_allow_html=True)
                
                cols = st.columns(len(d['slots']))
                for i, (slot, available) in enumerate(d['slots'].items()):
                    if available:
                        if cols[i].button(f"✅ {slot}", key=f"{d['n']}-{slot}"):
                            st.session_state.selected_doc, st.session_state.time, st.session_state.step = d, slot, 3
                            st.rerun()
                    else:
                        cols[i].button(f"❌ {slot}", disabled=True, key=f"{d['n']}-{slot}")

# --- المرحلة 3: تذكرة الحجز ---
elif st.session_state.step == 3:
    st.balloons()
    st.markdown(f"""
        <div style="background:white; color:black; padding:30px; border-radius:15px; text-align:center;">
            <h2>تذكرة حجز موعد 🎫</h2>
            <hr>
            <p>المريض: <b>{st.session_state.p_info['name']}</b></p>
            <p>الطبيب: <b>{st.session_state.selected_doc['n']}</b></p>
            <p>الموعد: <b>{st.session_state.time}</b></p>
            <p>الموقع: <b>{st.session_state.selected_doc['a']}</b></p>
            <br>
            <h4 style="color:green;">تم الحجز بنجاح!</h4>
        </div>
    """, unsafe_allow_html=True)
    if st.button("حجز جديد"):
        st.session_state.step = 1
        st.rerun()
