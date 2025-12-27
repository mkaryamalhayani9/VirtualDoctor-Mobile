import streamlit as st
import math
import google.generativeai as genai
import requests

# --- 1. محرك الذكاء الاصطناعي الذاتي الإصلاح ---
def safe_ai_analysis(prompt_text):
    try:
        if "GEMINI_API_KEY" in st.secrets:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            # البحث عن الموديل المتاح تلقائياً لتجنب خطأ NotFound
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            if available_models:
                selected_model = genai.GenerativeModel(available_models[0])
                response = selected_model.generate_content(prompt_text)
                return response.text.replace("%", "*%*")
        return "التشخيص: يرجى استشارة الطبيب لإجراء الفحوصات السريرية."
    except Exception:
        return "نعتذر، محرك التحليل مشغول حالياً. ننصحك بمراجعة الطبيب المختص."

# --- 2. وظيفة الموقع الحية (بدون قيم ثابتة) ---
def get_live_location():
    try:
        # جلب الموقع بناءً على الـ IP الحالي للمستخدم
        response = requests.get('https://ipapi.co/json/', timeout=3).json()
        city = response.get("city", "بغداد")
        region = response.get("region", "تحديد تلقائي")
        return f"{city} - {region}"
    except:
        return "بغداد - تحديد تلقائي"

# --- 3. التنسيق الرسمي (خط تنبيه صغير + إطارات متصلة) ---
st.set_page_config(page_title="AI Doctor", layout="centered")
st.markdown(r'''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');
    * { font-family: 'Tajawal', sans-serif; direction: rtl; text-align: right; }
    .stApp { background-color: #050505; color: #e0e0e0; }
    
    .app-title { text-align: center; color: #40E0D0; font-size: 40px; font-weight: 700; margin-bottom: 5px; }
    .user-highlight { color: #40E0D0; font-size: 45px; font-weight: 700; text-align: center; display: block; margin-bottom: 30px; }
    
    .main-card { border: 2px solid #40E0D0; background: rgba(64, 224, 208, 0.02); padding: 22px; border-radius: 15px; margin-bottom: 20px; }
    
    /* تنبيه بخط صغير جداً ومرتب بناءً على طلبك */
    .small-warning { 
        border: 1.5px solid #f1c40f; 
        background: rgba(241, 196, 15, 0.03); 
        padding: 10px; 
        border-radius: 10px; 
        color: #f1c40f; 
        font-size: 11.5px; 
        margin-bottom: 20px;
        text-align: center;
    }
    
    .location-bar { border: 1px dashed #40E0D0; padding: 8px; border-radius: 10px; text-align: center; color: #40E0D0; margin-bottom: 20px; font-size: 13px; }
    [data-testid="column"] { flex: 1 !important; min-width: 85px !important; }
    .stButton button { width: 100% !important; border-radius: 8px !important; }
    
    .leaf-icon { font-size: 25px; color: #40E0D0; text-align: center; display: block; margin: 5px 0; }
    </style>
    ''', unsafe_allow_html=True)

# --- 4. قاعدة البيانات ---
DATA = {
    "أطباء": [
        {"n": "د. علي الركابي", "s": "قلبية", "a": "الحارثية", "stars": 5, "slots": ["03:00 PM", "04:30 PM", "06:00 PM"], "phone": "07701234567"},
        {"n": "د. سارة الجبوري", "s": "قلبية", "a": "المنصور", "stars": 4, "slots": ["03:30 PM", "05:00 PM", "07:30 PM"], "phone": "07801112223"}
    ]
}

if 'step' not in st.session_state: st.session_state.step = 1

# --- المرحلة 1 ---
if st.session_state.step == 1:
    st.markdown("<div class='app-title'>AI Doctor 🩺</div>", unsafe_allow_html=True)
    current_loc = get_live_location()
    st.markdown(f'<div class="location-bar">📍 موقعك المكتشف: {current_loc}</div>', unsafe_allow_html=True)
    st.markdown('<div class="small-warning">تنبيه: هذا النظام ذكاء اصطناعي للمساعدة الاستشارية فقط، ولا يعتبر بديلاً عن الفحص الطبي المباشر.</div>', unsafe_allow_html=True)
    
    name = st.text_input("الأسم الكامل")
    phone = st.text_input("رقم الهاتف")
    if st.button("دخول النظام", use_container_width=True):
        if name:
            st.session_state.p_info = {"name": name, "phone": phone}
            st.session_state.step = 2; st.rerun()

# --- المرحلة 2 ---
elif st.session_state.step == 2:
    st.markdown(f'<div style="text-align:center; color:#40E0D0; font-size:18px;">Welcome to AI Doctor ⛑️</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="user-highlight">{st.session_state.p_info["name"]}</div>', unsafe_allow_html=True)
    
    text = st.text_area("اشرح حالتك الصحية:")
    if st.button("بدء تحليل الحالة", use_container_width=True):
        with st.spinner("جاري التحليل..."):
            st.session_state.diag_res = safe_ai_analysis(f"حلل بدقة واذكر النسبة المئوية: {text}")
            st.session_state.diag_ready = True

    if st.session_state.get('diag_ready'):
        st.markdown(f'<div class="main-card"><b>التشخيص المبدئي:</b><br>{st.session_state.diag_res}</div>', unsafe_allow_html=True)
        st.write("### 👨‍⚕️ الأطباء القريبون منك:")
        for d in DATA["أطباء"]:
            st.markdown(f'<div class="main-card"><b style="color:#40E0D0; font-size:18px;">{d["n"]}</b> | {d["s"]}<br>⭐ {d["stars"]} | {d["a"]}</div>', unsafe_allow_html=True)
            cols = st.columns(len(d['slots']))
            for i, time in enumerate(d['slots']):
                with cols[i]:
                    if st.button(f"✅ {time}", key=f"{d['n']}-{time}"):
                        st.session_state.selected_doc = d; st.session_state.final_time = time; st.session_state.step = 3; st.rerun()

# --- المرحلة 3 ---
elif st.session_state.step == 3:
    st.markdown(f'''
        <div class="main-card" style="text-align:center;">
            <div class="leaf-icon">🌿</div>
            <h2 style="color:#40E0D0;">تأكيد موعد الحجز</h2>
            <div style="text-align:right; line-height:2.2;">
                <p>👤 <b>المريض:</b> {st.session_state.p_info['name']}</p>
                <p>👨‍⚕️ <b>الطبيب:</b> {st.session_state.selected_doc['n']}</p>
                <p>🕒 <b>الموعد:</b> {st.session_state.final_time}</p>
                <p>📞 <b>للتواصل:</b> <span style="color:#40E0D0; font-weight:bold;">{st.session_state.selected_doc['phone']}</span></p>
            </div>
            <div class="leaf-icon">🌿</div>
        </div>
    ''', unsafe_allow_html=True)
    if st.button("العودة للرئيسية"): st.session_state.step = 1; st.rerun()
