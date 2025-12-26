import streamlit as st
import math
from streamlit_js_eval import get_geolocation

# --- 1. التنسيق البصري الفخم وضبط الاتجاهات ---
st.set_page_config(page_title="AI Doctor 🩺", layout="wide")

st.markdown(r'''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&family=Orbitron:wght@700&display=swap');
    .stApp { direction: rtl; text-align: right; background-color: #050505; color: #e0e0e0; font-family: 'Tajawal', sans-serif; }
    div[data-baseweb="select"] > div { direction: rtl !important; text-align: right !important; }
    div[role="listbox"] { direction: rtl !important; text-align: right !important; }
    .welcome-header { font-family: 'Orbitron', sans-serif; color: #40E0D0; text-align: center; font-size: 35px; padding: 20px; direction: ltr; }
    .doc-card { background: #0d0d0d; padding: 20px; border-radius: 15px; border-right: 8px solid #40E0D0; margin-bottom: 12px; }
    .star-rating { color: #FFD700; font-size: 16px; margin-bottom: 5px; }
    .time-badge { display: inline-block; padding: 4px 10px; background: #1d4e4a; border-radius: 6px; margin: 3px; color: #40E0D0; font-size: 12px; }
    .stButton>button { background: linear-gradient(135deg, #1d4e4a 0%, #40E0D0 100%) !important; color: #000 !important; font-weight: bold; border-radius: 10px; width: 100%; border: none; }
    .emergency-glow { background: rgba(255, 0, 0, 0.15); color: #ff4b4b; padding: 20px; border-radius: 15px; text-align: center; font-weight: bold; border: 2px solid #ff4b4b; animation: pulse 2s infinite; }
    @keyframes pulse { 0% { opacity: 0.8; } 100% { opacity: 1; } }
    .disclaimer { background: #1a1a1a; padding: 15px; border-radius: 10px; border: 1px solid #333; font-size: 13px; color: #888; margin-top: 20px; }
    </style>
    ''', unsafe_allow_html=True)

