import streamlit as st
import math
from streamlit_js_eval import get_geolocation

# --- 1. التنسيق الفيروزي والأسود الثابت ---
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
    .wish-safe { color: #40E0D0; font-size: 24px; font-weight: bold; margin-top: 20px; display: block; text-align: center; }
    </style>
    ''', unsafe_allow_html=True)

# --- 2. البيانات المثبتة (أطباء + 30 عارض + مناطق) ---
AREAS = {
    "المنصور": (33.3251, 44.3482), "الحارثية": (33.3222, 44.3585), "الكرادة": (33.3135, 44.4291),
    "الجادرية": (33.2801, 44.3905), "الأعظمية": (33.3652, 44.3751), "زيونة": (33.3401, 44.4502),
    "الدورة": (33.2500, 44.4000), "السيدية": (33.2650, 44.3600), "العامرية": (33.3200, 44.2800),
    "الغزالية": (33.3400, 44.2500), "حي الجامعة": (33.3350, 44.3100), "البياع": (33.2800, 44.3400),
    "بغداد الجديدة": (33.3000, 44.4800), "الشعب": (33.4000, 44.4200), "الكاظمية": (33.3800, 44.3400),
    "البنوك": (33.3900, 44.4300), "الوزيرية": (33.3500, 44.3800), "الأمين": (33.2800, 44.4900),
    "الصليخ": (33.3700, 44.3900), "شارع المغرب": (33.3550, 44.3800)
}

DATA = {
    "أطباء": [
        {"n": "د. علي الركابي", "s": "قلبية", "desc": "استشاري قسطرة وأمراض قلب", "a": "الحارثية", "lat": 33.3222, "lon": 44.3585, "stars": 5, "p": "07701234567"},
        {"n": "د. عمر الخفاجي", "s": "جملة عصبية", "desc": "جراح دماغ وفقرات", "a": "الجادرية", "lat": 33.2801, "lon": 44.3905, "stars": 5, "p": "07705556667"},
        {"n": "د. مريم القيسي", "s": "مفاصل", "desc": "أخصائية الروماتزم", "a": "الكرادة", "lat": 33.3135, "lon": 44.4291, "stars": 5, "p": "07901231234"},
        {"n": "د. حسن الهاشمي", "s": "باطنية", "desc": "أخصائي أمراض هضمية وكبد", "a": "الأعظمية", "lat": 33.3652, "lon": 44.3751, "stars": 5, "p": "07801212123"},
        {"n": "د. زينة الحسني", "s": "جلدية", "desc": "أخصائية أمراض الجلد والليزر", "a": "زيونة", "lat": 33.3401, "lon": 44.4502, "stars": 5, "p": "07703332221"}
    ],
    "أعراض": {
        "ألم حاد ومفاجئ في الصدر": ("قلبية", 10, "🚨 طوارئ: اشتباه ذبحة صدرية"),
        "خفقان قلب سريع جداً": ("قلبية", 7, "التشخيص: تسارع ضربات قلب"),
        "ثقل في الكلام وخدر جانبي": ("جملة عصبية", 10, "🚨 طوارئ: اشتباه سكتة دماغية"),
        "صداع انفجاري مفاجئ": ("جملة عصبية", 9, "🚨 طوارئ: احتمال نزف دماغي"),
        "ألم مفاصل وتيبس صباحي": ("مفاصل", 5, "التشخيص: التهاب مفاصل روماتزمي"),
        "ألم أسفل الظهر مع الساق": ("مفاصل", 5, "التشخيص: انزلاق غضروفي"),
        "ألم بطن يمين حاد جداً": ("باطنية", 9, "🚨 طوارئ: اشتباه زائدة دودية"),
        "اصفرار في العين والجلد": ("باطنية", 7, "التشخيص: يرقان - كبد فيروسي"),
        "ضيق تنفس حاد وازرقاق": ("باطنية", 10, "🚨 طوارئ: فشل تنفسي"),
        "عطش شديد وتبول متكرر": ("باطنية", 5, "التشخيص: اضطراب سكر الدم"),
        "خمول دائم ونعاس": ("باطنية", 4, "التشخيص: خمول غدة درقية"),
        "طفح جلدي وحكة شديدة": ("جلدية", 4, "التشخيص: حساسية جلدية حادة"),
        "تساقط شعر فراغي": ("جلدية", 4, "التشخيص: داء الثعلبة"),
        "تنميل في الأطراف": ("جملة عصبية", 5, "التشخيص: اعتلال أعصاب"),
        "دوار مستمر وطنين أذن": ("جملة عصبية", 5, "التشخيص: اضطراب توازن"),
        "حرقة معدة تزداد ليلاً": ("باطنية", 4, "التشخيص: ارتجاع مريئي"),
        "غازات وانتفاخ دائم": ("باطنية", 4, "التشخيص: قولون عصبي"),
        "حرارة مرتفعة مستمرة": ("باطنية", 7, "التشخيص: عدوى بكتيرية"),
        "ضعف عام وشحوب": ("باطنية", 4, "التشخيص: فقر دم"),
        "رعشة في اليدين": ("جملة عصبية", 6, "التشخيص: رعاش عصبي"),
        "سعال جاف مستمر": ("باطنية", 5, "التشخيص: تحسس قصبي"),
        "ألم أذن حاد": ("باطنية", 5, "التشخيص: التهاب أذن وسطى"),
        "نزف أنف متكرر": ("باطنية", 6, "التشخيص: ضعف شعيرات"),
        "تورم ساق واحدة وألم": ("باطنية", 8, "🚨 احتمال جلطة وريدية"),
        "تعرق ليلي شديد": ("باطنية", 7, "التشخيص: يحتاج فحوصات"),
        "صداع مزمن خلف الرأس": ("جملة عصبية", 4, "التشخيص: صداع توتري"),
        "ألم الفك عند المضغ": ("مفاصل", 4, "التشخيص: اضطراب مفصل الفك"),
        "جفاف عين وحرقان": ("باطنية", 3, "التشخيص: نقص دمع"),
        "نزيف لثة مستمر": ("باطنية", 4, "التشخيص: التهاب لثة"),
        "فقدان توازن مفاجئ": ("جملة عصبية", 6, "التشخيص: دوار وضعي")
    }
}

if 'step' not in st.session_state: st.session_state.step = 1

def calculate_dist(lat1, lon1, lat2, lon2):
    try:
        val = (lat1 - lat2)*2 + (lon1 - lon2)*2
        return math.sqrt(max(0, val)) * 111.13
    except: return 0.0

# --- الصفحة 1: المعلومات ---
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
                loc = get_geolocation()
                st.session_state.u_coords = (loc['coords']['latitude'], loc['coords']['longitude']) if loc and 'coords' in loc else AREAS[u_area]
                st.session_state.step = 2
                st.rerun()

# --- الصفحة 2: التشخيص ---
elif st.session_state.step == 2:
    st.markdown('<div class="welcome-title" style="font-size:35px;">AI Doctor ⛑️</div>', unsafe_allow_html=True)
    sel = st.selectbox("بماذا تشعر اليوم؟", ["اختر العارض..."] + list(DATA["أعراض"].keys()))
    if sel != "اختر العارض...":
        spec, urg, diag = DATA["أعراض"][sel]
        st.session_state.selected_spec = spec
        st.markdown(f'<div class="diag-box"><h4>🔍 التشخيص الذكي:</h4><p style="font-size:18px;">{diag}</p></div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ رجوع"): st.session_state.step = 1; st.rerun()
        with col2:
            if st.button("حجز أقرب طبيب"): st.session_state.step = 3; st.rerun()

# --- الصفحة 3: المواعيد (3-9 مساءً) ---
elif st.session_state.step == 3:
    st.markdown('<div class="welcome-title" style="font-size:28px;">حجز موعد 📅</div>', unsafe_allow_html=True)
    u_lat, u_lon = st.session_state.u_coords
    matches = [d for d in DATA["أطباء"] if d['s'] == st.session_state.selected_spec]
    for d in matches: d['current_dist'] = calculate_dist(u_lat, u_lon, d['lat'], d['lon'])
    
    for d in sorted(matches, key=lambda x: x['current_dist']):
        st.markdown(f'''
            <div class="doc-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div><span style="font-size:20px; color:#40E0D0;"><b>{d['n']}</b></span><br>
                    <span style="color:#FFD700; font-size:14px;">{"⭐" * d['stars']} | اختصاص {d['s']}</span></div>
                    <span style="color:#40E0D0; font-weight:bold;">📍 {("في منطقتك" if d['current_dist'] < 0.5 else f"{d['current_dist']:.1f} كم")}</span>
                </div>
            </div>
        ''', unsafe_allow_html=True)
        
        slots = {"03:00 PM": True, "04:00 PM": False, "05:00 PM": True, "06:00 PM": True, "07:00 PM": False, "08:00 PM": True, "09:00 PM": True}
        cols = st.columns(4)
        for i, (time_str, available) in enumerate(slots.items()):
            with cols[i % 4]:
                if available:
                    if st.button(f"✅ {time_str}", key=f"t_{d['n']}_{time_str}"):
                        st.session_state.final = {"doc": d['n'], "time": time_str, "area": d['a'], "phone": d['p']}
                        st.session_state.step = 4; st.rerun()
                else: st.markdown(f'<div class="slot-box slot-booked">🔒 {time_str}</div>', unsafe_allow_html=True)

    if st.button("⬅️ السابق"): st.session_state.step = 2; st.rerun()

# --- الصفحة 4: النجاح النهائي ---
elif st.session_state.step == 4:
    f, p = st.session_state.final, st.session_state.p_data
    st.markdown(f'''
        <div style="border: 2px solid #40E0D0; border-radius: 20px; padding: 40px; text-align: center;">
            <h1 style="color:#40E0D0; font-size:40px;">✅ تم الحجز بنجاح</h1>
            <p>شكراً <b>{p['name']}</b>. تم تأكيد موعدك.</p>
            <div style="background:#111; padding:25px; border-radius:15px; margin:25px 0; border:1px solid #333; text-align:right;">
                <p>👨‍⚕️ الطبيب: {f['doc']}</p><p>⏰ الوقت: {f['time']}</p><p>📍 الموقع: بغداد - {f['area']}</p>
                <p>📞 هاتف العيادة: <span style="color:#40E0D0;">{f['phone']}</span></p>
            </div>
            <span class="wish-safe">نتمنى لكم السلامة .. 💐</span>
        </div>
    ''', unsafe_allow_html=True)
    if st.button("حجز جديد"): st.session_state.step = 1; st.rerun()
