import streamlit as st
import math
import google.generativeai as genai

# --- 1. إعداد الذكاء الاصطناعي ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # تم تحديث اسم الموديل هنا لحل مشكلة الـ 404 الظاهرة في صورتك
        model = genai.GenerativeModel('models/gemini-1.5-flash')
    else:
        st.error("⚠️ لم يتم العثور على المفتاح في Secrets")
except Exception as e:
    st.error(f"❌ فشل الاتصال بمحرك الذكاء الاصطناعي: {e}")

# --- 2. التنسيق المتطور (نفس ألوانك ومسمياتك) ---
st.set_page_config(page_title="AI Doctor 🩺 ", layout="centered")

st.markdown(r'''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&family=Playfair+Display:wght@700&display=swap');
    * { font-family: 'Tajawal', sans-serif; direction: rtl; text-align: center; }
    .stApp { background-color: #050505; color: #e0e0e0; }
    .welcome-title { font-family: 'Playfair Display', serif; font-size: 42px; color: #40E0D0; margin-bottom: 5px; }
    .page-header { font-family: 'Playfair Display', serif; font-size: 35px; color: #40E0D0; margin-top: 20px; }
    .ai-warning { background: rgba(255, 255, 255, 0.05); border: 1px solid #444; padding: 10px; border-radius: 10px; font-size: 12px; color: #888; margin-bottom: 20px; }
    .diag-box { margin: 20px auto; max-width: 600px; padding: 25px; border-radius: 15px; background: rgba(64, 224, 208, 0.05); border: 1px solid #40E0D0; text-align: right; }
    .doc-card { background-color: #0d0d0d; padding: 20px; border-radius: 15px; border: 1px solid #333; border-bottom: 4px solid #40E0D0; margin: 15px auto; max-width: 600px; text-align: right; }
    .success-card { border: 2px solid #40E0D0; border-radius: 20px; padding: 40px; max-width:600px; margin:auto; background: rgba(64, 224, 208, 0.03); }
    .wish-safe { color: #40E0D0; font-size: 26px; font-weight: bold; margin-top: 30px; display: block; }
    .disclaimer-box { background-color: #1a1a1a; padding: 12px; border: 1px solid #444; border-right: 5px solid #ff4b4b; border-radius: 5px; margin-bottom: 20px; text-align: right; }
    </style>
    ''', unsafe_allow_html=True)

# --- 3. قاعدة البيانات ---
AREAS_COORDS = {
    "المنصور": (33.3251, 44.3482), "الحارثية": (33.3222, 44.3585), "الكرادة": (33.3135, 44.4291),
    "الجادرية": (33.2801, 44.3905), "الأعظمية": (33.3652, 44.3751), "زيونة": (33.3401, 44.4502),
    "اليرموك": (33.3000, 44.3350), "الدورة": (33.2500, 44.4000), "السيدية": (33.2650, 44.3600),
    "حي الجامعة": (33.3350, 44.3100), "الكاظمية": (33.3800, 44.3400), "الشعب": (33.4000, 44.4200)
}

DATA = {
    "أطباء": [
        {"n": "د. علي الركابي", "s": "قلبية", "a": "الحارثية", "lat": 33.3222, "lon": 44.3585, "stars": 5, "p": "07701234567"},
        {"n": "د. سارة الجبوري", "s": "قلبية", "a": "المنصور", "lat": 33.3251, "lon": 44.3482, "stars": 4, "p": "07801112223"},
        {"n": "د. ليث ثامر خزعل", "s": "جملة عصبية", "a": "المنصور", "lat": 33.3251, "lon": 44.3482, "stars": 5, "p": "07705556667"},
        {"n": "د. مريم القيسي", "s": "مفاصل", "a": "الكرادة", "lat": 33.3135, "lon": 44.4291, "stars": 5, "p": "07901231234"},
        {"n": "د. طه العسكري", "s": "باطنية", "a": "اليرموك", "lat": 33.3121, "lon": 44.3610, "stars": 5, "p": "07801212123"}
    ]
}

def calculate_dist(lat1, lon1, lat2, lon2):
    return math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2) * 111.13

