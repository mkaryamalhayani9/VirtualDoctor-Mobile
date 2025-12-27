import streamlit as st
import math
import google.generativeai as genai
import requests

# --- 1. محرك الذكاء الاصطناعي (تشخيص دقيق وسطرين شرح) ---
def safe_ai_analysis(prompt_text):
    try:
        if "GEMINI_API_KEY" in st.secrets:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            if available_models:
                selected_model = genai.GenerativeModel(available_models[0])
                # تعليمات صارمة للذكاء بالالتزام بالسطرين والبولد
                full_prompt = f"حلل الحالة التالية: '{prompt_text}'. المطلوب: اذكر التشخيص والنسبة المئوية بشكل عريض *Bold*، ثم اكتب شرحاً طبياً مختصراً سطرين فقط لا أكثر."
                response = selected_model.generate_content(full_prompt)
                return response.text.replace("%", "*%*")
        return "التشخيص: يرجى استشارة الطبيب لإجراء الفحوصات اللازمة."
    except Exception:
        return "المحرك مشغول، يرجى مراجعة الطبيب المختص بناءً على الأعراض."

# --- 2. وظيفة الموقع ---
def get_live_location():
    try:
        response = requests.get('https://ipapi.co/json/', timeout=3).json()
        return {
            "city": response.get("city", "بغداد"),
            "region": response.get("region", "تحديد تلقائي"),
            "lat": response.get("latitude", 33.3152),
            "lon": response.get("longitude", 44.3661)
        }
    except:
        return {"city": "بغداد", "region": "تحديد تلقائي", "lat": 33.3152, "lon": 44.3661}

def calculate_dist(lat1, lon1, lat2, lon2):
    return math.sqrt((lat1 - lat2)*2 + (lon1 - lon2)*2) * 111.13

# --- 3. التصميم (رسمي للكبار) ---
st.set_page_config(page_title="AI Doctor", layout="centered")
st.markdown(r'''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');
    * { font-family: 'Tajawal', sans-serif; direction: rtl; text-align: right; }
    .stApp { background-color: #050505; color: #e0e0e0; }
    
    .app-title { text-align: center; color: #40E0D0; font-size: 40px; font-weight: 700; }
    .user-highlight { color: #40E0D0; font-size: 45px; font-weight: 700; text-align: center; display: block; margin-bottom: 25px; }
    
    .main-card { border: 2px solid #40E0D0; background: rgba(64, 224, 208, 0.02); padding: 22px; border-radius: 15px; margin-bottom: 20px; }
    
    .small-warning { 
        border: 1.5px solid #f1c40f; background: rgba(241, 196, 15, 0.03); 
        padding: 8px; border-radius: 10px; color: #f1c40f; font-size: 11px; text-align: center; margin-bottom: 20px;
    }
    
    .dist-tag { color: #40E0D0; font-size: 13px; font-weight: bold; }
    .leaf-icon { font-size: 28px; color: #40E0D0; text-align: center; display: block; margin: 10px 0; }
    [data-testid="column"] { flex: 1 !important; min-width: 85px !important; }
    .stButton button { width: 100% !important; border-radius: 8px !important; }
    </style>
    ''', unsafe_allow_html=True)

# --- 4. قاعدة البيانات ---
DATA = {
    "أطباء": [
        {"n": "د. علي الركابي", "s": "قلبية", "a": "الحارثية", "lat": 33.3222, "lon": 44.3585, "stars": 5, "slots": {"03:00 PM": True, "04:30 PM": False, "06:00 PM": True}, "phone": "07701234567"},
        {"n": "د. سارة الجبوري", "s": "قلبية", "a": "المنصور", "lat": 33.3251, "lon": 44.3482, "stars": 4, "slots": {"03:30 PM": True, "05:00 PM": True, "06:30 PM": False}, "phone": "07801112223"},
        {"n": "د. مريم القيسي", "s": "مفاصل", "a": "الكرادة", "lat": 33.3135, "lon": 44.4291, "stars": 5, "slots": {"04:00 PM": True, "05:30 PM": True, "07:00 PM": False}, "phone": "07901231234"}
    ]
}

if 'step' not in st.session_state: st.session_state.step = 1

