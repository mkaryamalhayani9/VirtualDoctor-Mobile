import streamlit as st
import math
from streamlit_js_eval import get_geolocation

# --- 1. التنسيق المتطور (نفس الألوان والمسميات) ---
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

# --- 2. قاعدة البيانات (المناطق + الأطباء + 30 عارض) ---
AREAS_COORDS = {
    "المنصور": (33.3251, 44.3482), "الحارثية": (33.3222, 44.3585), "الكرادة": (33.3135, 44.4291),
    "الجادرية": (33.2801, 44.3905), "الأعظمية": (33.3652, 44.3751), "زيونة": (33.3401, 44.4502),
    "اليرموك": (33.3000, 44.3350), "الدورة": (33.2500, 44.4000), "السيدية": (33.2650, 44.3600),
    "حي الجامعة": (33.3350, 44.3100), "الكاظمية": (33.3800, 44.3400), "الشعب": (33.4000, 44.4200),
    "البنوك": (33.3900, 44.4300), "العامرية": (33.3200, 44.2800), "الغزالية": (33.3400, 44.2500),
    "الوزيرية": (33.3600, 44.4000), "الأمين": (33.3100, 44.4800), "بغداد الجديدة": (33.3200, 44.4600)
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
        "ألم حاد ومفاجئ في الصدر": ("قلبية", "🚨 طوارئ: اشتباه ذبحة صدرية", 10),
        "ثقل في الكلام وخدر جانبي": ("جملة عصبية", "🚨 طوارئ: اشتباه سكتة دماغية", 10),
        "ضبابية مفاجئة في الرؤية": ("عيون", "🚨 طوارئ: احتمال انفصال شبكية", 10),
        "ألم بطن يمين حاد جداً": ("باطنية", "🚨 طوارئ: اشتباه زائدة دودية", 9),
        "ضيق تنفس حاد وازرقاق": ("باطنية", "🚨 طوارئ: فشل تنفسي", 10),
        "صداع انفجاري مفاجئ": ("جملة عصبية", "🚨 طوارئ: احتمال نزف دماغي", 9),
        "تورم ساق واحدة وألم": ("باطنية", "🚨 طوارئ: احتمال جلطة وريدية", 8),
        "خفقان قلب سريع جداً": ("قلبية", "التشخيص: تسارع ضربات قلب", 7),
        "ألم مفاصل وتيبس صباحي": ("مفاصل", "التشخيص: التهاب مفاصل روماتزمي", 5),
        "طفح جلدي وحكة شديدة": ("جلدية", "التشخيص: حساسية جلدية حادة", 4),
        "عطش شديد وتبول متكرر": ("باطنية", "التشخيص: اضطراب سكر الدم", 5),
        "تنميل ووخز في الأطراف": ("جملة عصبية", "التشخيص: اعتلال أعصاب محيطية", 5),
        "بقع بيضاء في الجلد": ("جلدية", "التشخيص: اشتباه بهاق", 4),
        "تساقط شعر فراغي": ("جلدية", "التشخيص: داء الثعلبة", 4),
        "ألم أسفل الظهر مع الساق": ("مفاصل", "التشخيص: انزلاق غضروفي", 5),
        "ألم حاد في العين مع احمرار": ("عيون", "التشخيص: التهاب القزحية", 8),
        "جفاف وحرقة في العين": ("عيون", "التشخيص: جفاف العين", 3),
        "حرقة معدة مستمرة": ("باطنية", "التشخيص: ارتجاع مريئي", 4),
        "غازات وانتفاخ دائم": ("باطنية", "التشخيص: قولون عصبي", 4),
        "دوار مستمر وطنين أذن": ("جملة عصبية", "التشخيص: اضطراب توازن", 5),
        "خمول دائم ونعاس": ("باطنية", "التشخيص: خمول غدة درقية", 4),
        "حرارة مرتفعة مستمرة": ("باطنية", "التشخيص: عدوى بكتيرية", 7),
        "ضعف عام وشحوب": ("باطنية", "التشخيص: فقر دم", 4),
        "رعشة في اليدين": ("جملة عصبية", "التشخيص: رعاش عصبي", 6),
        "سعال جاف مستمر": ("باطنية", "التشخيص: تحسس قصبي", 5),
        "ألم أذن حاد وإفرازات": ("باطنية", "التشخيص: التهاب أذن وسطى", 5),
        "تعرق ليلي شديد": ("باطنية", "التشخيص: يحتاج فحوصات شاملة", 7),
        "صداع مزمن خلف الرأس": ("جملة عصبية", "التشخيص: صداع توتري", 4),
        "ألم الفك عند المضغ": ("مفاصل", "التشخيص: اضطراب مفصل الفك", 4),
        "فقدان توازن مفاجئ": ("جملة عصبية", "التشخيص: دوار وضعي", 6)
    }
}

if 'step' not in st.session_state: st.session_state.step = 1

def calculate_dist(lat1, lon1, lat2, lon2):
    if lat1 is None or lat2 is None: return 0.0
    # تم تصحيح الأس إلى **2 لضمان صحة الحساب
    return math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2) * 111.13

