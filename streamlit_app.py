import streamlit as st
import math
import google.generativeai as genai
import requests

# --- 1. إعدادات الذكاء الاصطناعي ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-pro')
except Exception as e:
    st.error("❌ خطأ اتصال")

# --- 2. وظائف الموقع والمسافة ---
def detect_user_location():
    try:
        r = requests.get('https://ipapi.co/json/', timeout=5).json()
        return {"city": r.get("city", "بغداد"), "lat": r.get("latitude", 33.3152), "lon": r.get("longitude", 44.3661)}
    except:
        return {"city": "بغداد", "lat": 33.3152, "lon": 44.3661}

def get_dist(lat1, lon1, lat2, lon2):
    return math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2) * 111

# --- 3. التصميم المطور (إصلاح خربطة الأكواد) ---
st.set_page_config(page_title="AI DR", layout="centered")
st.markdown(r'''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    .stApp { direction: rtl; text-align: right; background-color: #050505; color: #e0e0e0; font-family: 'Tajawal', sans-serif; }
    
    /* مربع التشخيص - نظيف ومرتب */
    .diagnosis-card {
        background: rgba(64, 224, 208, 0.07);
        padding: 20px;
        border-radius: 15px;
        border-right: 5px solid #40E0D0;
        margin: 20px 0;
        line-height: 1.6;
    }
    .diag-header { color: #40E0D0; font-weight: bold; font-size: 18px; margin-bottom: 10px; display: block; }

    /* بطاقة الطبيب - بدون أكواد ظاهرة */
    .doctor-box {
        background: #0d0d0d;
        border: 1px solid #222;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 10px;
    }
    .doc-name { color: #40E0D0; font-size: 20px; font-weight: bold; display: block; }
    .doc-info { color: #aaa; font-size: 14px; margin: 5px 0; }
    .doc-dist { color: #FFD700; font-size: 13px; }

    /* التذكرة النهائية */
    .ticket {
        background: #111; border: 2px dashed #40E0D0; padding: 25px; border-radius: 20px;
        position: relative; text-align: center; margin: 20px 0;
    }
    .ticket::before, .ticket::after {
        content: ''; position: absolute; top: 50%; width: 24px; height: 24px;
        background: #050505; border-radius: 50%; transform: translateY(-50%);
    }
    .ticket::before { left: -14px; border-right: 2px dashed #40E0D0; }
    .ticket::after { right: -14px; border-left: 2px dashed #40E0D0; }

    .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; }
    </style>
    ''', unsafe_allow_html=True)

# --- 4. البيانات ---
DATA = {
    "أطباء": [
        {"n": "د. علي الركابي", "s": "قلبية", "a": "الحارثية", "lat": 33.3222, "lon": 44.3585, "stars": 5, "slots": ["04:00 PM", "05:00 PM", "06:00 PM"], "phone": "07701234567"},
        {"n": "د. سارة الجبوري", "s": "قلبية", "a": "المنصور", "lat": 33.3251, "lon": 44.3482, "stars": 4, "slots": ["06:00 PM", "07:30 PM"], "phone": "07801112223"},
        {"n": "د. حيدر السلطاني", "s": "باطنية", "a": "اليرموك", "lat": 33.3121, "lon": 44.3610, "stars": 5, "slots": ["03:00 PM", "04:00 PM", "05:00 PM"], "phone": "07712312312"},
        {"n": "د. طه العسكري", "s": "باطنية", "a": "حي الجامعة", "lat": 33.3330, "lon": 44.3280, "stars": 4, "slots": ["08:00 PM", "09:00 PM"], "phone": "07801212123"}
    ]
}

if 'step' not in st.session_state: st.session_state.step = 1

# --- المرحلة 1 ---
if st.session_state.step == 1:
    st.markdown("<h1 style='text-align:center; color:#40E0D0;'>AI Doctor 🩺</h1>", unsafe_allow_html=True)
    loc = detect_user_location()
    st.session_state.user_loc = loc
    st.markdown(f"<div style='text-align:center; color:#888;'>📍 موقعك المكتشف: {loc['city']}</div>", unsafe_allow_html=True)
    
    name = st.text_input("الأسم الكامل")
    phone = st.text_input("رقم الهاتف")
    if st.button("دخول النظام"):
        if name and phone:
            st.session_state.p_info = {"name": name, "phone": phone}
            st.session_state.step = 2
            st.rerun()

