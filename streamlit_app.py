import streamlit as st
import math
import google.generativeai as genai
import requests

# --- 1. إعدادات الصفحة والخطوط ---
st.set_page_config(page_title="AI Doctor Baghdad", layout="centered")

# تم إصلاح طريقة كتابة CSS لضمان عدم حدوث SyntaxError
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif;
        direction: rtl;
        text-align: right;
    }
    
    .stApp { background-color: #0b1016; color: white; }

    /* تنبيه إخلاء المسؤولية */
    .disclaimer {
        background-color: rgba(255, 75, 75, 0.1);
        border: 1px solid #ff4b4b;
        color: #ff4b4b;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 20px;
        font-size: 0.9rem;
    }

    /* صندوق التشخيص الأنيق */
    .diag-box {
        background: #161b22;
        border-right: 5px solid #40E0D0;
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
        border-top: 1px solid #30363d;
    }

    .wish-text {
        color: #40E0D0;
        font-weight: bold;
        text-align: center;
        font-size: 1.2rem;
    }

    /* بطاقة الطبيب */
    .doctor-card {
        background: #1c2128;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #30363d;
        margin-bottom: 10px;
    }
    
    .star-rating { color: #ffca28; }
    .dist-tag { color: #40E0D0; font-size: 0.8rem; border: 1px solid #40E0D0; padding: 2px 5px; border-radius: 4px; }
    
    /* تعديل محاذاة المدخلات */
    input, textarea { direction: rtl !important; text-align: right !important; }
    </style>
""", unsafe_allow_html=True)

# --- 2. الوظائف البرمجية ---
def get_distance(lat1, lon1, lat2, lon2):
    return round(math.sqrt((lat1-lat2)**2 + (lon1-lon2)**2) * 111, 1)

def detect_user_location():
    try:
        r = requests.get('https://ipapi.co/json/', timeout=3).json()
        return {"city": r.get("city", "بغداد"), "lat": r.get("latitude", 33.3152), "lon": r.get("longitude", 44.3661)}
    except:
        return {"city": "بغداد", "lat": 33.3152, "lon": 44.3661}

# إعداد الذكاء الاصطناعي
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None

# --- 3. قاعدة البيانات ---
DATA = {
    "أطباء": [
        {"n": "د. علي الركابي", "s": "قلبية", "a": "الحارثية", "lat": 33.3222, "lon": 44.3585, "stars": 5, "slots": {"04:00 PM": True, "05:00 PM": False}},
        {"n": "د. سارة الجبوري", "s": "قلبية", "a": "المنصور", "lat": 33.3251, "lon": 44.3482, "stars": 4, "slots": {"06:00 PM": True, "07:00 PM": True}},
        {"n": "د. حيدر السلطاني", "s": "باطنية", "a": "اليرموك", "lat": 33.3121, "lon": 44.3610, "stars": 5, "slots": {"03:00 PM": True, "04:00 PM": False}}
    ]
}

if 'step' not in st.session_state: st.session_state.step = 1

# --- المرحلة 1: البداية ---
if st.session_state.step == 1:
    st.markdown('<div class="disclaimer">⚠️ الموقع افتراضي للذكاء الاصطناعي. لا يعتد به كاستشارة طبية رسمية.</div>', unsafe_allow_html=True)
    
    loc = detect_user_location()
    st.session_state.user_loc = loc
    
    st.markdown(f"<h1 style='text-align:center; color:#40E0D0;'>AI Doctor 🩺</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center;'>📍 موقعك المكتشف: <b>{loc['city']}</b></p>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        name = st.text_input("الأسم الكامل")
        phone = st.text_input("رقم الهاتف")
        if st.button("دخول النظام", use_container_width=True):
            if name and phone:
                st.session_state.p_info = {"name": name, "phone": phone}
                st.session_state.step = 2
                st.rerun()

# --- المرحلة 2: التحليل والأطباء ---
elif st.session_state.step == 2:
    st.markdown(f"### مرحباً بك يا {st.session_state.p_info['name']} ⛑️")
    text = st.text_area("اشرح حالتك الصحية بالتفصيل:")

    if st.button("بدء التحليل الذكي", use_container_width=True):
        if model and text:
            with st.spinner("جاري تحليل حالتك..."):
                prompt = f"حلل الأعراض التالية: {text}. اعطِ تشخيصاً محتملاً بنسبة مئوية وسطرين شرح بأسلوب طبي هادئ."
                res = model.generate_content(prompt).text
                st.session_state.diag = res
                st.session_state.spec = "قلبية" if any(x in res for x in ["قلب", "صدر", "تنفس"]) else "باطنية"
                st.session_state.ready = True

    if st.session_state.get('ready'):
        st.markdown(f'<div class="diag-box"><b>🔍 نتيجة التحليل:</b><br>{st.session_state.diag}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="wish-text">نتمنى لك الشفاء العاجل يا {st.session_state.p_info['name']} ❤️</div>', unsafe_allow_html=True)
        
        st.write("---")
        st.subheader("الأطباء الأقرب إليك حسب موقعك:")
        
        u = st.session_state.user_loc
        matches = [d for d in DATA["أطباء"] if d['s'] == st.session_state.spec]
        for d in matches: d['dist'] = get_distance(u['lat'], u['lon'], d['lat'], d['lon'])
        matches.sort(key=lambda x: x['dist'])

        for d in matches:
            with st.container():
                st.markdown(f"""
                    <div class="doctor-card">
                        <span class="star-rating">{'★' * d['stars']}</span>
                        <b>{d['n']}</b> <span class="dist-tag">يبعد {d['dist']} كم</span><br>
                        <small>📍 {d['a']} | اختصاص {d['s']}</small>
                    </div>
                """, unsafe_allow_html=True)
                
                cols = st.columns(len(d['slots']))
                for i, (slot, avail) in enumerate(d['slots'].items()):
                    if avail:
                        if cols[i].button(f"✅ {slot}", key=f"{d['n']}-{slot}"):
                            st.session_state.selected_doc, st.session_state.time, st.session_state.step = d, slot, 3
                            st.rerun()
                    else:
                        cols[i].button(f"❌ {slot}", disabled=True, key=f"{d['n']}-{slot}")

# --- المرحلة 3: التذكرة ---
elif st.session_state.step == 3:
    st.balloons()
    st.markdown(f"""
        <div style="background:white; color:black; padding:30px; border-radius:15px; text-align:center; direction:rtl;">
            <h2 style="color:#0b1016;">تم تأكيد الحجز بنجاح ✅</h2>
            <hr>
            <p>المريض: <b>{st.session_state.p_info['name']}</b></p>
            <p>الطبيب: <b>{st.session_state.selected_doc['n']}</b></p>
            <p>الموعد: <b>{st.session_state.time}</b></p>
            <p>العنوان: <b>{st.session_state.selected_doc['a']}</b></p>
            <hr>
            <h4 style="color:#40E0D0;">نتمنى لك الشفاء العاجل 🌿</h4>
        </div>
    """, unsafe_allow_html=True)
    if st.button("العودة للرئيسية"):
        st.session_state.step = 1
        st.rerun()
