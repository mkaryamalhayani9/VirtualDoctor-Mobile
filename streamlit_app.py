import streamlit as st
import math
from streamlit_js_eval import get_geolocation

# --- 1. التنسيق المتطور وتوسيط العناصر ---
st.set_page_config(page_title="AI Doctor Baghdad", layout="centered")

st.markdown(r'''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&family=Playfair+Display:wght@700&display=swap');
    * { font-family: 'Tajawal', sans-serif; direction: rtl; text-align: center; }
    .stApp { background-color: #050505; color: #e0e0e0; }
    .welcome-title { font-family: 'Playfair Display', serif; font-size: 42px; color: #40E0D0; margin-bottom: 5px; }
    .ai-warning { background: rgba(255, 255, 255, 0.05); border: 1px solid #444; padding: 10px; border-radius: 10px; font-size: 12px; color: #888; margin-bottom: 20px; }
    
    .diag-box, .emergency-box { margin: 20px auto; max-width: 600px; padding: 25px; border-radius: 15px; }
    .diag-box { background: rgba(64, 224, 208, 0.05); border: 1px solid #40E0D0; }
    .emergency-box { background: rgba(255, 0, 0, 0.15); border: 2px solid #ff4b4b; box-shadow: 0 0 15px rgba(255, 75, 75, 0.3); }
    
    .doc-card { background-color: #0d0d0d; padding: 20px; border-radius: 15px; border: 1px solid #333; border-bottom: 4px solid #40E0D0; margin: 15px auto; max-width: 600px; }
    .slot-booked { background: #222 !important; color: #555 !important; border: 1px solid #333 !important; opacity: 0.5; cursor: not-allowed; }
    .wish-safe { color: #40E0D0; font-size: 26px; font-weight: bold; margin-top: 30px; display: block; }
    .success-card { border: 2px solid #40E0D0; border-radius: 20px; padding: 40px; max-width:600px; margin:auto; background: rgba(64, 224, 208, 0.02); }
    </style>
    ''', unsafe_allow_html=True)

# --- 2. قاعدة البيانات الشاملة (أطباء + 30 عارض مع الأولوية) ---
AREAS = ["المنصور", "الحارثية", "الكرادة", "الجادرية", "الأعظمية", "زيونة", "الدورة", "السيدية", "حي الجامعة", "العامرية", "الغزالية", "بغداد الجديدة", "الشعب", "البنوك", "الوزيرية", "الأمين", "الكاظمية", "الصليخ"]