# --- 2. قاعدة البيانات (30 عارضاً وأطباء مكررين) ---
DB = {
    "أطباء": [
        {"n": "د. علي الركابي", "s": "قلبية", "a": "الحارثية", "lat": 33.322, "lon": 44.358, "t": ["09:00 ص", "11:00 ص"], "r": 5},
        {"n": "د. سارة الوائلي", "s": "قلبية", "a": "المنصور", "lat": 33.324, "lon": 44.340, "t": ["04:00 م", "08:00 م"], "r": 4},
        {"n": "د. حسن القلبي", "s": "قلبية", "a": "الكرادة", "lat": 33.310, "lon": 44.420, "t": ["10:00 ص", "01:00 م"], "r": 5},
        {"n": "د. عمر الجبوري", "s": "أعصاب", "a": "المنصور", "lat": 33.325, "lon": 44.348, "t": ["10:00 ص", "01:00 م"], "r": 5},
        {"n": "د. حيدر القزويني", "s": "أعصاب", "a": "الحارثية", "lat": 33.321, "lon": 44.357, "t": ["05:00 م", "09:00 م"], "r": 4},
        {"n": "د. مريم العصب", "s": "أعصاب", "a": "الجادرية", "lat": 33.280, "lon": 44.395, "t": ["11:00 ص", "02:00 م"], "r": 5},
        {"n": "د. زينب الباطن", "s": "باطنية", "a": "زيونة", "lat": 33.330, "lon": 44.450, "t": ["09:00 ص", "12:00 م"], "r": 5},
        {"n": "د. سامر الهضم", "s": "باطنية", "a": "الدورة", "lat": 33.250, "lon": 44.380, "t": ["03:00 م", "06:00 م"], "r": 4}
    ],
    "أعراض": {
        "ألم صدر حاد ومفاجئ": ("قلبية", 10, "🚨 تنبيه طوارئ: اشتباه ذبحة صدرية - اتصل بالإسعاف فوراً"),
        "ثقل مفاجئ في الكلام": ("أعصاب", 10, "🚨 تنبيه طوارئ: اشتباه سكتة دماغية - توجه لأقرب مستشفى"),
        "ضيق تنفس مستمر": ("باطنية", 9, "🚨 تنبيه: أزمة تنفسية حادة تحتاج فحص فوري"),
        "خفقان قلب سريع": ("قلبية", 7, "تشخيص الذكاء: اضطراب في نظم القلب"),
        "صداع نصفي شديد": ("أعصاب", 5, "تشخيص الذكاء: نوبة شقيقة حادة"),
        "اصفرار العين والجلد": ("باطنية", 8, "تشخيص الذكاء: اضطراب وظائف الكبد"),
        "دوار وفقدان توازن": ("أعصاب", 7, "تشخيص الذكاء: اضطراب الأذن الداخلية"),
        "حرقة معدة مزمنة": ("باطنية", 4, "تشخيص الذكاء: ارتجاع مريئي"),
        "ألم حاد في المفاصل": ("باطنية", 5, "تشخيص الذكاء: التهاب مفاصل"),
        "طفح جلدي وحكة": ("باطنية", 4, "تشخيص الذكاء: تحسس جلدي"),
        "رؤية مشوشة": ("باطنية", 6, "تشخيص الذكاء: إجهاد بصري شديد"),
        "تنميل في الأطراف": ("أعصاب", 6, "تشخيص الذكاء: اعتلال أعصاب طرفية"),
        "ألم أسفل الظهر": ("باطنية", 5, "تشخيص الذكاء: تشنج عضلي أو كلى"),
        "سعال جاف ومستمر": ("باطنية", 5, "تشخيص الذكاء: تهيج في القصبات"),
        "نزيف من الأنف": ("باطنية", 6, "تشخيص الذكاء: جفاف أو ضغط دم"),
        "انتفاخ في القدمين": ("قلبية", 7, "تشخيص الذكاء: احتباس سوائل"),
        "رعشة في اليدين": ("أعصاب", 5, "تشخيص الذكاء: إجهاد عصبي"),
        "قشرة رأس حادة": ("باطنية", 2, "تشخيص الذكاء: فطريات فروة الرأس"),
        "غازات وانتفاخ": ("باطنية", 3, "تشخيص الذكاء: قولون عصبي"),
        "صعوبة في البلع": ("باطنية", 7, "تشخيص الذكاء: تشنج مريئي"),
        "بقع بيضاء": ("باطنية", 5, "تشخيص الذكاء: نقص صبغة"),
        "خدر في الوجه": ("أعصاب", 8, "تشخيص الذكاء: عصب سابع"),
        "ألم خلف العين": ("باطنية", 5, "تشخيص الذكاء: ضغط عين"),
        "تعرق ليلي": ("باطنية", 6, "تشخيص الذكاء: اضطراب هرموني"),
        "ألم عند التنفس": ("قلبية", 8, "تشخيص الذكاء: التهاب غشاء القلب"),
        "هشاشة أظافر": ("باطنية", 2, "تشخيص الذكاء: نقص معادن"),
        "تشنج عضلي ليلي": ("باطنية", 4, "تشخيص الذكاء: نقص مغنيسيوم"),
        "طنين في الأذن": ("أعصاب", 4, "تشخيص الذكاء: اضطراب سمعي"),
        "عطش مفرط": ("باطنية", 7, "تشخيص الذكاء: اشتباه سكر"),
        "تعب عام وخمول": ("باطنية", 3, "تشخيص الذكاء: نقص فيتامينات")
    }
}

if "pg" not in st.session_state: st.session_state.pg = "login"

st.markdown('<div class="welcome-header">AI Doctor System 🩺</div>', unsafe_allow_html=True)