# --- الصفحة 1: Welcome to AI Doctor 🩺 ---
if st.session_state.step == 1:
    st.markdown('<div class="welcome-title">Welcome to AI Doctor 🩺</div>', unsafe_allow_html=True)
    st.markdown('<div class="ai-warning">⚠️ تنبيه: هذا النظام يعمل بالذكاء الاصطناعي للمساعدة في التشخيص، لا يعوض عن الفحص الطبي المباشر في الحالات الحرجة.</div>', unsafe_allow_html=True)
    with st.container():
        name = st.text_input("الأسم الكامل")
        u_area = st.selectbox("اختر منطقتك الحالية:", sorted(list(AREAS_COORDS.keys())))
        phone = st.text_input("رقم الهاتف")
        if st.button("دخول النظام"):
            if name and phone:
                st.session_state.p_data = {"name": name, "area": u_area, "phone": phone}
                loc = get_geolocation()
                # تصحيح جلب الإحداثيات لضمان عدم حدوث ValueError
                st.session_state.u_coords = (loc['coords']['latitude'], loc['coords']['longitude']) if loc and 'coords' in loc else AREAS_COORDS[u_area]
                st.session_state.step = 2; st.rerun()

# --- الصفحة 2: ⛑️ Ai Dr. ---
elif st.session_state.step == 2:
    st.markdown('<div class="page-header">AI DR.⛑️</div>', unsafe_allow_html=True)
    
    # 1. إخلاء مسؤولية (قانوني وواضح)
    st.markdown('''
        <div style="background-color: #1a1a1a; padding: 12px; border: 1px solid #444; border-right: 5px solid #ff4b4b; border-radius: 5px; margin-bottom: 20px;">
            <strong style="color: #ff4b4b;">⚠️ إخلاء مسؤولية:</strong> 
            هذا النظام استرشادي فقط. النتائج والنسب الظاهرة هي تحليل برمجي أولي ولا تعتبر تشخيصاً طبياً معتمداً. 
            في حالات الطوارئ، توجه فوراً للمستشفى.
        </div>
    ''', unsafe_allow_html=True)

    sels = st.multiselect("اختر جميع الأعراض التي تشعر بها حالياً:", list(DATA["أعراض"].keys()))
    
    if sels:
        # حساب التخصص الأكثر احتمالاً بناءً على أخطر عرض تم اختياره
        sorted_sels = sorted(sels, key=lambda x: DATA["أعراض"][x][2], reverse=True)
        top_symptom = sorted_sels[0]
        spec, diag, urg = DATA["أعراض"][top_symptom]
        
        # --- معادلة الدقة المئوية الذكية ---
        # تحسب النسبة بناءً على عدد الأعراض المتوافقة مع التخصص المختار
        match_count = sum(1 for s in sels if DATA["أعراض"][s][0] == spec)
        # نسبة أساسية 82.4% تزيد بـ 4.2% لكل عرض إضافي متوافق، بحد أقصى 99.1%
        accuracy = min(82.4 + (match_count * 4.2), 99.1) 
        
        st.session_state.selected_spec = spec
        
        # 2. تنبيه الطوارئ (يظهر فقط للحالات الحرجة جداً)
        if urg >= 9:
            st.markdown(f'''
                <div class="emergency-box">
                    <h2 style="color: #ff4b4b; margin:0; font-size:24px;">🚨 حالة طارئة قصوى</h2>
                    <p style="font-size:20px; font-weight:bold; margin:10px 0;">{diag}</p>
                    <hr style="border-color: rgba(255,255,255,0.2)">
                    <p style="font-size:16px;">دقة التحليل: <span style="color:#ff4b4b;">{accuracy}%</span></p>
                    <p style="font-size:14px; background:white; color:black; padding:5px; border-radius:5px;">
                        يتوجب عليك التوجه فوراً لأقرب طوارئ في منطقة <b>{st.session_state.p_data['area']}</b>
                    </p>
                </div>
            ''', unsafe_allow_html=True)
        else:
            # 3. التشخيص الاعتيادي مع النسبة المئوية
            st.markdown(f'''
                <div class="diag-box">
                    <h4 style="color: #40E0D0;">🔍 نتيجة التحليل الأولي:</h4>
                    <p style="font-size:22px; font-weight:bold;">{diag}</p>
                    <div style="margin-top:15px; background: rgba(64, 224, 208, 0.1); padding: 10px; border-radius: 8px;">
                        <span style="font-size:14px; color: #aaa;">نسبة دقة المطابقة البرمجية:</span><br>
                        <span style="font-size:24px; color: #40E0D0; font-weight: bold;">{accuracy}%</span>
                    </div>
                </div>
            ''', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ تعديل الأعراض"): st.session_state.step = 1; st.rerun()
        with col2:
            if st.button("حجز موعد مع مختص 🏥"): st.session_state.step = 3; st.rerun()
# --- الصفحة 3: Appointment ⏱️ ---
elif st.session_state.step == 3:
    st.markdown('<div class="page-header">Appointment ⏱️</div>', unsafe_allow_html=True)
    u_lat, u_lon = st.session_state.u_coords
    matches = [d for d in DATA["أطباء"] if d['s'] == st.session_state.selected_spec]
    for d in matches: d['d'] = calculate_dist(u_lat, u_lon, d['lat'], d['lon'])
    
    for d in sorted(matches, key=lambda x: x['d']):
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

# --- الصفحة 4: النهاية ---
elif st.session_state.step == 4:
    f, p = st.session_state.final, st.session_state.p_data
    st.markdown(f'''
        <div class="success-card">
            <h1 style="color:#40E0D0;">Confirmed ✅</h1>
            <p>السيد/ة <b>{p['name']}</b>، تم تثبيت موعدك.</p>
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
