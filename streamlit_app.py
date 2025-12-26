import streamlit as st
import math

# --- 1. التنسيق الثابت (فيروزي وأسود) ---
st.set_page_config(page_title="AI Doctor Baghdad", layout="centered")

st.markdown(r'''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&family=Playfair+Display:wght@700&display=swap');
    * { font-family: 'Tajawal', sans-serif; direction: rtl; }
    .stApp { background-color: #050505; color: #e0e0e0; }
    .welcome-title { font-family: 'Playfair Display', serif; font-size: 42px; text-align: center; color: #40E0D0; margin-bottom: 5px; }
    .welcome-sub { text-align: center; color: #40E0D0; font-size: 12px; margin-bottom: 40px; letter-spacing: 3px; opacity: 0.7; }
    .diag-box { background: rgba(64, 224, 208, 0.05); border: 1px solid #40E0D0; padding: 20px; border-radius: 15px; margin-bottom: 20px; }
    .doc-card { background-color: #0d0d0d; padding: 20px; border-radius: 15px; border-right: 8px solid #40E0D0; border: 1px solid #333; margin-bottom: 15px; }
    .slot-box { padding: 12px; text-align: center; border-radius: 8px; font-weight: bold; font-size: 14px; margin-bottom: 10px; }
    .slot-booked { background: rgba(255, 255, 255, 0.05); border: 1px solid #333; color: #555; }
    .stButton>button { background-color: transparent; color: #40E0D0 !important; border: 1px solid #40E0D0 !important; border-radius: 8px; width: 100%; transition: 0.3s; }
    .stButton>button:hover { background-color: #40E0D0 !important; color: #000 !important; }
    .disclaimer-card { background: rgba(255, 0, 0, 0.05); border: 1px solid #ff4b4b; padding: 15px; border-radius: 10px; color: #ff4b4b; text-align: center; margin: 20px 0; }
    </style>
    ''', unsafe_allow_html=True)

# --- 2. قائمة مناطق بغداد الكاملة ---
AREAS = {
    "المنصور": (33.3251, 44.3482), "الحارثية": (33.3222, 44.3585), "الكرادة": (33.3135, 44.4291),
    "الجادرية": (33.2801, 44.3905), "الأعظمية": (33.3652, 44.3751), "زيونة": (33.3401, 44.4502),
    "الدورة": (33.2500, 44.4000), "السيدية": (33.2650, 44.3600), "العامرية": (33.3200, 44.2800),
    "الغزالية": (33.3400, 44.2500), "حي الجامعة": (33.3350, 44.3100), "البياع": (33.2800, 44.3400),
    "بغداد الجديدة": (33.3000, 44.4800), "الغدير": (33.3150, 44.4700), "الشعب": (33.4000, 44.4200),
    "مدينة الصدر": (33.3800, 44.4600), "الزعفرانية": (33.2400, 44.4800), "القادسية": (33.3000, 44.3600),
    "اليرموك": (33.3100, 44.3300), "الكاظمية": (33.3800, 44.3400), "الصليخ": (33.3700, 44.3900),
    "الأمين": (33.2800, 44.4900), "الوزيرية": (33.3500, 44.3800), "البنوك": (33.3900, 44.4300)
}

