import streamlit as st
import math
import google.generativeai as genai

# --- 1. إعداد الذكاء الاصطناعي (طريقة آمنة) ---
try:
    # سيقرأ المفتاح من الملف الذي أنشأته أنت في .streamlit/secrets.toml
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"خطأ في الإعداد: تأكد من ملف secrets.toml. التفاصيل: {e}")

# --- 2. التنسيق الجمالي (الثيم الأسود والفيروزي) ---
st.set_page_config(page_title="AI Doctor Baghdad", layout="centered")

st.markdown(r'''
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
* { font-family: 'Tajawal', sans-serif; direction: rtl; text-align: center; }
.stApp { background-color: #050505; color: #e0e0e0; }
.page-header { font-size: 35px; color: #40E0D0; font-weight: bold; margin-bottom: 20px; }
.diag-card { background: rgba(64, 224, 208, 0.05); border: 1px solid #40E0D0; padding: 20px; border-radius: 15px; margin-bottom: 25px; }
.doc-card { background: #0d0d0d; border: 1px solid #333; padding: 20px; border-radius: 15px; margin-bottom: 15px; text-align: right; border-right: 5px solid #40E0D0; }
.star-rating { color: #FFD700; font-size: 16px; }
.dist-text { color: #40E0D0; font-weight: bold; }
button { border-radius: 10px !important; }
</style>
''', unsafe_allow_html=True)

# --- 3. بيانات الأطباء في بغداد ---
DATA = {
    "أطباء": [
        {"n":"د. علي الركابي","s":"قلبية","a":"الحارثية","lat":33.3222,"lon":44.3585,"stars":5},
        {"n":"د. سارة الجبوري","s":"قلبية","a":"المنصور","lat":33.3251,"lon":44.3482,"stars":4},
        {"n":"د. ليث ثامر خزعل","s":"جملة عصبية","a":"شارع المغرب","lat":33.3550,"lon":44.3850,"stars":5},
        {"n":"د. طه العسكري","s":"باطنية","a":"اليرموك","lat":33.3121,"lon":44.3610,"stars":5},
        {"n":"د. مريم القيسي","s":"مفاصل","a":"الكرادة","lat":33.3135,"lon":44.4291,"stars":5}
    ]
}

def calculate_dist(lat1, lon1, lat2, lon2):
    # معادلة حساب المسافة التقريبية بالكيلومترات
    return math.sqrt((lat1-lat2)*2 + (lon1-lon2)*2) * 111.13

# إدارة التنقل بين الشاشات
if 'step' not in st.session_state:
    st.session_state.step = 1

# --- الشاشة 1: تسجيل الدخول ---
if st.session_state.step == 1:
    st.markdown('<div class="page-header">AI DR 🩺</div>', unsafe_allow_html=True)
    st.write("مرحباً بك في منصة تشخيص أطباء بغداد الذكية")
    name = st.text_input("الأسم الكامل")
    phone = st.text_input("رقم الهاتف")
    if st.button("ابدأ التشخيص"):
        if name and phone:
            st.session_state.user = {"name": name, "phone": phone}
            st.session_state.step = 2
            st.rerun()
        else:
            st.warning("يرجى إدخال البيانات المطلوبة")

# --- الشاشة 2: التشخيص وتحليل الذكاء الاصطناعي ---
elif st.session_state.step == 2:
    st.markdown('<div class="page-header">تحليل الحالة</div>', unsafe_allow_html=True)
    text = st.text_area("📝 اشرح حالتك الصحية بالتفصيل:", placeholder="مثال: أحس بصداع مستمر منذ يومين..")

    if st.button("🔍 تشخيص الآن"):
        with st.spinner("جاري التحليل بواسطة الذكاء الاصطناعي..."):
            prompt = f"حلل الحالة: '{text}'. حدد الاختصاص بدقة من (قلبية، باطنية، جملة عصبية، مفاصل). الرد بتنسيق: الاختصاص: [الاسم]، التشخيص: [نص مطمئن]."
            try:
                response = model.generate_content(prompt)
                res = response.text
                # استخراج التخصص من الرد
                st.session_state.spec = "باطنية" # الافتراضي
                for s in ["قلبية", "باطنية", "جملة عصبية", "مفاصل"]:
                    if s in res:
                        st.session_state.spec = s
                        break
                st.session_state.diag_msg = res.split("التشخيص:")[1].strip() if "التشخيص:" in res else "يرجى مراجعة الطبيب المختص."
                st.session_state.diag_ready = True
            except:
                st.error("فشل الاتصال بالذكاء الاصطناعي. تأكد من الإنترنت والمفتاح.")

    if st.session_state.get('diag_ready'):
        st.markdown(f'<div class="diag-card"><h3>{st.session_state.diag_msg}</h3><p>الاختصاص المقترح: {st.session_state.spec}</p></div>', unsafe_allow_html=True)
        
        st.markdown("### 🏥 الأطباء المقترحون في بغداد")
        matches = [d for d in DATA["أطباء"] if d["s"] == st.session_state.spec]
        
        for doc in matches:
            # افتراض موقع المريض في المنصور للتبسيط
            dist = calculate_dist(33.3250, 44.3480, doc["lat"], doc["lon"])
            st.markdown(f'''
            <div class="doc-card">
                <span class="dist-text" style="float:left;">{dist:.1f} كم 📍</span>
                <strong>{doc['n']}</strong><br>
                <span>تخصص: {doc['s']} | المنطقة: {doc['a']}</span><br>
                <span class="star-rating">{"⭐" * doc['stars']}</span>
            </div>
            ''', unsafe_allow_html=True)
            if st.button(f"حجز عند {doc['n']}", key=doc['n']):
                st.session_state.selected_doc = doc
                st.session_state.step = 3
                st.rerun()

# --- الشاشة 3: اختيار الموعد ---
elif st.session_state.step == 3:
    doc = st.session_state.selected_doc
    st.markdown(f'<div class="page-header">موعد {doc["n"]}</div>', unsafe_allow_html=True)
    st.write("اختر الوقت المناسب لك:")
    
    times = ["04:30 PM", "05:30 PM", "06:30 PM", "07:30 PM"]
    cols = st.columns(2)
    for idx, t in enumerate(times):
        if cols[idx % 2].button(f"🕒 {t}", use_container_width=True):
            st.session_state.final_time = t
            st.session_state.step = 4
            st.rerun()

# --- الشاشة 4: نجاح الحجز ---
elif st.session_state.step == 4:
    st.markdown(f'''<div class="diag-card" style="border: 2px solid #40E0D0;">
        <h2 style="color:#40E0D0;">تم الحجز بنجاح ✅</h2>
        <p>المريض: <b>{st.session_state.user["name"]}</b></p>
        <p>الطبيب: <b>{st.session_state.selected_doc["n"]}</b></p>
        <p>الموعد: <b>{st.session_state.final_time}</b></p>
        <hr>
        <p style="font-size: 12px;">سيصلك تأكيد عبر الرقم: {st.session_state.user["phone"]}</p>
    </div>''', unsafe_allow_html=True)
    if st.button("عودة للرئيسية"):
        st.session_state.step = 1
        st.session_state.diag_ready = False
        st.rerun()
