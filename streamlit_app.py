import streamlit as st
import math
import google.generativeai as genai
import requests

# --- 1. إعدادات الذكاء الاصطناعي (نسخة مستقرة) ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # استخدام الموديل الأحدث والأكثر توافقاً
        model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("❌ عذراً، هناك مشكلة في الاتصال بالخادم")

# --- 2. وظائف الموقع والمسافة ---
def detect_user_location():
    try:
        r = requests.get('https://ipapi.co/json/', timeout=5).json()
        return {"city": r.get("city", "بغداد"), "lat": r.get("latitude", 33.3152), "lon": r.get("longitude", 44.3661)}
    except:
        return {"city": "بغداد", "lat": 33.3152, "lon": 44.3661}

def get_dist(lat1, lon1, lat2, lon2):
    return math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2) * 111

# --- 3. التصميم المطور (لابتوب + موبايل) ---
st.set_page_config(page_title="AI DR Baghdad", layout="centered")
st.markdown(r'''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    
    .stApp { 
        direction: rtl; text-align: right; background-color: #050505; color: #e0e0e0; font-family: 'Tajawal', sans-serif;
    }

    /* تنسيق مربع التشخيص الذكي */
    .diag-box {
        background: rgba(64, 224, 208, 0.05); padding: 20px; border-radius: 15px;
        border: 1px solid #222; border-right: 6px solid #40E0D0; margin: 20px 0; line-height: 1.8;
    }

    /* بطاقة الطبيب - إصلاح الخربطة بأسلوب نظيف */
    .doctor-card-ui {
        background: #0d0d0d; border: 1px solid #1a1a1a; padding: 20px; border-radius: 15px; margin-top: 15px;
    }
    .doc-name-text { color: #40E0D0; font-size: 22px; font-weight: bold; display: block; margin-bottom: 5px; }
    .doc-info-text { color: #888; font-size: 14px; margin-bottom: 3px; }
    .doc-rating { color: #FFD700; font-size: 13px; }

    /* التذكرة النهائية (نمط مقطع احترافي) */
    .ticket-view {
        background: #0d0d0d; border: 2px dashed #40E0D0; padding: 35px; border-radius: 25px;
        position: relative; text-align: center; margin: 20px auto; max-width: 550px;
    }
    .ticket-view::before, .ticket-view::after {
        content: ''; position: absolute; top: 50%; width: 30px; height: 30px;
        background: #050505; border-radius: 50%; transform: translateY(-50%);
    }
    .ticket-view::before { left: -17px; border-right: 2px dashed #40E0D0; }
    .ticket-view::after { right: -17px; border-left: 2px dashed #40E0D0; }

    /* تحسين الأزرار والمداخل */
    .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; height: 45px; transition: 0.3s; }
    .stButton>button:hover { background-color: #40E0D0; color: #000; }
    
    /* توسيط نصوص البداية */
    .hero-section { text-align: center; margin-bottom: 30px; }
    </style>
    ''', unsafe_allow_html=True)

# --- 4. قاعدة البيانات (أطباء بغداد) ---
DATA = {
    "أطباء": [
        {"n": "د. علي الركابي", "s": "قلبية", "a": "الحارثية", "lat": 33.3222, "lon": 44.3585, "stars": 5, "slots": ["04:00 PM", "05:00 PM", "06:00 PM"], "phone": "07701234567"},
        {"n": "د. سارة الجبوري", "s": "قلبية", "a": "المنصور", "lat": 33.3251, "lon": 44.3482, "stars": 4, "slots": ["06:00 PM", "07:30 PM"], "phone": "07801112223"},
        {"n": "د. حيدر السلطاني", "s": "باطنية", "a": "اليرموك", "lat": 33.3121, "lon": 44.3610, "stars": 5, "slots": ["03:00 PM", "04:00 PM", "05:00 PM"], "phone": "07712312312"},
        {"n": "د. طه العسكري", "s": "باطنية", "a": "حي الجامعة", "lat": 33.3330, "lon": 44.3280, "stars": 4, "slots": ["08:00 PM", "09:00 PM"], "phone": "07801212123"}
    ]
}

if 'step' not in st.session_state: st.session_state.step = 1