DATA = {
    "أطباء": [
        {"n": "د. علي الركابي", "s": "قلبية", "desc": "استشاري قسطرة وأمراض قلب", "a": "الحارثية", "lat": 33.3222, "lon": 44.3585, "stars": 5, "p": "07701234567"},
        {"n": "د. سارة الجبوري", "s": "قلبية", "desc": "أخصائية سونار القلب", "a": "المنصور", "lat": 33.3251, "lon": 44.3482, "stars": 4, "p": "07809876543"},
        {"n": "د. عمر الخفاجي", "s": "جملة عصبية", "desc": "جراح دماغ وفقرات", "a": "الجادرية", "lat": 33.2801, "lon": 44.3905, "stars": 5, "p": "07702223344"},
        {"n": "د. مريم القيسي", "s": "مفاصل", "desc": "أخصائية الروماتزم", "a": "الكرادة", "lat": 33.3135, "lon": 44.4291, "stars": 5, "p": "07905556677"},
        {"n": "د. حسن الهاشمي", "s": "باطنية", "desc": "أخصائي هضمية وكبد", "a": "الأعظمية", "lat": 33.3652, "lon": 44.3751, "stars": 5, "p": "07807778899"},
        {"n": "د. زينة الحسني", "s": "جلدية", "desc": "أخصائية ليزر وجلدية", "a": "زيونة", "lat": 33.3401, "lon": 44.4502, "stars": 5, "p": "07709990011"}
        # يمكن إضافة المزيد من الأطباء بنفس النمط هنا
    ],
    "أعراض": {
        "ألم حاد ومفاجئ في الصدر": ("قلبية", 10, "🚨 طوارئ: اشتباه ذبحة صدرية"),
        "ثقل في الكلام وخدر جانبي": ("جملة عصبية", 10, "🚨 طوارئ: اشتباه سكتة دماغية"),
        "ألم بطن يمين حاد جداً": ("باطنية", 9, "🚨 طوارئ: اشتباه زائدة دودية"),
        "ضيق تنفس حاد": ("باطنية", 10, "🚨 طوارئ: فشل تنفسي"),
        "خفقان قلب وقت الراحة": ("قلبية", 7, "التشخيص: تسارع ضربات قلب"),
        "اصفرار في العين والجلد": ("باطنية", 7, "التشخيص: يرقان - كبد فيروسي"),
        "ألم مفاصل وتيبس صباحي": ("مفاصل", 5, "التشخيص: التهاب مفاصل روماتزمي"),
        "ألم أسفل الظهر مع الساق": ("مفاصل", 5, "التشخيص: انزلاق غضروفي"),
        "عطش شديد وتبول متكرر": ("باطنية", 5, "التشخيص: اضطراب سكر الدم"),
        "خمول دائم ونعاس": ("باطنية", 4, "التشخيص: خمول غدة درقية"),
        "طفح جلدي شديد وحكة": ("جلدية", 4, "التشخيص: حساسية جلدية حادة"),
        "تساقط شعر فراغي": ("جلدية", 4, "التشخيص: داء الثعلبة"),
        "نزيف لثة مستمر": ("باطنية", 4, "التشخيص: التهاب لثة"),
        "صداع مزمن خلف الرأس": ("جملة عصبية", 4, "التشخيص: صداع توتري"),
        "ألم الفك عند المضغ": ("مفاصل", 4, "التشخيص: اضطراب مفصل الفك"),
        "جفاف عين وحرقان": ("باطنية", 3, "التشخيص: نقص إفراز الدمع"),
        "غازات وانتفاخ دائم": ("باطنية", 4, "التشخيص: قولون عصبي"),
        "تنميل في الأطراف": ("جملة عصبية", 5, "التشخيص: اعتلال أعصاب"),
        "حرقة معدة تزداد ليلاً": ("باطنية", 4, "التشخيص: ارتجاع مريئي"),
        "دوار مستمر وطنين": ("جملة عصبية", 5, "التشخيص: اضطراب توازن"),
        "نزف أنف متكرر": ("باطنية", 6, "التشخيص: ضعف شعيرات"),
        "ألم أذن حاد": ("باطنية", 5, "التشخيص: التهاب أذن"),
        "رعشة في اليدين": ("جملة عصبية", 6, "التشخيص: رعاش عصبي"),
        "سعال جاف مستمر": ("باطنية", 5, "التشخيص: تحسس قصبي"),
        "صداع انفجاري": ("جملة عصبية", 9, "🚨 طوارئ: احتمال نزف دماغي"),
        "حرارة مرتفعة": ("باطنية", 7, "التشخيص: عدوى بكتيرية"),
        "ضعف عام وشحوب": ("باطنية", 4, "التشخيص: فقر دم"),
        "تعرق ليلي": ("باطنية", 7, "التشخيص: يحتاج فحوصات"),
        "تورم ساق واحدة": ("باطنية", 8, "🚨 احتمال جلطة وريدية"),
        "فقدان توازن": ("جملة عصبية", 6, "التشخيص: دوار وضعي")
    }
}

# --- 3. الدوال البرمجية (معالجة الخطأ الجذري) ---
if 'step' not in st.session_state: st.session_state.step = 1

def calculate_dist(lat1, lon1, lat2, lon2):
    # الحل الجذري للـ ValueError: التأكد من أن القيمة ليست سالبة أبداً
    inner_val = (lat1-lat2)*2 + (lon1-lon2)*2
    if inner_val < 0: inner_val = 0 
    return math.sqrt(inner_val) * 111.13

