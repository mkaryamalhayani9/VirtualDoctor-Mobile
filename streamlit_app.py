import streamlit as st
import math
from streamlit_js_eval import get_geolocation

# --- 1. التنسيق المتطور (وميض الطوارئ وتنسيق الصفحات) ---
st.set_page_config(page_title="AI Doctor Baghdad", layout="centered")

st.markdown(r'''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&family=Playfair+Display:wght@700&display=swap');
    * { font-family: 'Tajawal', sans-serif; direction: rtl; text-align: center; }
    .stApp { background-color: #050505; color: #e0e0e0; }
    
    .welcome-title { font-family: 'Playfair Display', serif; font-size: 42px; color: #40E0D0; margin-bottom: 5px; }
    .page-header { font-family: 'Playfair Display', serif; font-size: 35px; color: #40E0D0; margin-top: 20px; }
    .ai-warning { background: rgba(255, 255, 255, 0.05); border: 1px solid #444; padding: 10px; border-radius: 10px; font-size: 12px; color: #888; margin-bottom: 20px; }
    
    .diag-box { margin: 20px auto; max-width: 600px; padding: 25px; border-radius: 15px; background: rgba(64, 224, 208, 0.05); border: 1px solid #40E0D0; }
    
    @keyframes blinker { 50% { opacity: 0.3; transform: scale(1.01); } }
    .emergency-box { 
        margin: 20px auto; max-width: 600px; padding: 25px; border-radius: 15px; 
        background: rgba(255, 0, 0, 0.2); border: 3px solid #ff4b4b; 
        box-shadow: 0 0 20px rgba(255, 75, 75, 0.6);
        animation: blinker 1s linear infinite;
    }
    
    .doc-card { background-color: #0d0d0d; padding: 20px; border-radius: 15px; border: 1px solid #333; border-bottom: 4px solid #40E0D0; margin: 15px auto; max-width: 600px; }
    .success-card { border: 2px solid #40E0D0; border-radius: 20px; padding: 40px; max-width:600px; margin:auto; background: rgba(64, 224, 208, 0.03); }
    .wish-safe { color: #40E0D0; font-size: 26px; font-weight: bold; margin-top: 30px; display: block; }
    </style>
    ''', unsafe_allow_html=True)

# --- 2. قاعدة البيانات الشاملة (المناطق + الأطباء + الأعراض) ---
AREAS_COORDS = {
    "المنصور": (33.3251, 44.3482), "الحارثية": (33.3222, 44.3585), "الكرادة": (33.3135, 44.4291),
    "الجادرية": (33.2801, 44.3905), "الأعظمية": (33.3652, 44.3751), "زيونة": (33.3401, 44.4502),
    "اليرموك": (33.3000, 44.3350), "الدورة": (33.2500, 44.4000), "السيدية": (33.2650, 44.3600),
    "حي الجامعة": (33.3350, 44.3100), "الكاظمية": (33.3800, 44.3400), "الشعب": (33.4000, 44.4200),
    "البنوك": (33.3900, 44.4300), "العامرية": (33.3200, 44.2800), "الغزالية": (33.3400, 44.2500)
}