if st.session_state.pg == "login":
    st.markdown('<div style="max-width:500px; margin:auto; background:#0d0d0d; padding:30px; border-radius:20px; border:1px solid #40E0D0;">', unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:right;'>تسجيل الدخول</h3>", unsafe_allow_html=True)
    u_name = st.text_input("الأسم الكامل")
    u_age = st.number_input("العمر", 1, 110, 25)
    if st.button("دخول للنظام"):
        if u_name:
            st.session_state.u_name, st.session_state.u_age, st.session_state.pg = u_name, u_age, "main"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.pg == "main":
    u_loc = get_geolocation()
    st.write(f"المريض: *{st.session_state.u_name}* | العمر: *{st.session_state.u_age}*")
    sel = st.selectbox("بماذا تشعر الآن؟", ["اختر العارض..."] + list(DB["أعراض"].keys()))

    if sel != "اختر العارض...":
        spec, urg, diag = DB["أعراض"][sel]
        if urg >= 9: st.markdown(f'<div class="emergency-glow">{diag}</div>', unsafe_allow_html=True)
        else: st.success(f"🤖 {diag}")

        # نظام حماية الموقع لمنع الانهيار (ValueError)
        lat, lon = 33.315, 44.366 
        loc_available = False
        try:
            if u_loc and 'coords' in u_loc:
                c_lat, c_lon = u_loc['coords'].get('latitude'), u_loc['coords'].get('longitude')
                if c_lat and c_lon: lat, lon, loc_available = c_lat, c_lon, True
        except: pass 
        
        matches = [d for d in DB["أطباء"] if d['s'] == spec]
        if matches:
            for d in matches:
                try: d['dist'] = round(math.sqrt((lat - d['lat'])*2 + (lon - d['lon'])*2) * 111, 1)
                except: d['dist'] = 0.0
            
            matches = sorted(matches, key=lambda x: x['dist'])
            st.subheader(f"📍 الأطباء القريبين منك (أكثر من خيار):")
            for d in matches:
                with st.container():
                    stars = "★" * d['r'] + "☆" * (5 - d['r'])
                    dist_txt = f"{d['dist']} كم" if loc_available else "غير محدد"
                    st.markdown(f'''<div class="doc-card">
                        <div class="star-rating">{stars}</div>
                        <span style="color:#40E0D0; font-size:20px; font-weight:bold;">{d['n']}</span>
                        <p>📍 {d['a']} | 📏 المسافة: {dist_txt}</p>
                        <div> المواعيد: {''.join([f'<span class="time-badge">{t}</span>' for t in d['t']])}</div>
                    </div>''', unsafe_allow_html=True)
                    if st.button(f"تأكيد الحجز عند {d['n']}", key=f"bk_{d['n']}"):
                        st.session_state.dn, st.session_state.da, st.session_state.pg = d['n'], d['a'], "success"
                        st.rerun()

    st.markdown('<div class="disclaimer">⚠️ إخلاء مسؤولية: هذا النظام يعتمد على الذكاء الاصطناعي لتسهيل الوصول للأطباء ولا يغني عن الاستشارة الطبية المباشرة في الحالات الحرجة.</div>', unsafe_allow_html=True)

elif st.session_state.pg == "success":
    st.markdown(f'''
        <div style="text-align:center; padding:50px; border:2px solid #40E0D0; border-radius:25px; background:#0d0d0d; margin-top:30px;">
            <h1 style="color:#40E0D0;">✅ تم الحجز بنجاح</h1>
            <p style="font-size:20px;">تم تأكيد الموعد بنجاح لـ <b>{st.session_state.u_name}</b>.</p>
            <div style="background:#1a1a1a; padding:20px; border-radius:15px; margin: 20px auto; width: fit-content;">
                <p>الطبيب: <b>{st.session_state.dn}</b> | المكان: <b>{st.session_state.da}</b></p>
            </div>
        </div>
    ''', unsafe_allow_html=True)
    if st.button("العودة للفحص"):
        st.session_state.pg = "main"
        st.rerun()
