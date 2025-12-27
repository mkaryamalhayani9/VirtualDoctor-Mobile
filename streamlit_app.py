import streamlit as st
import math
import google.generativeai as genai
import requests

# --- 1. محرك الذكاء الاصطناعي (تنسيق صارم للنتائج) ---
def safe_ai_analysis(prompt_text):
    try:
        if "GEMINI_API_KEY" in st.secrets:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            if available_models:
                selected_model = genai.GenerativeModel(available_models[0])
                # طلب صريح للخط العريض والنسبة والاختصار
                refined_prompt = f"""
                أنت طبيب مساعد ذكي. حلل الحالة التالية بدقة:
                1. اسم الحالة الطبية المحتملة بين نجمتين ليكون خط عريض (مثال: *التهاب المفاصل*).
                2. اذكر نسبة الاحتمالية (مثال: 85%).
                3. شرح طبي مبسط جداً لا يتجاوز 3 أسطر فقط.
                الحالة: {prompt_text}
                """
                response = selected_model.generate_content(refined_prompt)
                return response.text
        return "التشخيص: يرجى استشارة الطبيب لإجراء الفحوصات اللازمة."
    except Exception:
        return "نعتذر، محرك التحليل مشغول حالياً."

# --- 2. وظيفة الموقع ---
def get_live_location():
    try:
        response = requests.get('https://ipapi.co/json/', timeout=3).json()
        city = response.get("city", "بغداد")
        region = response.get("region", "تحديد تلقائي")
        return f"{city} - {region}"
    except:
        return "بغداد - تحديد تلقائي"

# --- 3. التنسيق الجمالي الاحترافي ---
st.set_page_config(page_title="AI Doctor Pro", layout="centered")
st.markdown(r'''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');
    * { font-family: 'Tajawal', sans-serif; direction: rtl; text-align: right; }
    .stApp { background-color: #080808; color: #ffffff; }
    
    .app-title { text-align: center; color: #40E0D0; font-size: 38px; font-weight: 700; margin-bottom: 5px; }
    .user-highlight { color: #40E0D0; font-size: 42px; font-weight: 700; text-align: center; display: block; margin-bottom: 25px; }
    
    /* إطارات متصلة احترافية */
    .main-card { border: 1px solid rgba(64, 224, 208, 0.3); background: rgba(255, 255, 255, 0.03); padding: 20px; border-radius: 12px; margin-bottom: 15px; }
    .small-warning { border: 1px solid #f1c40f; background: rgba(241, 196, 15, 0.05); padding: 8px; border-radius: 8px; color: #f1c40f; font-size: 11px; margin-bottom: 20px; text-align: center; }
    .location-bar { border: 1px dashed #40E0D0; padding: 8px; border-radius: 10px; text-align: center; color: #40E0D0; margin-bottom: 20px; font-size: 13px; }
    
    /* تاغات الأطباء */
    .doc-tag { font-size: 11px; background: #40E0D0; color: #000; padding: 2px 10px; border-radius: 4px; font-weight: bold; margin-left: 5px; }
    
    /* الصفحة الأخيرة الاحترافية */
    .final-receipt { border: 2px solid #40E0D0; background: #111111; border-radius: 15px; overflow: hidden; }
    .receipt-header { background: #40E0D0; color: #000; padding: 20px; text-align: center; font-size: 22px; font-weight: bold; }
    .receipt-body { padding: 25px; line-height: 2.2; }
    .receipt-footer { background: #1a1a1a; padding: 15px; text-align: center; color: #888; font-size: 12px; border-top: 1px solid #333; }
    </style>
    ''', unsafe_allow_html=True)

# --- 4. قاعدة البيانات ---
DATA = {
    "أطباء": [
        {"n": "د. علي الركابي", "s": "قلبية وباطنية", "a": "الحارثية", "stars": "⭐⭐⭐⭐⭐", "dist": "1.2 كم", "slots": ["03:00 PM", "06:00 PM"], "phone": "07701234567", "rank": "الأكثر خبرة"},
        {"n": "د. سارة الجبوري", "s": "باطنية عامة", "a": "المنصور", "stars": "⭐⭐⭐⭐", "dist": "3.5 كم", "slots": ["03:30 PM", "05:00 PM"], "phone": "07801112223", "rank": "الأقرب إليك"},
        {"n": "د. مريم القيسي", "s": "مفاصل وتأهيل", "a": "الكرادة", "stars": "⭐⭐⭐⭐⭐", "dist": "5.0 كم", "slots": ["04:00 PM", "07:00 PM"], "phone": "07901231234", "rank": "استشاري"}
    ]
}