DATA = {
    "أطباء": [
        {"n": "د. علي الركابي", "s": "قلبية", "desc": "استشاري قسطرة وأمراض قلب", "a": "الحارثية", "lat": 33.3222, "lon": 44.3585, "stars": 5, "p": "07701234567"},
        {"n": "د. سارة الجبوري", "s": "قلبية", "desc": "أخصائية سونار القلب", "a": "المنصور", "lat": 33.3251, "lon": 44.3482, "stars": 4, "p": "07801112223"},
        {"n": "د. محمد الزبيدي", "s": "قلبية", "desc": "جراحة القلب الصدري", "a": "الكرادة", "lat": 33.3135, "lon": 44.4291, "stars": 5, "p": "07902223334"},
        {"n": "د. عمر الخفاجي", "s": "جملة عصبية", "desc": "جراح دماغ وفقرات", "a": "الجادرية", "lat": 33.2801, "lon": 44.3905, "stars": 5, "p": "07705556667"},
        {"n": "د. مريم القيسي", "s": "مفاصل", "desc": "أخصائية الروماتزم", "a": "الكرادة", "lat": 33.3135, "lon": 44.4291, "stars": 5, "p": "07901231234"},
        {"n": "د. حسن الهاشمي", "s": "باطنية", "desc": "أخصائي هضمية وكبد", "a": "الأعظمية", "lat": 33.3652, "lon": 44.3751, "stars": 5, "p": "07801212123"}
    ],
    "أعراض": {
        "ألم حاد ومفاجئ في الصدر": ("قلبية", "🚨 طوارئ: اشتباه ذبحة صدرية", 10),
        "خفقان قلب سريع جداً": ("قلبية", "التشخيص: تسارع ضربات قلب", 7),
        "ثقل في الكلام وخدر جانبي": ("جملة عصبية", "🚨 طوارئ: اشتباه سكتة دماغية", 10),
        "صداع انفجاري مفاجئ": ("جملة عصبية", "🚨 طوارئ: احتمال نزف دماغي", 9),
        "ألم مفاصل وتيبس صباحي": ("مفاصل", "التشخيص: التهاب مفاصل روماتزمي", 5),
        "ألم بطن يمين حاد جداً": ("باطنية", "🚨 طوارئ: اشتباه زائدة دودية", 9),
        "ضيق تنفس حاد وازرقاق": ("باطنية", "🚨 طوارئ: فشل تنفسي", 10),
        "عطش شديد وتبول متكرر": ("باطنية", "التشخيص: اضطراب سكر الدم", 5),
        "خمول دائم ونعاس": ("باطنية", "التشخيص: خمول غدة درقية", 4),
        "طفح جلدي وحكة شديدة": ("جلدية", "التشخيص: حساسية جلدية حادة", 4),
        "تساقط شعر فراغي": ("جلدية", "التشخيص: داء الثعلبة", 4),
        "تنميل في الأطراف": ("جملة عصبية", "التشخيص: اعتلال أعصاب", 5),
        "دوار مستمر وطنين أذن": ("جملة عصبية", "التشخيص: اضطراب توازن", 5),
        "حرقة معدة تزداد ليلاً": ("باطنية", "التشخيص: ارتجاع مريئي", 4),
        "غازات وانتفاخ دائم": ("باطنية", "التشخيص: قولون عصبي", 4),
        "حرارة مرتفعة مستمرة": ("باطنية", "التشخيص: عدوى بكتيرية", 7),
        "ضعف عام وشحوب": ("باطنية", "التشخيص: فقر دم", 4),
        "رعشة في اليدين": ("جملة عصبية", "التشخيص: رعاش عصبي", 6),
        "سعال جاف مستمر": ("باطنية", "التشخيص: تحسس قصبي", 5),
        "ألم أذن حاد وإفرازات": ("باطنية", "التشخيص: التهاب أذن وسطى", 5),
        "نزف أنف متكرر": ("باطنية", "التشخيص: ضعف شعيرات", 6),
        "تورم ساق واحدة وألم": ("باطنية", "🚨 طوارئ: احتمال جلطة وريدية", 8),
        "تعرق ليلي شديد": ("باطنية", "التشخيص: يحتاج فحوصات شاملة", 7),
        "صداع مزمن خلف الرأس": ("جملة عصبية", "التشخيص: صداع توتري", 4),
        "ألم الفك عند المضغ": ("مفاصل", "التشخيص: اضطراب مفصل الفك", 4),
        "جفاف عين وحرقان": ("باطنية", "التشخيص: نقص دمع", 3),
        "نزيف لثة مستمر": ("باطنية", "التشخيص: التهاب لثة", 4),
        "فقدان توازن مفاجئ": ("جملة عصبية", "التشخيص: دوار وضعي", 6),
        "ألم أسفل الظهر مع الساق": ("مفاصل", "التشخيص: انزلاق غضروفي", 5),
        "اصفرار في العين والجلد": ("باطنية", "التشخيص: يرقان كبدي", 7)
    }
}

if 'step' not in st.session_state: st.session_state.step = 1

def calculate_dist(lat1, lon1, lat2, lon2):
    return math.sqrt((lat1 - lat2)*2 + (lon1 - lon2)*2) * 111.13

# --- الصفحة 1: الدخول ---
if st.session_state.step == 1:
    st.markdown('<div class="welcome-title">AI Doctor Baghdad 🩺</div>', unsafe_allow_html=True)
    st.markdown('<div class="ai-warning">⚠️ تنبيه: هذا النظام يعمل بالذكاء الاصطناعي للمساعدة الفورية، لا يعوض عن الفحص الطبي المباشر في الحالات الحرجة.</div>', unsafe_allow_html=True)
    with st.container():
        name = st.text_input("الأسم الكامل")
        u_area = st.selectbox("منطقتك في بغداد:", sorted(AREAS))
        phone = st.text_input("رقم الهاتف")
        if st.button("دخول النظام"):
            if name and phone:
                st.session_state.p_data = {"name": name, "area": u_area, "phone": phone}
                loc = get_geolocation()
                st.session_state.u_coords = (loc['coords']['latitude'], loc['coords']['longitude']) if loc and 'coords' in loc else (33.3152, 44.3661)
                st.session_state.step = 2; st.rerun()