# --- المرحلة 1: واجهة الدخول (توسيط كامل) ---
if st.session_state.step == 1:
    st.markdown('<div class="hero-section">', unsafe_allow_html=True)
    st.markdown("<h1 style='color:#40E0D0; font-size: 3rem;'>AI Doctor 🩺</h1>", unsafe_allow_html=True)
    loc = detect_user_location()
    st.session_state.user_loc = loc
    st.markdown(f"<p style='color:#888; font-size: 1.2rem;'>📍 مرحباً بك في {loc['city']}</p>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        name = st.text_input("الأسم الكامل", placeholder="مثال: مريم علي")
        phone = st.text_input("رقم الهاتف", placeholder="07XXXXXXXXX")
        if st.button("دخول النظام"):
            if name and phone:
                st.session_state.p_info = {"name": name, "phone": phone}
                st.session_state.step = 2
                st.rerun()

# --- المرحلة 2: التحليل الذكي وقائمة الأطباء ---
elif st.session_state.step == 2:
    st.markdown(f"### أهلاً بك م. {st.session_state.p_info['name']} ⛑️")
    text = st.text_area("اشرح حالتك الصحية بالتفصيل:", placeholder="أعاني من ضيق في التنفس وألم في الصدر...")
    
    if st.button("تحليل الحالة بالذكاء الاصطناعي"):
        with st.spinner("جاري التحليل..."):
            prompt = f"حلل الأعراض باختصار (سطرين): {text}. حدد الاختصاص، التشخيص المبدئي، والخطورة."
            res = model.generate_content(prompt).text
            st.session_state.diag = res
            st.session_state.spec = "قلبية" if any(x in res for x in ["قلب", "صدر", "تنفس"]) else "باطنية"
            st.session_state.ready = True

    if st.session_state.get('ready'):
        st.markdown(f'''
            <div class="diag-box">
                <b style="color:#40E0D0; font-size: 18px;">🩺 التشخيص المقترح:</b><br>
                {st.session_state.diag}
            </div>
        ''', unsafe_allow_html=True)

        if any(x in st.session_state.diag for x in ["طوارئ", "خطيرة", "مشفى", "فوري"]):
            st.error("🚨 تحذير: حالتك قد تستوجب تدخل طبي عاجل. يرجى التوجه لأقرب مستشفى.")

        st.write("### 👨‍⚕️ الأطباء المرشحون في منطقتك:")
        u_lat, u_lon = st.session_state.user_loc['lat'], st.session_state.user_loc['lon']
        matches = [d for d in DATA["أطباء"] if d['s'] == st.session_state.spec]
        
        for d in sorted(matches, key=lambda x: get_dist(u_lat, u_lon, x['lat'], x['lon'])):
            dist = get_dist(u_lat, u_lon, d['lat'], d['lon'])
            
            st.markdown(f'''
                <div class="doctor-card-ui">
                    <span class="doc-name-text">{d['n']}</span>
                    <div class="doc-info-text">اختصاص {d['s']} | عيادة {d['a']}</div>
                    <div class="doc-rating">⭐ {"★"*d['stars']} | 📍 يبعد {dist:.1f} كم عن موقعك</div>
                </div>
            ''', unsafe_allow_html=True)
            
            # عرض المواعيد أفقياً (متجاوب)
            st.write("📅 المواعيد المتاحة اليوم:")
            cols = st.columns(3)
            for i, slot in enumerate(d['slots']):
                with cols[i % 3]:
                    if st.button(f"✅ {slot}", key=f"btn-{d['n']}-{slot}"):
                        st.session_state.selected_doc, st.session_state.time, st.session_state.step = d, slot, 3
                        st.rerun()
            st.write("---")

# --- المرحلة 3: تذكرة النجاح ---
elif st.session_state.step == 3:
    st.markdown(f'''
        <div class="ticket-view">
            <h1 style="color:#40E0D0; margin-top:0;">تم تثبيت الموعد ✅</h1>
            <p style="font-size:1.2rem;">المريض: <b>{st.session_state.p_info['name']}</b></p>
            <hr style="border:0.5px dashed #333; margin: 20px 0;">
            <div style="text-align:right; display:inline-block; line-height:2.2;">
                <p>👨‍⚕️ <b>الطبيب:</b> {st.session_state.selected_doc['n']}</p>
                <p>⏰ <b>الوقت المخصص:</b> {st.session_state.time}</p>
                <p>📍 <b>العنوان:</b> بغداد - {st.session_state.selected_doc['a']}</p>
                <p>📞 <b>رقم التواصل:</b> <span style="color:#40E0D0;">{st.session_state.selected_doc['phone']}</span></p>
            </div>
            <hr style="border:0.5px dashed #333; margin: 20px 0;">
            <p style="color:#40E0D0;">نتمنى لك شفاءً عاجلاً لا يغادر سقماً 💐</p>
        </div>
    ''', unsafe_allow_html=True)
    if st.button("العودة إلى الصفحة الرئيسية"):
        st.session_state.step = 1
        st.rerun()
