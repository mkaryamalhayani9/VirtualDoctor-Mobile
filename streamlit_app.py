import streamlit as st
import math
import google.generativeai as genai
import requests

# ---------------- 1. إعدادات الذكاء الاصطناعي (مدققة) ----------------
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # استخدام موديل فلاش لضمان السرعة وعدم حدوث خطأ NotFound
        model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("❌ خطأ اتصال بالذكاء الاصطناعي")

# ---------------- 2. وظيفة الموقع ----------------
def detect_user_location_by_ip():
    try:
        r = requests.get("https://ipapi.co/json/", timeout=5).json()
        return {
            "city": r.get("city", "بغداد"),
            "region": r.get("region", "العراق"),
            "lat": r.get("latitude", 33.3152),
            "lon": r.get("longitude", 44.3661)
        }
    except:
        return {"city": "بغداد", "region": "اليرموك", "lat": 33.3152, "lon": 44.3661}

def calculate_dist(lat1, lon1, lat2, lon2):
    return math.sqrt((lat1-lat2)**2 + (lon1-lon2)**2) * 111.13

# ---------------- 3. التصميم (ثيم احترافي متناسق) ----------------
st.set_page_config(page_title="AI DR Baghdad", layout="centered")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
.main, .stApp { direction:rtl; background:#050505; color:#e0e0e0; font-family:'Tajawal', sans-serif; }

/* بطاقات الأطباء */
.doc-card {
    background:#0d0d0d; padding:20px; border-radius:15px; border:1px solid #333; margin-bottom:15px;
}

/* الأوسمة */
.recommend-badge {
    background:#40E0D0; color:#000; padding:3px 12px; border-radius:20px; font-size:11px; font-weight:bold; display:inline-block; margin-bottom:8px;
}

/* النجوم والتحذيرات */
.star { color:#FFD700; font-size:15px; }
.legal-disclaimer { font-size:12px; color:#888; text-align:center; margin:20px 0; }

/* تذكرة النجاح */
.success-panel {
    border:2px dashed #40E0D0; padding:35px; border-radius:25px; background:rgba(64,224,208,.05); text-align:center;
}
.stButton>button { width: 100%; border-radius: 10px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ---------------- 4. البيانات ----------------
DATA = {
    "أطباء": [
        {"n": "د. علي الركابي", "s": "قلبية", "a": "الحارثية", "lat": 33.3222, "lon": 44.3585, "stars": 5, "slots": {"03:00 PM": True, "04:00 PM": False, "05:00 PM": True}, "phone": "07701234567"},
        {"n": "د. سارة الجبوري", "s": "قلبية", "a": "المنصور", "lat": 33.3251, "lon": 44.3482, "stars": 4, "slots": {"04:00 PM": True, "06:00 PM": True}, "phone": "07801112223"},
        {"n": "د. حيدر السلطاني", "s": "باطنية", "a": "اليرموك", "lat": 33.3121, "lon": 44.3610, "stars": 5, "slots": {"03:00 PM": True, "04:00 PM": False}, "phone": "07712312312"},
        {"n": "د. مريم القيسي", "s": "مفاصل", "a": "الكرادة", "lat": 33.3135, "lon": 44.4291, "stars": 5, "slots": {"05:00 PM": True}, "phone": "07901231234"},
    ]
}

if "step" not in st.session_state: st.session_state.step = 1

# ================= المرحلة 1 =================
if st.session_state.step == 1:
    st.markdown("<h1 style='text-align:center;color:#40E0D0'>AI DR ⛑️</h1>", unsafe_allow_html=True)
    loc = detect_user_location_by_ip()
    st.session_state.loc = loc

    st.markdown(f'<div class="doc-card" style="text-align:center;">📍 موقعك الحالي: {loc["city"]}</div>', unsafe_allow_html=True)

    # عرض أطباء مقترحين في البداية
    st.write("### 🏥 أطباء متاحون الآن بالقرب منك:")
    candidates = []
    for d in DATA["أطباء"]:
        d["dist"] = calculate_dist(loc["lat"], loc["lon"], d["lat"], d["lon"])
        candidates.append(d)
    
    for d in sorted(candidates, key=lambda x: x["dist"])[:2]:
        st.markdown(f'<div class="doc-card"><div class="recommend-badge">⭐ مقترح</div><br><b>{d["n"]}</b> - {d["s"]}<br><span class="star">{"★"*d["stars"]}</span> | 📍 {d["a"]}</div>', unsafe_allow_html=True)

    name = st.text_input("الاسم الكامل")
    phone = st.text_input("رقم الهاتف")
    if st.button("دخول النظام"):
        if name and phone:
            st.session_state.p = {"name": name, "phone": phone}
            st.session_state.step = 2
            st.rerun()

# ================= المرحلة 2 =================
elif st.session_state.step == 2:
    st.markdown(f"<h3>أهلاً {st.session_state.p['name']}</h3>", unsafe_allow_html=True)
    text = st.text_area("اشرح حالتك الصحية بالتفصيل")

    if st.button("بدء التحليل"):
        with st.spinner("جاري التحليل..."):
            # برومبت محسن لضمان شكل المخرجات
            prompt = f"حلل الحالة التالية في سطرين فقط وبشكل مرتب: {text}. اذكر الاختصاص والتشخيص المبدئي."
            res = model.generate_content(prompt).text
            st.session_state.res = res
            st.session_state.specs = [s for s in ["قلبية", "باطنية", "مفاصل"] if s in res] or ["باطنية"]

    if "res" in st.session_state:
        st.markdown(f'<div class="doc-card" style="border-right:5px solid #40E0D0;"><b>🩺 النتيجة:</b><br>{st.session_state.res}</div>', unsafe_allow_html=True)
        st.markdown('<div class="legal-disclaimer">⚠️ هذا التحليل استشاري فقط ولا يُغني عن مراجعة الطبيب المختص</div>', unsafe_allow_html=True)

        loc = st.session_state.loc
        matches = [d for d in DATA["أطباء"] if d["s"] in st.session_state.specs]
        
        st.write("### 👨‍⚕️ الأطباء المرشحون:")
        for d in sorted(matches, key=lambda x: calculate_dist(loc["lat"], loc["lon"], x["lat"], x["lon"])):
            st.markdown(f'<div class="doc-card"><div class="recommend-badge">⭐ الأنسب</div><br><b>{d["n"]}</b> – {d["s"]}<br><span class="star">{"★"*d["stars"]}</span> | 📍 {d["a"]}</div>', unsafe_allow_html=True)

            cols = st.columns(len(d["slots"]))
            for i, (t, v) in enumerate(d["slots"].items()):
                with cols[i]:
                    if v:
                        if st.button(f"✅ {t}", key=f"{d['n']}{t}"):
                            st.session_state.doc, st.session_state.time, st.session_state.step = d, t, 3
                            st.rerun()
                    else:
                        st.button(f"🔒 {t}", key=f"locked-{d['n']}{t}", disabled=True)

# ================= المرحلة 3 =================
elif st.session_state.step == 3:
    d = st.session_state.doc
    st.markdown(f"""
    <div class="success-panel">
        <h2 style="color:#40E0D0;">تم تأكيد الحجز ✅</h2>
        <div style="text-align:right; display:inline-block;">
            <p><b>المريض:</b> {st.session_state.p['name']}</p>
            <p><b>الطبيب:</b> {d['n']}</p>
            <p><b>الموعد:</b> {st.session_state.time}</p>
            <p><b>الموقع:</b> {d['a']}</p>
            <p><b>الهاتف:</b> {d['phone']}</p>
        </div>
        <hr style="border:0.5px dashed #333;">
        <h3 style="color:#40E0D0;">نتمنى لكم الصحة والعافية 🌿</h3>
    </div>
    """, unsafe_allow_html=True)

    if st.button("العودة للرئيسية"):
        st.session_state.step = 1
        st.rerun()
