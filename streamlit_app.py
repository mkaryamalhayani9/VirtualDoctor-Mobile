import streamlit as st
import math
import google.generativeai as genai

# --- 1. إعداد الذكاء الاصطناعي ---
# ضع مفتاحك هنا ليعمل التشخيص الذكي
genai.configure(api_key="ضع_مفتاح_API_الخاص_بك_هنا")
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 2. التنسيق (الثيم الأسود والفيروزي) ---
st.set_page_config(page_title="AI Doctor Baghdad", layout="centered")

st.markdown(r'''
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
* { font-family: 'Tajawal', sans-serif; direction: rtl; text-align: center; }
.stApp { background-color: #050505; color: #e0e0e0; }
.page-header { font-size: 35px; color: #40E0D0; margin-bottom: 20px; }
.diag-card { background: rgba(64, 224, 208, 0.05); border: 1px solid #40E0D0; padding: 20px; border-radius: 15px; margin-bottom: 25px; }
.doc-card { background: #0d0d0d; border: 1px solid #333; padding: 20px; border-radius: 15px; margin-bottom: 15px; text-align: right; border-right: 5px solid #40E0D0; }
.star-rating { color: #FFD700; font-size: 16px; }
.dist-text { color: #40E0D0; font-weight: bold; }
</style>
''', unsafe_allow_html=True)

# --- 3. البيانات الحقيقية للأطباء ---
DATA = {
    "أطباء": [
        {"n":"د. علي الركابي","s":"قلبية","a":"الحارثية","lat":33.3222,"lon":44.3585,"stars":5,"p":"07701234567"},
        {"n":"د. سارة الجبوري","s":"قلبية","a":"المنصور","lat":33.3251,"lon":44.3482,"stars":4,"p":"07801112223"},
        {"n":"د. ليث ثامر خزعل","s":"جملة عصبية","a":"شارع المغرب","lat":33.3550,"lon":44.3850,"stars":5,"p":"07727302343"},
        {"n":"د. طه العسكري","s":"باطنية","a":"اليرموك","lat":33.3121,"lon":44.3610,"stars":5,"p":"07832572938"},
        {"n":"د. مريم القيسي","s":"مفاصل","a":"الكرادة","lat":33.3135,"lon":44.4291,"stars":5,"p":"07901231234"}
    ]
}

def calculate_dist(lat1, lon1, lat2, lon2):
    return math.sqrt((lat1-lat2)*2 + (lon1-lon2)*2) * 111.13

if 'step' not in st.session_state:
    st.session_state.step = 1

# --- الشاشة 1: تسجيل الدخول ---
if st.session_state.step == 1:
    st.markdown('<div class="page-header">AI DR 🩺</div>', unsafe_allow_html=True)
    name = st.text_input("الأسم الكامل")
    phone = st.text_input("رقم الهاتف")
    if st.button("بدء التشخيص"):
        if name and phone:
            st.session_state.user = {"name": name, "phone": phone}
            st.session_state.step = 2
            st.rerun()

# --- الشاشة 2: التشخيص وعرض قائمة الأطباء ---
elif st.session_state.step == 2:
    st.markdown('<div class="page-header">تحليل الحالة</div>', unsafe_allow_html=True)
    text = st.text_area("📝 اشرح حالتك الصحية بالتفصيل:", placeholder="مثال: أحس بدوخة وألم خفيف بالصدر..")

    if st.button("🔍 تشخيص الآن"):
        with st.spinner("جاري التحليل بهدوء..."):
            prompt = f"حلل الحالة: '{text}'. حدد الاختصاص (قلبية، باطنية، جملة عصبية، مفاصل). أعطني النتيجة بتنسيق: الاختصاص: [الاسم]، التشخيص: [نص مطمئن للمريض يتجنب التخويف]."
            response = model.generate_content(prompt)
            res = response.text
            # تصحيح طباعة الاختصاص
            st.session_state.spec = res.split("الاختصاص:")[1].split("\n")[0].strip() if "الاختصاص:" in res else "باطنية"
            st.session_state.diag_msg = res.split("التشخيص:")[1].strip() if "التشخيص:" in res else "الحالة مستقرة، يرجى مراجعة الطبيب للتأكد."
            st.session_state.diag_ready = True

    if st.session_state.get('diag_ready'):
        st.markdown(f'<div class="diag-card"><h3>{st.session_state.diag_msg}</h3><p>الاختصاص المقترح: {st.session_state.spec}</p></div>', unsafe_allow_html=True)
        
        st.markdown("### 🏥 الأطباء المقترحون (الأقرب لك)")
        matches = [d for d in DATA["أطباء"] if d["s"] == st.session_state.spec]
        
        for doc in matches:
            dist = calculate_dist(33.3121, 44.3610, doc["lat"], doc["lon"]) # حساب البعد عن مركز بغداد
            st.markdown(f'''
            <div class="doc-card">
                <span class="dist-text" style="float:left;">{dist:.1f} كم 📍</span>
                <strong>{doc['n']}</strong><br>
                <span class="star-rating">{"⭐" * doc['stars']}</span>
            </div>
            ''', unsafe_allow_html=True)
            if st.button(f"اختيار {doc['n']}", key=doc['n']):
                st.session_state.selected_doc = doc
                st.session_state.step = 3
                st.rerun()

# --- الشاشة 3: حجز المواعيد (بنفس الثيم) ---
elif st.session_state.step == 3:
    doc = st.session_state.selected_doc
    st.markdown(f'<div class="page-header">حجز موعد: {doc["n"]}</div>', unsafe_allow_html=True)
    
    times = ["04:00 PM", "05:00 PM", "06:00 PM", "07:00 PM"]
    for t in times:
        if st.button(f"🕒 {t}", use_container_width=True):
            st.session_state.final_time = t
            st.session_state.step = 4
            st.rerun()

# --- الشاشة 4: النجاح ---
elif st.session_state.step == 4:
    st.markdown(f'''<div class="diag-card" style="border-color:#40E0D0;">
        <h2 style="color:#40E0D0;">تم الحجز بنجاح ✅</h2>
        <p>المريض: {st.session_state.user["name"]}</p>
        <p>الطبيب: {st.session_state.selected_doc["n"]}</p>
        <p>الموعد: {st.session_state.final_time}</p>
    </div>''', unsafe_allow_html=True)
    if st.button("حجز جديد"):
        st.session_state.step = 1
        st.rerun()
