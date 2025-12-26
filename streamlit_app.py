import streamlit as st
import math

# --- 1. التنسيق الثابت المعتمد (فيروزي وأسود) ---
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
    .success-card { border: 2px solid #40E0D0; border-radius: 20px; padding: 30px; text-align: center; }
    </style>
    ''', unsafe_allow_html=True)

# --- قاعدة البيانات المتصلة .2 
AREAS = {
    "المنصور": (33.3251, 44.3482), "الحارثية": (33.3222, 44.3585), "الكرادة": (33.3135, 44.4291),
    "الجادرية": (33.2801, 44.3905), "الأعظمية": (33.3652, 44.3751), "زيونة": (33.3401, 44.4502),
    "الدورة": (33.2500, 44.4000), "السيدية": (33.2650, 44.3600), "العامرية": (33.3200, 44.2800),
    "اليرموك": (33.3100, 44.3300), "الكاظمية": (33.3800, 44.3400), "البنوك": (33.3900, 44.4300)
}

DATA = {
    "أطباء": [
        {"n": "د. علي الركابي", "s": "قلبية", "desc": "استشاري قسطرة وأمراض قلب", "a": "الحارثية", "lat": 33.3222, "lon": 44.3585, "stars": 5, "p": "07701234567"},
        {"n": "د. سارة الجبوري", "s": "قلبية", "desc": "أخصائية سونار القلب المتقدم", "a": "المنصور", "lat": 33.3251, "lon": 44.3482, "stars": 4, "p": "07809876543"},
        {"n": "د. زيد الشمري", "s": "قلبية", "desc": "بورد عراقي - كهربائية القلب", "a": "الكرادة", "lat": 33.3135, "lon": 44.4291, "stars": 5, "p": "07901112233"},
        {"n": "د. عمر الخفاجي", "s": "جملة عصبية", "desc": "جراح دماغ وفقرات", "a": "الجادرية", "lat": 33.2801, "lon": 44.3905, "stars": 5, "p": "07702223344"},
        {"n": "د. حيدر عباس", "s": "جملة عصبية", "desc": "أخصائي طب الأعصاب والصرع", "a": "الأعظمية", "lat": 33.3652, "lon": 44.3751, "stars": 4, "p": "07804445566"},
        {"n": "د. مريم القيسي", "s": "مفاصل", "desc": "أخصائية الروماتزم وحقن المفاصل", "a": "الكرادة", "lat": 33.3135, "lon": 44.4291, "stars": 5, "p": "07905556677"},
        {"n": "د. ليث العاني", "s": "مفاصل", "desc": "استشاري طب الكسور والمفاصل", "a": "العامرية", "lat": 33.3200, "lon": 44.2800, "stars": 4, "p": "07706667788"},
        {"n": "د. حسن الهاشمي", "s": "باطنية", "desc": "أخصائي أمراض هضمية وكبد", "a": "الأعظمية", "lat": 33.3652, "lon": 44.3751, "stars": 5, "p": "07807778899"},
        {"n": "د. نور الهدى", "s": "باطنية", "desc": "أخصائية غدد صماء وسكري", "a": "زيونة", "lat": 33.3401, "lon": 44.4502, "stars": 5, "p": "07908889900"},
        {"n": "د. زينة الحسني", "s": "جلدية", "desc": "أخصائية أمراض الجلد والليزر", "a": "زيونة", "lat": 33.3401, "lon": 44.4502, "stars": 5, "p": "07709990011"},
        {"n": "د. رامي السعدي", "s": "جلدية", "desc": "تجميل وجلدية - بورد عربي", "a": "المنصور", "lat": 33.3251, "lon": 44.3482, "stars": 4, "p": "07801112244"}
    ],
    "أعراض": {
        "ألم حاد ومفاجئ في الصدر": ("قلبية", 10, "🚨 طوارئ: اشتباه ذبحة صدرية"),
        "ثقل في الكلام وخدر جانبي": ("جملة عصبية", 10, "🚨 طوارئ: اشتباه سكتة دماغية"),
        "ألم بطن يمين حاد جداً": ("باطنية", 9, "🚨 طوارئ: اشتباه زائدة دودية"),
        "ضيق تنفس حاد وازرقاق": ("باطنية", 10, "🚨 طوارئ: فشل تنفسي"),
        "صداع انفجاري مفاجئ": ("جملة عصبية", 9, "🚨 طوارئ: احتمال نزف دماغي"),
        "تورم ساق واحدة مع ألم": ("باطنية", 8, "🚨 تنبيه: احتمال جلطة وريدية بالساق"),
        "خفقان قلب وقت الراحة": ("قلبية", 7, "التشخيص: تسارع ضربات قلب"),
        "اصفرار في العين والجلد": ("باطنية", 7, "التشخيص: يرقان - كبد فيروسي"),
        "حرارة مرتفعة لا تنخفض": ("باطنية", 7, "التشخيص: عدوى بكتيرية حادة"),
        "تعرق ليلي شديد": ("باطنية", 7, "التشخيص: يحتاج فحوصات شاملة"),
        "رعشة في اليدين": ("جملة عصبية", 6, "التشخيص: رعاش عصبي"),
        "نزف أنف متكرر": ("باطنية", 6, "التشخيص: ضعف شعيرات أنفية"),
        "فقدان توازن عند الوقوف": ("جملة عصبية", 6, "التشخيص: دوار وضعي حميد"),
        "دوار مستمر وطنين أذن": ("جملة عصبية", 5, "التشخيص: اضطراب توازن"),
        "ألم مفاصل وتيبس صباحي": ("مفاصل", 5, "التشخيص: التهاب مفاصل روماتزمي"),
        "تنميل في الأطراف المستمر": ("جملة عصبية", 5, "التشخيص: اعتلال أعصاب محيطية"),
        "ألم أسفل الظهر مع الساق": ("مفاصل", 5, "التشخيص: انزلاق غضروفي (عرق النسا)"),
        "عطش شديد وتبول متكرر": ("باطنية", 5, "التشخيص: اضطراب سكر الدم"),
        "سعال جاف مستمر": ("باطنية", 5, "التشخيص: تحسس قصبي"),
        "ألم أذن حاد وإفرازات": ("باطنية", 5, "التشخيص: التهاب أذن وسطى"),
        "طفح جلدي شديد وحكة": ("جلدية", 4, "التشخيص: حساسية جلدية حادة"),
        "حرقة معدة تزداد ليلاً": ("باطنية", 4, "التشخيص: ارتجاع مريئي"),
        "خمول دائم ونعاس": ("باطنية", 4, "التشخيص: خمول غدة درقية"),
        "غازات وانتفاخ دائم": ("باطنية", 4, "التشخيص: قولون عصبي"),
        "ضعف عام وشحوب": ("باطنية", 4, "التشخيص: فقر دم"),
        "تساقط شعر فراغي": ("جلدية", 4, "التشخيص: داء الثعلبة"),
        "نزيف لثة مستمر": ("باطنية", 4, "التشخيص: التهاب لثة"),
        "صداع مزمن خلف الرأس": ("جملة عصبية", 4, "التشخيص: صداع توتري"),
        "ألم الفك عند المضغ": ("مفاصل", 4, "التشخيص: اضطراب مفصل الفك"),
        "جفاف عين وحرقان": ("باطنية", 3, "التشخيص: نقص إفراز الدمع")
    }
}

# --- 3. الدوال ---
if 'step' not in st.session_state: st.session_state.step = 1

def calculate_dist(lat1, lon1, lat2, lon2):
    return math.sqrt((lat1-lat2)*2 + (lon1-lon2)*2) * 111.13

# --- 4. الصفحات ---

# الصفحة 1: الترحيب والمنطقة
if st.session_state.step == 1:
    st.markdown('<div class="welcome-title">Welcome to AI Doctor 🩺</div>', unsafe_allow_html=True)
    st.markdown('<div class="welcome-sub">BAGHDAD PREMIUM HEALTHCARE</div>', unsafe_allow_html=True)
    with st.form("p_info"):
        name = st.text_input("الأسم الكامل")
        u_area = st.selectbox("اختر منطقتك في بغداد (للبحث عن الأقرب):", sorted(list(AREAS.keys())))
        phone = st.text_input("رقم الهاتف")
        if st.form_submit_button("دخول النظام"):
            if name and phone:
                st.session_state.p_data = {"name": name, "area": u_area, "phone": phone}
                st.session_state.u_coords = AREAS[u_area]
                st.session_state.step = 2
                st.rerun()
            else: st.error("يرجى ملء البيانات")

# الصفحة 2: AI Doctor ⛑️
elif st.session_state.step == 2:
    st.markdown('<div class="welcome-title" style="font-size:35px;">AI Doctor ⛑️</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#40E0D0;">بماذا تشعر اليوم؟</p>', unsafe_allow_html=True)
    sel = st.selectbox("قائمة الأعراض (30 عارض طبي):", ["اختر..."] + list(DATA["أعراض"].keys()))
    
    if sel != "اختر...":
        spec, urg, diag = DATA["أعراض"][sel]
        st.session_state.selected_spec = spec
        st.markdown(f'''
            <div class="diag-box">
                <h4 style="color:#40E0D0;">🔍 التشخيص الذكي:</h4>
                <p style="font-size:18px;">{diag}</p>
            </div>
            <div class="disclaimer-card">
                <b>⚠️ إخلاء مسؤولية وطوارئ</b><br>
                هذا التحليل استرشادي فقط. للحالات الحرجة اتصل بـ <b>122</b> فوراً.
            </div>
        ''', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ رجوع"): st.session_state.step = 1; st.rerun()
        with col2:
            if st.button("حجز أقرب طبيب"): st.session_state.step = 3; st.rerun()

# الصفحة 3: الحجوزات
elif st.session_state.step == 3:
    st.markdown('<div class="welcome-title" style="font-size:28px;">حجز موعد 📅</div>', unsafe_allow_html=True)
    u_lat, u_lon = st.session_state.u_coords
    matches = []
    for d in DATA["أطباء"]:
        if d['s'] == st.session_state.selected_spec:
            d['dist'] = calculate_dist(u_lat, u_lon, d['lat'], d['lon'])
            matches.append(d)
    
    matches = sorted(matches, key=lambda x: x['dist'])
    
    for d in matches:
        st.markdown(f'''
            <div class="doc-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:20px; color:#40E0D0;"><b>{d['n']}</b></span>
                    <span style="color:#40E0D0; font-weight:bold;">📍 ({d['dist']:.1f} كم)</span>
                </div>
                <div style="color:#FFD700; font-size:14px;">{"⭐" * d['stars']} | اختصاص {d['s']}</div>
                <div style="font-size:13px; margin-top:5px; color:#bbb;">{d['desc']} - {d['a']}</div>
            </div>
        ''', unsafe_allow_html=True)
        
        slots = {"04:00 PM": True, "05:00 PM": False, "06:00 PM": True, "07:00 PM": False, "08:00 PM": True, "09:00 PM": False}
        cols = st.columns(3)
        for i, (time_str, available) in enumerate(slots.items()):
            with cols[i % 3]:
                if available:
                    if st.button(f"✅ {time_str}", key=f"t_{d['n']}_{time_str}"):
                        st.session_state.final = {"doc": d['n'], "time": time_str, "area": d['a'], "phone": d['p']}
                        st.session_state.step = 4
                        st.rerun()
                else:
                    st.markdown(f'<div class="slot-box slot-booked">🔒 {time_str}</div>', unsafe_allow_html=True)

    if st.button("⬅️ السابق"): st.session_state.step = 2; st.rerun()

# الصفحة 4: تم الحجز (إعادة لمسة النهاية)
elif st.session_state.step == 4:
    f, p = st.session_state.final, st.session_state.p_data
    st.markdown(f'''
        <div class="success-card">
            <h1 style="color:#40E0D0; font-size:40px;">✅ تم الحجز بنجاح</h1>
            <p style="font-size:18px;">شكراً لثقتك بنا <b>{p['name']}</b>.</p>
            <div style="background:#111; padding:25px; border-radius:15px; margin:25px 0; border:1px solid #333; text-align:right;">
                <p>👨‍⚕️ الطبيب: {f['doc']}</p>
                <p>⏰ الموعد: اليوم - {f['time']}</p>
                <p>📍 الموقع: بغداد - {f['area']}</p>
                <p>📞 هاتف العيادة: <span style="color:#40E0D0;">{f['phone']}</span></p>
            </div>
            <p style="color:#888;">تم إرسال تفاصيل الموعد إلى رقمك: {p['phone']}</p>
        </div>
    ''', unsafe_allow_html=True)
    if st.button("حجز جديد"):
        st.session_state.step = 1
        st.rerun()