if 'step' not in st.session_state: st.session_state.step = 1

# --- المرحلة 1: الدخول ---
if st.session_state.step == 1:
    st.markdown("<div class='app-title'>AI Doctor 🩺</div>", unsafe_allow_html=True)
    current_loc = get_live_location()
    st.markdown(f'<div class="location-bar">📍 موقعك المكتشف: {current_loc}</div>', unsafe_allow_html=True)
    st.markdown('<div class="small-warning">تنبيه: هذا النظام يعتمد على الذكاء الاصطناعي للاستشارة المبدئية، ولا يغني عن زيارة الطبيب المختص.</div>', unsafe_allow_html=True)
    
    name = st.text_input("الأسم الكامل")
    phone = st.text_input("رقم الهاتف")
    if st.button("دخول النظام", use_container_width=True):
        if name and phone:
            st.session_state.p_info = {"name": name, "phone": phone}
            st.session_state.step = 2; st.rerun()

# --- المرحلة 2: التحليل والبحث عن الطبيب الأنسب ---
elif st.session_state.step == 2:
    st.markdown(f'<div style="text-align:center; color:#40E0D0; font-size:18px;">Welcome</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="user-highlight">{st.session_state.p_info["name"]}</div>', unsafe_allow_html=True)
    
    text = st.text_area("اشرح حالتك الصحية باختصار:")
    if st.button("بدء تحليل الحالة والمطابقة الذكية", use_container_width=True):
        with st.spinner("جاري تحليل بياناتك واختيار الطبيب الأنسب..."):
            st.session_state.diag_res = safe_ai_analysis(text)
            st.session_state.diag_ready = True

    if st.session_state.get('diag_ready'):
        st.markdown(f'<div class="main-card"><b>التشخيص المقترح:</b><br>{st.session_state.diag_res}</div>', unsafe_allow_html=True)
        
        st.write("### 👨‍⚕️ الأطباء المقترحون حسب حالتك وموقعك:")
        for d in DATA["أطباء"]:
            st.markdown(f'''
                <div class="main-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <b style="color:#40E0D0; font-size:19px;">{d["n"]}</b>
                        <span style="color:#f1c40f; font-size:12px;">{d["rank"]}</span>
                    </div>
                    <div style="margin-top:8px;">
                        <span class="doc-tag">{d["s"]}</span>
                        <span style="font-size:13px; color:#bbb;">{d["stars"]} | 📍 يبعد {d["dist"]}</span>
                    </div>
                </div>
            ''', unsafe_allow_html=True)
            cols = st.columns(len(d['slots']))
            for i, time in enumerate(d['slots']):
                with cols[i]:
                    if st.button(f"✅ {time}", key=f"{d['n']}-{time}"):
                        st.session_state.selected_doc = d; st.session_state.final_time = time; st.session_state.step = 3; st.rerun()

# --- المرحلة 3: صفحة النجاح (تصميم احترافي بدون أغصان) ---
elif st.session_state.step == 3:
    st.markdown(f'''
        <div class="final-receipt">
            <div class="receipt-header">تأكيد حجز الموعد</div>
            <div class="receipt-body">
                <p style="border-bottom: 1px solid #222;">👤 <b>اسم المريض:</b> {st.session_state.p_info['name']}</p>
                <p style="border-bottom: 1px solid #222;">👨‍⚕️ <b>الطبيب:</b> {st.session_state.selected_doc['n']}</p>
                <p style="border-bottom: 1px solid #222;">🛡️ <b>الاختصاص:</b> {st.session_state.selected_doc['s']}</p>
                <p style="border-bottom: 1px solid #222;">🕒 <b>الوقت المعتمد:</b> اليوم في الساعة {st.session_state.final_time}</p>
                <p style="border-bottom: 1px solid #222;">📍 <b>العنوان:</b> بغداد - {st.session_state.selected_doc['a']}</p>
                <p>📞 <b>رقم التواصل:</b> <span style="color:#40E0D0; font-weight:bold;">{st.session_state.selected_doc['phone']}</span></p>
            </div>
            <div class="receipt-footer">
                يرجى إبراز هذه الشاشة عند الدخول للعيادة لضمان الأولوية.
            </div>
        </div>
    ''', unsafe_allow_html=True)
    st.write("")
    if st.button("العودة للرئيسية", use_container_width=True): st.session_state.step = 1; st.rerun()
