import streamlit as st
import math
import google.generativeai as genai
import requests

# --- 1. إعدادات الصفحة والذكاء الاصطناعي ---
st.set_page_config(page_title="AI DR Baghdad", layout="centered")

try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("خطأ في تهيئة الذكاء الاصطناعي")

# --- 2. وظائف الموقع والمسافة ---
def detect_user_location():
    try:
        # محاولة جلب الموقع عبر الـ IP
        response = requests.get('https://ipapi.co/json/', timeout=5).json()
        return {
            "city": response.get("city", "بغداد"),
            "region": response.get("region", "اليرموك"),
            "lat": response.get("latitude", 33.3152),
            "lon": response.get("longitude", 44.3661)
        }
    except:
        return {"city": "بغداد", "region": "اليرموك", "lat": 33.3152, "lon": 44.3661}

def calculate_dist(lat1, lon1, lat2, lon2):
    return math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2) * 111.13

# --- 3. التنسيق CSS الاحترافي (RTL + UI/UX) ---
st.markdown(r'''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;500;700;900&display=swap');
    
    * { font-family: 'Tajawal', sans-serif; }
    .stApp { background-color: #050505; color: #FFFFFF; direction: rtl; }
    
    /* العناصر العلوية */
    .main-title { font-size: 52px; font-weight: 900; text-align: center; color: #40E0D0; margin-top: 20px; }
    .sub-title { font-size: 18px; text-align: center; color: #888; margin-bottom: 20px; }
    
    .location-box { 
        background: rgba(64, 224, 208, 0.1); 
        padding: 15px; 
        border-radius: 15px; 
        border: 1px solid #40E0D0; 
        text-align: center; 
        color: #40E0D0;
        font-weight: bold;
        margin-bottom: 10px;
    }
    
    .disclaimer-box {
        font-size: 13px;
        color: #FFD700;
        text-align: center;
        background: rgba(255, 215, 0, 0.05);
        padding: 10px;
        border-radius: 10px;
        border: 1px dashed #FFD700;
        margin-bottom: 30px;
    }

    /* بطاقة الطبيب */
    .doc-card {
        background: #111;
        border-right: 5px solid #40E0D0;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 15px;
    }
    .doc-name { font-size: 24px; font-weight: 700; color: #40E0D0; }
    .doc-spec { font-size: 16px; color: #FFD700; margin-bottom: 5px; }
    .stars { color: #FFD700; margin-bottom: 10px; }
    
    /* المدخلات */
    input, textarea { text-align: right !important; direction: rtl !important; }
    </style>
''', unsafe_allow_html=True)

# --- 4. قاعدة البيانات ---
DATA = {
    "أطباء": [
        {"n": "د. علي الركابي", "s": "قلبية", "a": "الحارثية", "lat": 33.3222, "lon": 44.3585, "stars": 5, "slots": {"04:00 PM": True, "05:00 PM": False, "06:00 PM": True}, "phone": "07701234567"},
        {"n": "د. سارة الجبوري", "s": "قلبية", "a": "المنصور", "lat": 33.3251, "lon": 44.3482, "stars": 4, "slots": {"06:00 PM": True, "07:30 PM": True}, "phone": "07801112223"},
        {"n": "د. حيدر السلطاني", "s": "باطنية", "a": "اليرموك", "lat": 33.3121, "lon": 44.3610, "stars": 5, "slots": {"03:00 PM": True, "04:00 PM": True}, "phone": "07712312312"},
        {"n": "د. مريم القيسي", "s": "مفاصل", "a": "الكرادة", "lat": 33.3135, "lon": 44.4291, "stars": 5, "slots": {"05:00 PM": True, "06:00 PM": True}, "phone": "07901231234"}
    ]
}

if 'step' not in st.session_state: st.session_state.step = 1

# --- المرحلة 1: الدخول (الموقع + إخلاء المسؤولية) ---
if st.session_state.step == 1:
    st.markdown('<div class="main-title">AI DR ⛑️</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">نظام بغداد الذكي لحجز الأطباء</div>', unsafe_allow_html=True)
    
    # تحديد الموقع وعرضه فوراً
    u_loc = detect_user_location()
    st.session_state.u_loc = u_loc
    st.markdown(f'<div class="location-box">📍 موقعك المكتشف: {u_loc["city"]} - {u_loc["region"]}</div>', unsafe_allow_html=True)
    
    # إخلاء المسؤولية
    st.markdown('<div class="disclaimer-box">⚠️ إخلاء مسؤولية: هذا النظام استشاري مدعوم بالذكاء الاصطناعي. لا يعتبر بديلاً عن التشخيص الطبي المهني. في الحالات الطارئة، يرجى الاتصال بالإسعاف فوراً.</div>', unsafe_allow_html=True)

    with st.container():
        name = st.text_input("الأسم الكامل")
        phone = st.text_input("رقم الهاتف")
        if st.button("دخول النظام"):
            if name and phone:
                st.session_state.p_info = {"name": name, "phone": phone}
                st.session_state.step = 2
                st.rerun()

