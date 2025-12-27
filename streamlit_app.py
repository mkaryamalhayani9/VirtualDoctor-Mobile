import streamlit as st
import math
import google.generativeai as genai
import requests

# --- 1. إعدادات الذكاء الاصطناعي (حسب طلبك: نظام الجلسة بدون تسجيل) ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # حل مشكلة الـ 404 باختيار الموديل المتوفر تلقائياً
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        model = genai.GenerativeModel(models[0])
    else:
        st.error("⚠️ مفتاح API غير متوفر")
except Exception as e:
    st.error(f"❌ خطأ اتصال: {e}")

# --- 2. التنسيق الأنيق (ألوانك الأساسية مع تحسين صفحة النجاح) ---
st.set_page_config(page_title="AI Doctor Baghdad", layout="centered")
st.markdown(r'''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    * { font-family: 'Tajawal', sans-serif; direction: rtl; }
    .stApp { background-color: #050505; color: #e0e0e0; }
    .doc-card { background: #0d0d0d; padding: 20px; border-radius: 15px; border: 1px solid #333; margin-bottom: 15px; position: relative; text-align: right; }
    .recommend-badge { position: absolute; top: 10px; left: 10px; background: #40E0D0; color: black; padding: 2px 10px; border-radius: 20px; font-size: 11px; font-weight: bold; }
    .star-color { color: #FFD700; }
    .success-box { border: 2px solid #40E0D0; padding: 40px; border-radius: 25px; background: rgba(64, 224, 208, 0.05); text-align: center; line-height: 1.8; }
    </style>
    ''', unsafe_allow_html=True)

# --- 3. وظائف الموقع والمسافة ---
def get_auto_location():
    try:
        # جلب الموقع تلقائياً عبر IP بدون تدخل المريض
        res = requests.get('https://ipapi.co/json/', timeout=5).json()
        return {"city": res.get("city", "بغداد"), "region": res.get("region", "اليرموك"), "lat": res.get("latitude", 33.3152), "lon": res.get("longitude", 44.3661)}
    except:
        return {"city": "بغداد", "region": "بغداد", "lat": 33.3152, "lon": 44.3661}

def calculate_dist(lat1, lon1, lat2, lon2):
    return math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2) * 111.13

# --- 4. قاعدة بيانات الأطباء (مواعيد متاحة ومقفولة) ---
DATA = {
    "أطباء": [
        {"n": "د. علي الركابي", "s": "قلبية", "a": "الحارثية", "lat": 33.3222, "lon": 44.3585, "stars": 5, "slots": {"04:00 PM": True, "05:00 PM": False}, "phone": "07701234567"},
        {"n": "د. سارة الجبوري", "s": "قلبية", "a": "المنصور", "lat": 33.3251, "lon": 44.3482, "stars": 4, "slots": {"06:00 PM": True, "07:30 PM": True}, "phone": "07801112223"},
        {"n": "د. ليث ثامر خزعل", "s": "جملة عصبية", "a": "المنصور", "lat": 33.3251, "lon": 44.3482, "stars": 5, "slots": {"04:30 PM": False, "08:15 PM": True}, "phone": "07705556667"},
        {"n": "د. مريم القيسي", "s": "مفاصل", "a": "الكرادة", "lat": 33.3135, "lon": 44.4291, "stars": 5, "slots": {"05:00 PM": True}, "phone": "07901231234"},
        {"n": "د. طه العسكري", "s": "باطنية", "a": "اليرموك", "lat": 33.3121, "lon": 44.3610, "stars": 3, "slots": {"09:00 PM": True}, "phone": "07801212123"}
    ]
}

if 'step' not in st.session_state: st.session_state.step = 1

# --- المرحلة 1: صفحة الدخول (إضافة العمر والهاتف) ---
if st.session_state.step == 1:
    st.markdown("<h1 style='text-align:center; color:#40E0D0;'>AI Doctor 🩺</h1>", unsafe_allow_html=True)
    name = st.text_input("الأسم الكامل")
    phone = st.text_input("رقم الهاتف")
    age = st.number_input("العمر", min_value=1, max_value=120, value=25)
    
    if st.button("دخول النظام"):
        if name and phone:
            with st.spinner("جاري تحديد موقعك..."):
                loc = get_auto_location()
                st.session_state.p_info = {"name": name, "phone": phone, "age": age, "area": loc['region'], "city": loc['city']}
                st.session_state.u_coords = (loc['lat'], loc['lon'])
                st.session_state.step = 2
                st.rerun()
        else:
            st.error("يرجى ملء كافة الحقول")