DATA = {
    "أطباء": [
        {"n": "د. علي الركابي", "s": "قلبية", "a": "الحارثية", "lat": 33.3222, "lon": 44.3585, "stars": 5, "p": "07701234567"},
        {"n": "د. سارة الجبوري", "s": "قلبية", "a": "المنصور", "lat": 33.3251, "lon": 44.3482, "stars": 4, "p": "07801112223"},
        {"n": "د. محمد الزبيدي", "s": "قلبية", "a": "الكرادة", "lat": 33.3135, "lon": 44.4291, "stars": 5, "p": "07902223334"},
        {"n": "د. عمر الخفاجي", "s": "جملة عصبية", "a": "الجادرية", "lat": 33.2801, "lon": 44.3905, "stars": 5, "p": "07705556667"},
        {"n": "د. ليث الدوري", "s": "جملة عصبية", "a": "المنصور", "lat": 33.3251, "lon": 44.3482, "stars": 4, "p": "07700001112"},
        {"n": "د. حسن الهاشمي", "s": "باطنية", "a": "الأعظمية", "lat": 33.3652, "lon": 44.3751, "stars": 5, "p": "07801212123"},
        {"n": "د. مريم القيسي", "s": "مفاصل", "a": "الكرادة", "lat": 33.3135, "lon": 44.4291, "stars": 5, "p": "07901231234"},
        {"n": "د. ريم البياتي", "s": "جلدية", "a": "المنصور", "lat": 33.3251, "lon": 44.3482, "stars": 5, "p": "07705554433"},
        {"n": "د. سامر الحديثي", "s": "جلدية", "a": "اليرموك", "lat": 33.3000, "lon": 44.3350, "stars": 5, "p": "07802221110"},
        {"n": "د. ليث السامرائي", "s": "عيون", "a": "الكرادة", "lat": 33.3135, "lon": 44.4291, "stars": 5, "p": "07908887776"},
        {"n": "د. زينة القيسي", "s": "عيون", "a": "اليرموك", "lat": 33.3000, "lon": 44.3350, "stars": 5, "p": "07704445556"}
    ],
    "أعراض": {
        "ألم حاد ومفاجئ في الصدر": ("قلبية", "🚨 طوارئ: اشتباه ذبحة صدرية - توجه للمستشفى", 10),
        "ثقل في الكلام وخدر جانبي": ("جملة عصبية", "🚨 طوارئ: اشتباه سكتة دماغية", 10),
        "ضبابية مفاجئة في الرؤية": ("عيون", "🚨 طوارئ: احتمال انفصال شبكية", 10),
        "ألم بطن يمين حاد جداً": ("باطنية", "🚨 طوارئ: اشتباه زائدة دودية", 9),
        "ضيق تنفس حاد وازرقاق": ("باطنية", "🚨 طوارئ: فشل تنفسي", 10),
        "خفقان قلب سريع جداً": ("قلبية", "التشخيص: تسارع ضربات قلب", 7),
        "ألم مفاصل وتيبس صباحي": ("مفاصل", "التشخيص: التهاب مفاصل روماتزمي", 5),
        "طفح جلدي وحكة شديدة": ("جلدية", "التشخيص: حساسية جلدية حادة", 4),
        "عطش شديد وتبول متكرر": ("باطنية", "التشخيص: اضطراب سكر الدم", 5),
        "تنميل ووخز في الأطراف": ("جملة عصبية", "التشخيص: اعتلال أعصاب محيطية", 5),
        "بقع بيضاء في الجلد": ("جلدية", "التشخيص: اشتباه بهاق", 4),
        "تساقط شعر فراغي": ("جلدية", "التشخيص: داء الثعلبة", 4),
        "ألم أسفل الظهر مع الساق": ("مفاصل", "التشخيص: انزلاق غضروفي (دسك)", 5),
        "ألم حاد في العين مع احمرار": ("عيون", "التشخيص: التهاب القزحية", 8),
        "جفاف وحرقة في العين": ("عيون", "التشخيص: جفاف العين الإجهادي", 3),
        "صداع انفجاري مفاجئ": ("جملة عصبية", "🚨 طوارئ: احتمال نزف دماغي", 9),
        "حرقة معدة مستمرة": ("باطنية", "التشخيص: ارتجاع مريئي", 4),
        "تورم ساق واحدة وألم": ("باطنية", "🚨 طوارئ: احتمال جلطة وريدية", 8)
    }
}

if 'step' not in st.session_state: st.session_state.step = 1

def calculate_dist(lat1, lon1, lat2, lon2):
    return math.sqrt((lat1 - lat2)*2 + (lon1 - lon2)*2) * 111.13

# --- الصفحة 1: Welcome to AI Doctor 🩺 ---
if st.session_state.step == 1:
    st.markdown('<div class="welcome-title">Welcome to AI Doctor 🩺</div>', unsafe_allow_html=True)
    st.markdown('<div class="ai-warning">⚠️ نظام ذكاء اصطناعي للتحليل الفوري لمناطق بغداد كافة.</div>', unsafe_allow_html=True)
    with st.container():
        name = st.text_input("الأسم الكامل")
        u_area = st.selectbox("اختر منطقتك الحالية:", sorted(list(AREAS_COORDS.keys())))
        phone = st.text_input("رقم الهاتف")
        if st.button("دخول النظام"):
            if name and phone:
                st.session_state.p_data = {"name": name, "area": u_area, "phone": phone}
                # --- تكنيك الموقع GPS المحدث ---
                loc = get_geolocation()
                if loc and 'coords' in loc:
                    st.session_state.u_coords = (loc['coords']['latitude'], loc['coords']['longitude'])
                else:
                    st.session_state.u_coords = AREAS_COORDS[u_area]
                st.session_state.step = 2; st.rerun()