# --- المرحلة 2: التشخيص وعرض الأطباء المتاحين ---
elif st.session_state.step == 2:
    st.markdown(f'<h3 style="text-align:center;">مرحباً بك {st.session_state.p_info["name"]}</h3>', unsafe_allow_html=True)
    desc = st.text_area("صف لي حالتك الصحية بوضوح:")

    if st.button("بدء التحليل"):
        with st.spinner("جاري تحليل الأعراض..."):
            prompt = f"حلل الأعراض: {desc}. أعطني التشخيص والاختصاص (قلبية، باطنية، مفاصل) وهل الحالة طارئة؟"
            response = model.generate_content(prompt)
            st.session_state.diag_res = response.text
            
            # استخراج الاختصاص
            st.session_state.spec = "باطنية"
            for s in ["قلبية", "باطنية", "مفاصل"]:
                if s in response.text: st.session_state.spec = s; break
            st.session_state.diag_ready = True

    if st.session_state.get('diag_ready'):
        st.success(st.session_state.diag_res)
        
        # ترتيب الأطباء حسب الأقرب
        u_lat, u_lon = st.session_state.u_loc['lat'], st.session_state.u_loc['lon']
        matches = [d for d in DATA["أطباء"] if d['s'] == st.session_state.spec]
        for d in matches: d['dist'] = calculate_dist(u_lat, u_lon, d['lat'], d['lon'])
        sorted_docs = sorted(matches, key=lambda x: x['dist'])

        st.write("---")
        st.subheader("👨‍⚕️ الأطباء المتاحون حسب حالتك وموقعك:")

        for d in sorted_docs:
            st.markdown(f'''
                <div class="doc-card">
                    <div class="doc-name">{d['n']}</div>
                    <div class="doc-spec">اختصاص {d['s']}</div>
                    <div class="stars">{"★" * d['stars']} (تقييم ممتاز)</div>
                    <div style="font-size:14px; color:#aaa;">📍 {d['a']} | 📏 يبعد عنك {d['dist']:.1f} كم</div>
                </div>
            ''', unsafe_allow_html=True)
            
            # المواعيد أفقية
            st.write("أوقات الحجز المتاحة:")
            cols = st.columns(len(d['slots']))
            for i, (slot, is_open) in enumerate(d['slots'].items()):
                with cols[i]:
                    if is_open:
                        if st.button(f"✅ {slot}", key=f"{d['n']}-{slot}"):
                            st.session_state.final = {"doc": d, "time": slot}
                            st.session_state.step = 3
                            st.rerun()
                    else:
                        st.button(f"🔒 محجوز", key=f"{d['n']}-{slot}", disabled=True)

# --- المرحلة 3: صفحة النجاح ---
elif st.session_state.step == 3:
    st.markdown(f'''
        <div style="border: 2px solid #40E0D0; padding: 40px; border-radius: 30px; background: rgba(64, 224, 208, 0.05); text-align: center;">
            <h1 style="color:#40E0D0; font-size:45px;">تم الحجز بنجاح ✅</h1>
            <p style="font-size:20px;">المريض: <b>{st.session_state.p_info['name']}</b></p>
            <div style="text-align:right; display:inline-block; border-top: 1px solid #333; margin-top:20px; padding-top:20px;">
                <p>👨‍⚕️ <b>الطبيب المختص:</b> {st.session_state.final['doc']['n']}</p>
                <p>⏰ <b>وقت الموعد:</b> {st.session_state.final['time']}</p>
                <p>📍 <b>العنوان:</b> {st.session_state.final['doc']['a']}</p>
                <p>📞 <b>رقم العيادة:</b> {st.session_state.final['doc']['phone']}</p>
            </div>
            <br><br>
            <h2 style="color:#40E0D0; font-weight:900;">مع تمنياتنا لك بالشفاء العاجل 💐</h2>
        </div>
    ''', unsafe_allow_html=True)
    
    if st.button("عودة للرئيسية"):
        st.session_state.step = 1
        st.rerun()