if 'step' not in st.session_state: st.session_state.step = 1

# --- الصفحة 1: الدخول ---
if st.session_state.step == 1:
    st.markdown('<div class="welcome-title">Welcome to AI Doctor 🩺</div>', unsafe_allow_html=True)
    st.markdown('<div class="ai-warning">⚠️ تنبيه: هذا النظام يعمل بالذكاء الاصطناعي للمساعدة في التشخيص.</div>', unsafe_allow_html=True)
    name = st.text_input("الأسم الكامل")
    u_area = st.selectbox("اختر منطقتك الحالية في بغداد:", sorted(list(AREAS_COORDS.keys())))
    phone = st.text_input("رقم الهاتف")
    if st.button("دخول النظام"):
        if name and phone:
            st.session_state.p_data = {"name": name, "area": u_area, "phone": phone}
            st.session_state.u_coords = AREAS_COORDS[u_area]
            st.session_state.step = 2
            st.rerun()

# --- الصفحة 2: AI DR ---
elif st.session_state.step == 2:
    st.markdown('<div class="page-header">AI DR.⛑️</div>', unsafe_allow_html=True)
    st.markdown('<div class="disclaimer-box"><strong style="color: #ff4b4b;">⚠️ إخلاء مسؤولية:</strong> هذا النظام استرشادي.</div>', unsafe_allow_html=True)

    text = st.text_area("📝 اشرح حالتك الصحية:", placeholder="مثال: عندي ألم بالصدر...")

    if st.button("🔍 تحليل الحالة الآن"):
        with st.spinner("جاري التواصل مع الذكاء الاصطناعي..."):
            prompt = f"حلل: '{text}'. حدد الاختصاص (قلبية، باطنية، جملة عصبية، مفاصل). الرد بصيغة: الاختصاص: [الاسم]، التشخيص: [نص مطمئن]."
            try:
                response = model.generate_content(prompt)
                res = response.text
                st.session_state.spec = "باطنية"
                for s in ["قلبية", "باطنية", "جملة عصبية", "مفاصل"]:
                    if s in res: 
                        st.session_state.spec = s
                        break
                st.session_state.diag_msg = res.split("التشخيص:")[1].strip() if "التشخيص:" in res else res
                st.session_state.diag_ready = True
            except Exception as e:
                st.error(f"حدث خطأ في التحليل: {e}")
    
    if st.session_state.get('diag_ready'):
        st.markdown(f'''<div class="diag-box">
            <h4 style="color: #40E0D0;">🔍 نتيجة التحليل:</h4>
            <p>{st.session_state.diag_msg}</p>
            <p>الاختصاص المقترح: <b>{st.session_state.spec}</b></p>
        </div>''', unsafe_allow_html=True)

        u_lat, u_lon = st.session_state.u_coords
        matches = [d for d in DATA["أطباء"] if d['s'] == st.session_state.spec]
        for d in matches:
            dist = calculate_dist(u_lat, u_lon, d['lat'], d['lon'])
            st.markdown(f'''<div class="doc-card">
                <span style="color:#40E0D0; float:left; font-weight:bold;">{dist:.1f} كم 📍</span>
                <span style="font-size:20px; color:#40E0D0;"><b>{d['n']}</b></span><br>
                <span>المنطقة: {d['a']}</span>
            </div>''', unsafe_allow_html=True)
            if st.button(f"حجز عند {d['n']}", key=d['n']):
                st.session_state.selected_doc = d
                st.session_state.step = 3
                st.rerun()

# --- بقية الصفحات كما هي ---
elif st.session_state.step == 3:
    st.info(f"تأكيد الحجز عند {st.session_state.selected_doc['n']}")
    if st.button("تأكيد نهائي"):
        st.session_state.step = 4
        st.rerun()

elif st.session_state.step == 4:
    st.balloons()
    st.markdown('<div class="success-card"><h1>تم تأكيد الحجز ✅</h1></div>', unsafe_allow_html=True)
    if st.button("العودة للرئيسية"):
        st.session_state.step = 1
        st.rerun()
