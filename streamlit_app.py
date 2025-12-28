import streamlit as st
import google.generativeai as genai
import requests

# --- 1. محرك الذكاء الاصطناعي ---
def safe_ai_analysis(prompt_text):
    try:
        if "GEMINI_API_KEY" in st.secrets:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            if available_models:
                selected_model = genai.GenerativeModel(available_models[0])
                refined_prompt = f"""
                أنت طبيب مساعد ذكي. حلل الحالة التالية بدقة:
                1. اسم الحالة الطبية المحتملة بخط عريض (Bold).
                2. اذكر نسبة الاحتمالية (نسبة مئوية).
                3. شرح طبي مبسط جداً لا يتجاوز 3 أسطر فقط.
                4. حدد الاختصاص المطلوب بكلمة واحدة فقط من بين (قلبية، باطنية، مفاصل).
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
        return f"{response.get('city', 'بغداد')} - {response.get('region', 'العراق')}"
    except: return "بغداد - تحديد تلقائي"

# --- 3. التنسيق الجمالي ---
st.set_page_config(page_title="AI Doctor Pro", layout="centered")
st.markdown(r'''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');
    * { font-family: 'Tajawal', sans-serif; direction: rtl; text-align: right; }
    .stApp { background-color: #080808; color: #ffffff; }
    .app-title { text-align: center; color: #40E0D0; font-size: 38px; font-weight: 700; margin-bottom: 5px; }
    .user-highlight { color: #40E0D0; font-size: 42px; font-weight: 700; text-align: center; display: block; margin-bottom: 25px; }
    .main-card { border: 1px solid rgba(64, 224, 208, 0.3); background: rgba(255, 255, 255, 0.03); padding: 20px; border-radius: 12px; margin-bottom: 15px; }
    .location-bar { border: 1px dashed #40E0D0; padding: 8px; border-radius: 10px; text-align: center; color: #40E0D0; margin-bottom: 20px; font-size: 13px; }
    .doc-tag { font-size: 11px; background: #40E0D0; color: #000; padding: 2px 10px; border-radius: 4px; font-weight: bold; margin-left: 5px; }
    .final-receipt { border: 2px solid #40E0D0; background: #111111; border-radius: 15px; overflow: hidden; }
    .receipt-header { background: #40E0D0; color: #000; padding: 20px; text-align: center; font-size: 22px; font-weight: bold; }
    .receipt-body { padding: 25px; line-height: 2.2; }
    </style>
    ''', unsafe_allow_html=True)

# --- 4. قاعدة البيانات (3 لكل اختصاص) ---
DATA = {
    "أطباء": [
        {"n": "د. علي الركابي", "s": "قلبية", "a": "الحارثية", "stars": "⭐⭐⭐⭐⭐", "dist": 1.2, "phone": "07701234567", "rank": "الأكثر خبرة", "slots": [("03:00 PM", True), ("04:30 PM", False), ("06:00 PM", True), ("07:30 PM", False)]},
        {"n": "د. أحمد الموسوي", "s": "قلبية", "a": "المنصور", "stars": "⭐⭐⭐⭐", "dist": 2.1, "phone": "07712223334", "rank": "استشاري قسطرة", "slots": [("03:30 PM", True), ("05:00 PM", True), ("06:30 PM", True), ("08:00 PM", False)]},
        {"n": "د. زيد كمال", "s": "قلبية", "a": "شارع المغرب", "stars": "⭐⭐⭐⭐⭐", "dist": 4.5, "phone": "07723334445", "rank": "اختصاصي دقيق", "slots": [("04:00 PM", False), ("05:30 PM", True), ("07:00 PM", False), ("08:30 PM", True)]},
        {"n": "د. سارة الجبوري", "s": "باطنية", "a": "المنصور", "stars": "⭐⭐⭐⭐", "dist": 3.5, "phone": "07801112223", "rank": "بورد عربي", "slots": [("03:30 PM", True), ("05:00 PM", True), ("06:30 PM", False), ("08:00 PM", True)]},
        {"n": "د. ليث حسين", "s": "باطنية", "a": "زيونة", "stars": "⭐⭐⭐⭐⭐", "dist": 4.2, "phone": "07810009998", "rank": "خبير هضمية", "slots": [("03:00 PM", False), ("04:30 PM", True), ("06:00 PM", True), ("07:30 PM", True)]},
        {"n": "د. نورا السعدي", "s": "باطنية", "a": "حي الجامعة", "stars": "⭐⭐⭐⭐", "dist": 1.8, "phone": "07825556667", "rank": "بورد تخصصي", "slots": [("04:00 PM", True), ("05:30 PM", False), ("07:00 PM", True), ("08:30 PM", False)]},
        {"n": "د. مريم القيسي", "s": "مفاصل", "a": "الكرادة", "stars": "⭐⭐⭐⭐⭐", "dist": 5.0, "phone": "07901231234", "rank": "استشاري", "slots": [("04:00 PM", False), ("05:30 PM", True), ("07:00 PM", True), ("08:30 PM", False)]},
        {"n": "د. حسن الهاشمي", "s": "مفاصل", "a": "الجادرية", "stars": "⭐⭐⭐⭐", "dist": 0.9, "phone": "07911112222", "rank": "تأهيل طبي", "slots": [("03:30 PM", True), ("05:00 PM", False), ("06:30 PM", True), ("08:00 PM", True)]},
        {"n": "د. ريم الوائلي", "s": "مفاصل", "a": "يرموك", "stars": "⭐⭐⭐⭐⭐", "dist": 3.2, "phone": "07928889990", "rank": "علاج طبيعي", "slots": [("03:00 PM", True), ("04:30 PM", True), ("06:00 PM", False), ("07:30 PM", True)]}
    ]
}

if 'step' not in st.session_state: st.session_state.step = 1

# --- المرحلة 1: الدخول ---
if st.session_state.step == 1:
    st.markdown("<div class='app-title'>AI Doctor 🩺</div>", unsafe_allow_html=True)
    st.markdown(f'<div class="location-bar">📍 موقعك: {get_live_location()}</div>', unsafe_allow_html=True)
    name = st.text_input("الأسم الكامل")
    phone = st.text_input("رقم الهاتف")
    if st.button("دخول النظام", use_container_width=True):
        if name and phone:
            st.session_state.p_info = {"name": name, "phone": phone}
            st.session_state.step = 2; st.rerun()

# --- المرحلة 2: التحليل والعرض ---
elif st.session_state.step == 2:
    st.markdown(f'<div class="user-highlight">{st.session_state.p_info["name"]}</div>', unsafe_allow_html=True)
    text = st.text_area("اشرح حالتك الصحية:")
    if st.button("بدء تحليل الحالة", use_container_width=True):
        with st.spinner("جاري التحليل..."):
            res = safe_ai_analysis(text)
            st.session_state.diag_res = res
            matched = [d for d in DATA["أطباء"] if d["s"] in res]
            st.session_state.filtered_docs = sorted(matched, key=lambda x: x['dist']) if matched else DATA["أطباء"]
            st.session_state.diag_ready = True

    if st.session_state.get('diag_ready'):
        st.markdown(f'<div class="main-card">{st.session_state.diag_res}</div>', unsafe_allow_html=True)
        st.write("### 👨‍⚕️ الأطباء الموصى بهم:")
        
        for index, d in enumerate(st.session_state.filtered_docs):
            # وسم التوصية للطبيب الأول فقط
            rec_tag = '<span style="background:#f1c40f; color:#000; padding:2px 8px; border-radius:4px; font-size:10px; font-weight:bold; margin-right:10px;">⭐ مرشح الذكاء الاصطناعي</span>' if index == 0 else ""
            glow = "border: 1px solid #f1c40f;" if index == 0 else ""

            st.markdown(f'''
                <div class="main-card" style="{glow}">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div><b style="color:#40E0D0; font-size:18px;">{d["n"]}</b> {rec_tag}</div>
                        <span style="color:#f1c40f; font-size:12px;">{d["rank"]}</span>
                    </div>
                    <div style="margin-top:8px; margin-bottom:10px;">
                        <span class="doc-tag">{d["s"]}</span>
                        <span style="font-size:12px; color:#bbb;">📍 {d["a"]} | 🚗 يبعد {d["dist"]} كم</span>
                    </div>
                </div>
            ''', unsafe_allow_html=True)
            
            cols = st.columns(len(d['slots']))
            for i, (time, is_available) in enumerate(d['slots']):
                with cols[i]:
                    if st.button(f"✅ {time}" if is_available else f"🔒 {time}", key=f"{d['n']}-{time}", disabled=not is_available, use_container_width=True):
                        st.session_state.selected_doc, st.session_state.final_time = d, time
                        st.session_state.step = 3; st.rerun()

# --- المرحلة 3: تأكيد الحجز ---
elif st.session_state.step == 3:
    st.markdown(f'''
        <div class="final-receipt">
            <div class="receipt-header">تأكيد حجز الموعد</div>
            <div class="receipt-body">
                <p>👤 <b>المريض:</b> {st.session_state.p_info['name']}</p>
                <p>👨‍⚕️ <b>الطبيب:</b> {st.session_state.selected_doc['n']}</p>
                <p>🕒 <b>الوقت:</b> اليوم {st.session_state.final_time}</p>
                <p>📍 <b>الموقع:</b> {st.session_state.selected_doc['a']}</p>
                <p>📞 <b>للتواصل:</b> {st.session_state.selected_doc['phone']}</p>
            </div>
        </div>
    ''', unsafe_allow_html=True)
    if st.button("العودة للرئيسية", use_container_width=True):
        st.session_state.step = 1; st.rerun()