# --- الصفحة 2: تشخيص الأعراض المتعددة ---
elif st.session_state.step == 2:
    st.markdown('<div class="welcome-title" style="font-size:35px;">تحليل الحالات ⛑️</div>', unsafe_allow_html=True)
    sels = st.multiselect("اختر كل ما تشعر به حالياً:", list(DATA["أعراض"].keys()))
    if sels:
        # حل مشكلة الـ IndexError بالتأكد من وجود العنصر الثالث
        sorted_sels = sorted(sels, key=lambda x: DATA["أعراض"][x][2], reverse=True)
        top_symptom = sorted_sels[0]
        spec, diag, urg = DATA["أعراض"][top_symptom]
        st.session_state.selected_spec = spec
        
        box_class = "emergency-box" if "🚨" in diag else "diag-box"
        st.markdown(f'<div class="{box_class}"><h4>🔍 التحليل الذكي للشكوى:</h4><p style="font-size:18px;">{diag}</p><small>التوجيه بناءً على العارض الأهم: {top_symptom}</small></div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ رجوع"): st.session_state.step = 1; st.rerun()
        with col2:
            if st.button("عرض الأطباء المرشحين"): st.session_state.step = 3; st.rerun()

# --- الصفحة 3: عرض أكثر من طبيب وحجوزات افتراضية ---
elif st.session_state.step == 3:
    st.markdown('<div class="welcome-title" style="font-size:28px;">الأطباء الأقرب لموقعك 📅</div>', unsafe_allow_html=True)
    u_lat, u_lon = st.session_state.u_coords
    matches = [d for d in DATA["أطباء"] if d['s'] == st.session_state.selected_spec]
    for d in matches: d['d'] = calculate_dist(u_lat, u_lon, d['lat'], d['lon'])
    
    for d in sorted(matches, key=lambda x: x['d']):
        st.markdown(f'''
            <div class="doc-card">
                <span style="font-size:22px; color:#40E0D0;"><b>{d['n']}</b></span><br>
                <span style="color:#FFD700;">{"⭐" * d['stars']} | اختصاص {d['s']}</span><br>
                <span style="color:#888; font-size:13px;">بغداد - {d['a']} (يبعد {d['d']:.1f} كم)</span>
            </div>
        ''', unsafe_allow_html=True)
        
        # توزيع المواعيد (3-9 مساءً) مع حالات "محجوز" افتراضية
        slots = {"03:00 PM": True, "04:30 PM": False, "06:00 PM": True, "07:30 PM": False, "09:00 PM": True}
        cols = st.columns(len(slots))
        for i, (t_str, avail) in enumerate(slots.items()):
            with cols[i]:
                if avail:
                    if st.button(f"✅ {t_str}", key=f"btn_{d['n']}_{t_str}"):
                        st.session_state.final = {"doc": d['n'], "time": t_str, "area": d['a'], "phone": d['p']}
                        st.session_state.step = 4; st.rerun()
                else:
                    st.button(f"🔒 {t_str}", key=f"lock_{d['n']}_{t_str}", disabled=True, help="محجوز مسبقاً")

    if st.button("⬅️ السابق"): st.session_state.step = 2; st.rerun()

# --- الصفحة 4: الرسالة النهائية المرتبة ---
elif st.session_state.step == 4:
    f, p = st.session_state.final, st.session_state.p_data
    st.markdown(f'''
        <div class="success-card">
            <h1 style="color:#40E0D0; margin-bottom:10px;">✅ تم تثبيت الموعد</h1>
            <p style="font-size:18px;">السيد/ة <b>{p['name']}</b>، تم حجز مقعدك بنجاح.</p>
            <hr style="border-color:#333;">
            <div style="text-align:right; padding:10px;">
                <p>👨‍⚕️ <b>الطبيب:</b> {f['doc']}</p>
                <p>⏰ <b>الموعد:</b> اليوم، {f['time']}</p>
                <p>📍 <b>العنوان:</b> عيادة بغداد - {f['area']}</p>
                <p>📞 <b>للتواصل:</b> <span style="color:#40E0D0; font-family:monospace;">{f['phone']}</span></p>
            </div>
            <hr style="border-color:#333;">
            <span class="wish-safe">نتمنى لكم السلامة .. 💐</span>
        </div>
    ''', unsafe_allow_html=True)
    if st.button("العودة للرئيسية"): st.session_state.step = 1; st.rerun()