# --- المرحلة 2: التحليل الذكي (سطرين + نسب + موقع) ---
elif st.session_state.step == 2:
    st.markdown(f"I DR ⛑️<h3>مرحباً بك، {st.session_state.p_info['name']}</h3>", unsafe_allow_html=True)
    text = st.text_area("اشرح حالتك الصحية باختصار:")

    if st.button("تحليل الحالة"):
        with st.spinner("جاري التشخيص..."):
            # توجيه الذكاء للالتزام بالسطرين والنسب والموقع
            prompt = (
                f"حلل في سطرين فقط: '{text}'. المريض في {st.session_state.p_info['city']}/{st.session_state.p_info['area']}. "
                f"اذكر الاختصاص بالنسب المئوية، التشخيص، وتأكيد المحافظة والمنطقة."
            )
            response = model.generate_content(prompt)
            st.session_state.diag_res = response.text
            
            # استخراج الاختصاص للفلترة
            st.session_state.spec = "باطنية"
            for s in ["قلبية", "باطنية", "جملة عصبية", "مفاصل"]:
                if s in response.text: st.session_state.spec = s; break
            st.session_state.diag_ready = True

    if st.session_state.get('diag_ready'):
        st.info(f"📊 {st.session_state.diag_res}")
        
        # ترتيب حسب الأقرب للموقع المكتشف
        u_lat, u_lon = st.session_state.u_coords
        matches = [d for d in DATA["أطباء"] if d['s'] == st.session_state.spec]
        for d in matches: d['d_km'] = calculate_dist(u_lat, u_lon, d['lat'], d['lon'])
        sorted_docs = sorted(matches, key=lambda x: x['d_km'])

        st.write("### الأطباء الأقرب لموقعك المكتشف:")
        for idx, d in enumerate(sorted_docs):
            is_best = "⭐ المرشح الأقرب" if idx == 0 else ""
            st.markdown(f'''
                <div class="doc-card">
                    <span class="recommend-badge">{is_best}</span>
                    <b style="font-size:19px; color:#40E0D0;">{d['n']}</b><br>
                    <small>اختصاص {d['s']} | {d['a']}</small><br>
                    <span class="star-color">{"★" * d['stars']}</span> | يبعد {d['d_km']:.1f} كم 📍
                </div>
            ''', unsafe_allow_html=True)
            
            cols = st.columns(len(d['slots']))
            for i, (slot, is_open) in enumerate(d['slots'].items()):
                if is_open:
                    if cols[i].button(f"✅ {slot}", key=f"b-{d['n']}-{slot}"):
                        st.session_state.selected_doc = d
                        st.session_state.final_time = slot
                        st.session_state.step = 3
                        st.rerun()
                else:
                    cols[i].button(f"🔒 {slot}", key=f"l-{d['n']}-{slot}", disabled=True)

# --- المرحلة 3: صفحة النجاح (أنيقة وشاملة) ---
elif st.session_state.step == 3:
    st.balloons()
    st.markdown(f'''
        <div class="success-box">
            <h1 style="color:#40E0D0;">تم الحجز بنجاح ✅</h1>
            <p style="font-size:18px;">المريض: <b>{st.session_state.p_info['name']}</b> ({st.session_state.p_info['age']} سنة)</p>
            <hr style="border:0.5px solid #333;">
            <div style="text-align:right; display:inline-block;">
                <p>👨‍⚕️ <b>الدكتور:</b> {st.session_state.selected_doc['n']}</p>
                <p>🩺 <b>الاختصاص:</b> {st.session_state.selected_doc['s']}</p>
                <p>⏰ <b>الموعد:</b> {st.session_state.final_time}</p>
                <p>📍 <b>العنوان:</b> {st.session_state.selected_doc['a']}</p>
                <p>📞 <b>رقم العيادة:</b> <span style="color:#40E0D0;">{st.session_state.selected_doc['phone']}</span></p>
            </div>
            <br><br>
            <h3 style="color:#40E0D0;">تمنياتنا لكم بالشفاء العاجل 💐</h3>
        </div>
    ''', unsafe_allow_html=True)
    if st.button("بدء جلسة جديدة"):
        st.session_state.step = 1
        st.rerun()