# --- 4. الصفحات ---

if st.session_state.step == 1:
    st.markdown('<div class="welcome-title">Welcome to AI Doctor 🩺</div>', unsafe_allow_html=True)
    st.markdown('<div class="welcome-sub">BAGHDAD PREMIUM HEALTHCARE</div>', unsafe_allow_html=True)
    with st.form("p_info"):
        name = st.text_input("الأسم الكامل")
        u_area = st.selectbox("اختر منطقتك الحالية في بغداد:", sorted(list(AREAS.keys())))
        phone = st.text_input("رقم الهاتف")
        if st.form_submit_button("دخول النظام"):
            if name and phone:
                st.session_state.p_data = {"name": name, "area": u_area, "phone": phone}
                st.session_state.u_coords = AREAS[u_area]
                st.session_state.step = 2
                st.rerun()
            else: st.error("يرجى ملء كافة الحقول")

elif st.session_state.step == 2:
    st.markdown('<div class="welcome-title" style="font-size:35px;">AI Doctor ⛑️</div>', unsafe_allow_html=True)
    sel = st.selectbox("بماذا تشعر اليوم؟", ["اختر العارض..."] + list(DATA["أعراض"].keys()))
    if sel != "اختر العارض...":
        spec, urg, diag = DATA["أعراض"][sel]
        st.session_state.selected_spec = spec
        st.markdown(f'<div class="diag-box"><h4>🔍 التشخيص الذكي:</h4><p>{diag}</p></div>', unsafe_allow_html=True)
        st.markdown('<div class="disclaimer-card"><b>⚠️ طوارئ: 122</b></div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ رجوع"): st.session_state.step = 1; st.rerun()
        with col2:
            if st.button("حجز الطبيب الأقرب"): st.session_state.step = 3; st.rerun()

elif st.session_state.step == 3:
    st.markdown('<div class="welcome-title" style="font-size:28px;">حجز موعد 📅</div>', unsafe_allow_html=True)
    u_lat, u_lon = st.session_state.u_coords
    matches = [d for d in DATA["أطباء"] if d['s'] == st.session_state.selected_spec]
    
    for d in matches:
        d['dist'] = calculate_dist(u_lat, u_lon, d['lat'], d['lon'])
    
    for d in sorted(matches, key=lambda x: x['dist']):
        st.markdown(f'''
            <div class="doc-card">
                <div style="display:flex; justify-content:space-between;">
                    <span style="font-size:20px; color:#40E0D0;"><b>{d['n']}</b></span>
                    <span style="color:#40E0D0;">📍 {d['dist']:.1f} كم</span>
                </div>
                <div style="font-size:13px; color:#bbb;">{d['desc']} - {d['a']}</div>
            </div>
        ''', unsafe_allow_html=True)
        
        slots = {"04:00 PM": True, "05:00 PM": False, "06:00 PM": True}
        cols = st.columns(3)
        for i, (time_str, available) in enumerate(slots.items()):
            with cols[i % 3]:
                if available:
                    if st.button(f"✅ {time_str}", key=f"t_{d['n']}_{time_str}"):
                        st.session_state.final = {"doc": d['n'], "time": time_str, "area": d['a'], "phone": d['p']}
                        st.session_state.step = 4
                        st.rerun()
                else: st.markdown(f'<div class="slot-box slot-booked">🔒 {time_str}</div>', unsafe_allow_html=True)
    
    if st.button("⬅️ السابق"): st.session_state.step = 2; st.rerun()

elif st.session_state.step == 4:
    f, p = st.session_state.final, st.session_state.p_data
    st.markdown(f'''
        <div style="border:2px solid #40E0D0; border-radius:20px; padding:30px; text-align:center;">
            <h1 style="color:#40E0D0;">✅ تم الحجز بنجاح</h1>
            <p>المريض: <b>{p['name']}</b></p>
            <div style="background:#111; padding:20px; border-radius:15px; text-align:right;">
                <p>👨‍⚕️ الطبيب: {f['doc']}</p>
                <p>⏰ الموعد: {f['time']}</p>
                <p>📍 الموقع: {f['area']}</p>
                <p>📞 هاتف العيادة: <span style="color:#40E0D0;">{f['phone']}</span></p>
            </div>
        </div>
    ''', unsafe_allow_html=True)
    if st.button("حجز جديد"): st.session_state.step = 1; st.rerun()