# --- الصفحة 2: ⛑️ Ai Dr. ---
elif st.session_state.step == 2:
    st.markdown('<div class="page-header">⛑️ Ai Dr.</div>', unsafe_allow_html=True)
    sels = st.multiselect("اختر الأعراض (يمكنك اختيار أكثر من عارض):", list(DATA["أعراض"].keys()))
    if sels:
        sorted_sels = sorted(sels, key=lambda x: DATA["أعراض"][x][2], reverse=True)
        top_symptom = sorted_sels[0]
        spec, diag, urg = DATA["أعراض"][top_symptom]
        st.session_state.selected_spec = spec
        
        box_class = "emergency-box" if urg >= 9 else "diag-box"
        st.markdown(f'<div class="{box_class}"><h4>🔍 التشخيص الفوري:</h4><p style="font-size:18px;">{diag}</p></div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ رجوع"): st.session_state.step = 1; st.rerun()
        with col2:
            if st.button("عرض الأطباء"): st.session_state.step = 3; st.rerun()

# --- الصفحة 3: Appointment ⏱️ ---
elif st.session_state.step == 3:
    st.markdown('<div class="page-header">Appointment ⏱️</div>', unsafe_allow_html=True)
    u_lat, u_lon = st.session_state.u_coords
    matches = [d for d in DATA["أطباء"] if d['s'] == st.session_state.selected_spec]
    for d in matches: d['d'] = calculate_dist(u_lat, u_lon, d['lat'], d['lon'])
    
    # الترتيب حسب الأقرب (مع مراعاة الحالة في حال الطوارئ)
    matches = sorted(matches, key=lambda x: x['d'])

    for d in matches:
        st.markdown(f'''
            <div class="doc-card">
                <span style="font-size:22px; color:#40E0D0;"><b>{d['n']}</b></span><br>
                <span style="color:#FFD700;">{"⭐" * d['stars']} | اختصاص {d['s']}</span><br>
                <span style="color:#40E0D0; font-size:14px;">📍 بغداد - {d['a']} (يبعد {d['d']:.1f} كم)</span>
            </div>
        ''', unsafe_allow_html=True)
        
        slots = {"03:00 PM": True, "04:30 PM": False, "06:00 PM": True, "07:30 PM": False, "09:00 PM": True}
        cols = st.columns(5)
        for i, (t_str, avail) in enumerate(slots.items()):
            with cols[i]:
                if avail:
                    if st.button(f"✅ {t_str}", key=f"b_{d['n']}_{t_str}"):
                        st.session_state.final = {"doc": d['n'], "time": t_str, "area": d['a'], "phone": d['p']}
                        st.session_state.step = 4; st.rerun()
                else:
                    st.button(f"🔒 {t_str}", key=f"l_{d['n']}_{t_str}", disabled=True)

    if st.button("⬅️ السابق"): st.session_state.step = 2; st.rerun()

# --- الصفحة 4: الرسالة النهائية ---
elif st.session_state.step == 4:
    f, p = st.session_state.final, st.session_state.p_data
    st.markdown(f'''
        <div class="success-card">
            <h1 style="color:#40E0D0;">Confirmed ✅</h1>
            <p style="font-size:18px;">السيد/ة <b>{p['name']}</b>، تم تثبيت موعدك بنجاح.</p>
            <div style="text-align:right; background:rgba(255,255,255,0.05); padding:20px; border-radius:15px; border:1px solid #333; margin:20px 0;">
                <p>👨‍⚕️ <b>الطبيب:</b> {f['doc']}</p>
                <p>⏰ <b>الموعد:</b> اليوم، {f['time']}</p>
                <p>📍 <b>العنوان:</b> بغداد - {f['area']}</p>
                <p>📞 <b>للتواصل:</b> <span style="color:#40E0D0;">{f['phone']}</span></p>
            </div>
            <span class="wish-safe">نتمنى لكم السلامة .. 💐</span>
        </div>
    ''', unsafe_allow_html=True)
    if st.button("حجز جديد"): st.session_state.step = 1; st.rerun()