# --- المرحلة 1 ---
if st.session_state.step == 1:
    st.markdown("<div class='app-title'>AI Doctor 🩺</div>", unsafe_allow_html=True)
    loc_data = get_live_location()
    st.session_state.user_loc = loc_data
    st.markdown(f'<div style="text-align:center; color:#40E0D0; font-size:13px; margin-bottom:15px;">📍 موقعك الحالي: {loc_data["city"]} - {loc_data["region"]}</div>', unsafe_allow_html=True)
    st.markdown('<div class="small-warning">تنبيه: هذا النظام للاستشارة المبدئية الذكية فقط ولا يغني عن الفحص السريري.</div>', unsafe_allow_html=True)
    
    name = st.text_input("الأسم الكامل")
    phone = st.text_input("رقم الهاتف")
    if st.button("دخول النظام"):
        if name and phone:
            st.session_state.p_info = {"name": name, "phone": phone}
            st.session_state.step = 2; st.rerun()

# --- المرحلة 2 ---
elif st.session_state.step == 2:
    st.markdown(f'<div class="user-highlight">{st.session_state.p_info["name"]}</div>', unsafe_allow_html=True)
    text = st.text_area("اشرح حالتك الصحية:")

    if st.button("تحليل الحالة واختيار الطبيب الأنسب", use_container_width=True):
        with st.spinner("جاري التحليل..."):
            u = st.session_state.user_loc
            spec = "قلبية" if any(w in text for w in ["قلب", "صدر", "نفس"]) else "مفاصل" if "مفصل" in text else "باطنية"
            
            # منطق اختيار الطبيب الأنسب (المسافة + التقييم + الموعد)
            matches = []
            for d in DATA["أطباء"]:
                d['dist'] = calculate_dist(u['lat'], u['lon'], d['lat'], d['lon'])
                if d['s'] == spec: matches.append(d)
            
            best_doc = sorted(matches or DATA["أطباء"], key=lambda x: (x['dist'], -x['stars']))[0]
            st.session_state.diag_res = safe_ai_analysis(text)
            st.session_state.rec = f"💡 *توصية النظام:* بناءً على موقعك وخبرة الطبيب، ننصح بحجز موعد عند <span style='color:#40E0D0;'>{best_doc['n']}</span>."
            st.session_state.diag_ready = True

    if st.session_state.get('diag_ready'):
        st.markdown(f'<div class="main-card"><b>التشخيص المتوقع:</b><br>{st.session_state.diag_res}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="main-card" style="border-right: 10px solid #40E0D0;">{st.session_state.rec}</div>', unsafe_allow_html=True)
        
        st.write("### قائمة الأطباء المتاحين حسب موقعك:")
        for d in DATA["أطباء"]:
            st.markdown(f'''
                <div class="main-card">
                    <b style="color:#40E0D0; font-size:18px;">{d['n']}</b> | {d['s']}<br>
                    <span class="dist-tag">📍 يبعد عنك {d['dist']:.1f} كم</span> | {"⭐" * d['stars']}
                </div>
            ''', unsafe_allow_html=True)
            cols = st.columns(len(d['slots']))
            for i, (time, open) in enumerate(d['slots'].items()):
                with cols[i]:
                    if st.button(f"✅ {time}", key=f"{d['n']}-{time}", disabled=not open):
                        st.session_state.selected_doc = d; st.session_state.final_time = time; st.session_state.step = 3; st.rerun()

# --- المرحلة 3 ---
elif st.session_state.step == 3:
    st.markdown(f'''
        <div class="main-card" style="text-align:center;">
            <div class="leaf-icon">🌿</div>
            <h2 style="color:#40E0D0; margin-bottom:20px;">تأكيد تفاصيل الموعد</h2>
            <div style="text-align:right; line-height:2.4; font-size:16px;">
                <p>👤 <b>المريض:</b> {st.session_state.p_info['name']}</p>
                <p>👨‍⚕️ <b>الطبيب:</b> {st.session_state.selected_doc['n']}</p>
                <p>🕒 <b>الوقت:</b> اليوم {st.session_state.final_time}</p>
                <p>📍 <b>العنوان:</b> {st.session_state.selected_doc['a']} (يبعد {st.session_state.selected_doc['dist']:.1f} كم)</p>
                <p>📞 <b>رقم العيادة:</b> <span style="color:#40E0D0;">{st.session_state.selected_doc['phone']}</span></p>
            </div>
            <div class="leaf-icon">🌿</div>
            <p style="color:#888; font-size:13px;">يرجى الحضور قبل الموعد بـ 10 دقائق.</p>
        </div>
    ''', unsafe_allow_html=True)
    if st.button("إغلاق والعودة"): st.session_state.step = 1; st.rerun()