# --- المرحلة 2 ---
elif st.session_state.step == 2:
    st.markdown(f"### أهلاً بك {st.session_state.p_info['name']} ⛑️")
    text = st.text_area("اشرح حالتك الصحية باختصار:")
    
    if st.button("تحليل الحالة"):
        with st.spinner("جاري التحليل..."):
            prompt = f"حلل الأعراض باختصار شديد جداً (سطرين): {text}. اذكر الاختصاص والتشخيص والخطورة."
            res = model.generate_content(prompt).text
            st.session_state.diag = res
            st.session_state.spec = "قلبية" if "قلب" in res or "صدر" in res else "باطنية"
            st.session_state.ready = True

    if st.session_state.get('ready'):
        # مربع التشخيص المرتب
        st.markdown(f'''
            <div class="diagnosis-card">
                <span class="diag-header">🩺 النتيجة الطبية:</span>
                {st.session_state.diag}
            </div>
        ''', unsafe_allow_html=True)

        if any(x in st.session_state.diag for x in ["طوارئ", "خطيرة", "مشفى"]):
            st.error("🚨 حالة طارئة: يرجى التوجه لأقرب مستشفى فوراً")

        st.write("### 👨‍⚕️ الأطباء المرشحون لحالتك:")
        
        # عرض الأطباء بدون أكواد خربطة
        u_lat, u_lon = st.session_state.user_loc['lat'], st.session_state.user_loc['lon']
        matches = [d for d in DATA["أطباء"] if d['s'] == st.session_state.spec]
        
        for d in matches:
            dist = get_dist(u_lat, u_lon, d['lat'], d['lon'])
            st.markdown(f'''
                <div class="doctor-box">
                    <span class="doc-name">{d['n']}</span>
                    <div class="doc-info">اختصاص {d['s']} | الموقع: {d['a']}</div>
                    <div class="doc-dist">⭐ {"★"*d['stars']} | 📍 يبعد {dist:.1f} كم عنك</div>
                </div>
            ''', unsafe_allow_html=True)
            
            # ترتيب المواعيد أفقياً
            st.write("*المواعيد المتاحة:*")
            cols = st.columns(4) # توزيع المواعيد أفقياً
            for i, slot in enumerate(d['slots']):
                with cols[i % 4]:
                    if st.button(f"✅ {slot}", key=f"{d['n']}-{slot}"):
                        st.session_state.selected_doc = d
                        st.session_state.time = slot
                        st.session_state.step = 3
                        st.rerun()
            st.markdown("<hr style='border: 0.1px solid #222;'>", unsafe_allow_html=True)

# --- المرحلة 3: التذكرة ---
elif st.session_state.step == 3:
    st.markdown(f'''
        <div class="ticket">
            <h2 style="color:#40E0D0;">تم تأكيد الحجز ✅</h2>
            <p>المريض: <b>{st.session_state.p_info['name']}</b></p>
            <div style="border-top: 1px dashed #333; margin: 15px 0;"></div>
            <div style="text-align:right; padding: 0 20px;">
                <p>👨‍⚕️ الطبيب: {st.session_state.selected_doc['n']}</p>
                <p>⏰ الموعد: {st.session_state.time}</p>
                <p>📍 العنوان: {st.session_state.selected_doc['a']}</p>
                <p>📞 هاتف: <span style="color:#40E0D0;">{st.session_state.selected_doc['phone']}</span></p>
            </div>
            <div style="border-top: 1px dashed #333; margin: 15px 0;"></div>
            <h4 style="color:#40E0D0;">نتمنى لك السلامة التامة 💐</h4>
        </div>
    ''', unsafe_allow_html=True)
    if st.button("حجز جديد"):
        st.session_state.step = 1
        st.rerun()
