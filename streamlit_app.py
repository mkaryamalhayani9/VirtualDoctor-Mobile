import streamlit as st
import math
from streamlit_js_eval import get_geolocation

# --- 1. التصميم وضبط الاتجاهات ---
st.set_page_config(page_title="AI Doctor 🩺", layout="wide")

st.markdown(r'''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&family=Orbitron:wght@700&display=swap');
    
    /* ضبط الاتجاه العام */
    .stApp { direction: rtl; text-align: right; background-color: #050505; color: #e0e0e0; font-family: 'Tajawal', sans-serif; }
    
    /* إجبار القوائم والمدخلات على اليمين */
    div[data-baseweb="select"] > div { direction: rtl !important; text-align: right !important; }
    div[role="listbox"] { direction: rtl !important; text-align: right !important; }
    input { direction: rtl !important; text-align: right !important; }

    .welcome-header { 
        font-family: 'Orbitron', sans-serif; color: #40E0D0; text-align: center; 
        font-size: 45px; padding: 25px; text-shadow: 0 0 15px rgba(64,224,208,0.4);
        direction: ltr;
    }

    .doc-card { background: #0d0d0d; padding: 20px; border-radius: 15px; border-right: 8px solid #40E0D0; margin-bottom: 12px; }
    .star-rating { color: #FFD700; font-size: 16px; margin-bottom: 5px; }
    .time-badge { display: inline-block; padding: 4px 10px; background: #1d4e4a; border-radius: 6px; margin: 3px; color: #40E0D0; font-size: 12px; }
    
    .stButton>button { 
        background: linear-gradient(135deg, #1d4e4a 0%, #40E0D0 100%) !important; 
        color: #000 !important; font-weight: bold; border-radius: 10px; height: 45px; width: 100%; border: none;
    }
    
    .emergency-glow {
        background: rgba(255, 0, 0, 0.1); color: #ff4b4b; padding: 20px; border-radius: 15px;
        text-align: center; font-weight: bold; border: 2px solid #ff4b4b; animation: pulse 2s infinite;
    }
    @keyframes pulse { 0% { opacity: 0.8; } 100% { opacity: 1; } }
    </style>
    ''', unsafe_allow_html=True)

# --- 2. قاعدة البيانات (30 عارضاً وأطباء مكررين) ---
DB = {
    "أطباء": [
        # قلبية
        {"n": "د. علي الركابي", "s": "قلبية", "a": "الحارثية", "lat": 33.322, "lon": 44.358, "t": ["09:00 ص", "11:00 ص"], "r": 5},
        {"n": "د. سارة الوائلي", "s": "قلبية", "a": "المنصور", "lat": 33.324, "lon": 44.340, "t": ["04:00 م", "08:00 م"], "r": 4},
        {"n": "د. حسن القلبي", "s": "قلبية", "a": "الكرادة", "lat": 33.310, "lon": 44.420, "t": ["10:00 ص", "01:00 م"], "r": 5},
        # أعصاب
        {"n": "د. عمر الجبوري", "s": "أعصاب", "a": "المنصور", "lat": 33.325, "lon": 44.348, "t": ["10:00 ص", "01:00 م"], "r": 5},
        {"n": "د. حيدر القزويني", "s": "أعصاب", "a": "الحارثية", "lat": 33.321, "lon": 44.357, "t": ["05:00 م", "09:00 م"], "r": 4},
        {"n": "د. مريم العصب", "s": "أعصاب", "a": "الجادرية", "lat": 33.280, "lon": 44.395, "t": ["11:00 ص", "02:00 م"], "r": 5},
        # باطنية
        {"n": "د. مصطفى كمال", "s": "باطنية", "a": "اليرموك", "lat": 33.300, "lon": 44.330, "t": ["01:00 م", "05:00 م"], "r": 4},
        {"n": "د. زينب الباطن", "s": "باطنية", "a": "زيونة", "lat": 33.330, "lon": 44.450, "t": ["09:00 ص", "12:00 م"], "r": 5},
        {"n": "د. سامر الهضم", "s": "باطنية", "a": "الدورة", "lat": 33.250, "lon": 44.380, "t": ["03:00 م", "06:00 م"], "r": 4},
        # عيون
        {"n": "د. ليلى الشمري", "s": "عيون", "a": "الجادرية", "lat": 33.280, "lon": 44.390, "t": ["03:00 م", "06:00 م"], "r": 5},
        {"n": "د. أحمد البصري", "s": "عيون", "a": "المنصور", "lat": 33.326, "lon": 44.342, "t": ["09:00 ص", "12:00 م"], "r": 4},
        # جلدية
        {"n": "د. نورا الجلد", "s": "جلدية", "a": "المنصور", "lat": 33.328, "lon": 44.345, "t": ["10:00 ص", "01:00 م"], "r": 5},
        {"n": "د. وليد الحساسية", "s": "جلدية", "a": "الكرادة", "lat": 33.315, "lon": 44.425, "t": ["04:00 م", "08:00 م"], "r": 4}
    ],
    "أعراض": {
        "ألم صدر حاد ومفاجئ": ("قلبية", 10, "🚨 اشتباه ذبحة صدرية - طوارئ فورية"),
        "ثقل مفاجئ في الكلام": ("أعصاب", 10, "🚨 اشتباه سكتة دماغية - طوارئ فورية"),
        "خفقان قلب سريع": ("قلبية", 7, "تشخيص: اضطراب في نظم القلب"),
        "صداع نصفي شديد": ("أعصاب", 5, "تشخيص: نوبة شقيقة حادة"),
        "اصفرار العين والجلد": ("باطنية", 8, "تشخيص: اضطراب وظائف الكبد"),
        "ضيق تنفس مستمر": ("باطنية", 9, "تشخيص: أزمة تنفسية حادة"),
        "دوار وفقدان توازن": ("أعصاب", 7, "تشخيص: اضطراب الأذن الداخلية"),
        "حرقة معدة مزمنة": ("باطنية", 4, "تشخيص: ارتجاع مريئي"),
        "ألم حاد في المفاصل": ("باطنية", 5, "تشخيص: التهاب مفاصل روماتزمي"),
        "طفح جلدي مفاجئ": ("جلدية", 4, "تشخيص: تحسس جلدي حاد"),
        "رؤية مشوشة (زغلولة)": ("عيون", 6, "تشخيص: إجهاد بصري شديد"),
        "تساقط شعر حاد": ("جلدية", 3, "تشخيص: تساقط أندروجيني أو نقص فيتامينات"),
        "ألم أسفل الظهر": ("باطنية", 5, "تشخيص: تشنج عضلي أو كلى"),
        "تنميل في الأطراف": ("أعصاب", 6, "تشخيص: اعتلال أعصاب طرفية"),
        "سعال جاف ومستمر": ("باطنية", 5, "تشخيص: تهيج في القصبات"),
        "نزيف من الأنف": ("باطنية", 6, "تشخيص: جفاف أو ضغط دم"),
        "انتفاخ في القدمين": ("قلبية", 7, "تشخيص: احتباس سوائل"),
        "ألم في الأذن": ("أعصاب", 4, "تشخيص: التهاب أذن وسطى"),
        "جفاف العين": ("عيون", 3, "تشخيص: متلازمة العين الجافة"),
        "رعشة في اليدين": ("أعصاب", 5, "تشخيص: إجهاد عصبي"),
        "قشرة رأس حادة": ("جلدية", 2, "تشخيص: فطريات فروة الرأس"),
        "غازات وانتفاخ معدة": ("باطنية", 3, "تشخيص: قولون عصبي"),
        "صعوبة في البلع": ("باطنية", 7, "تشخيص: تشنج مريئي"),
        "بقع بيضاء على الجلد": ("جلدية", 5, "تشخيص: نقص صبغة أو فطريات"),
        "خدر في الوجه": ("أعصاب", 8, "تشخيص: عصب سابع"),
        "ألم خلف العين": ("عيون", 5, "تشخيص: ضغط عين أو جيوب"),
        "تعرق ليلي مفرط": ("باطنية", 6, "تشخيص: اضطراب هرموني"),
        "ألم عند التنفس": ("قلبية", 8, "تشخيص: التهاب غشاء القلب"),
        "هشاشة أظافر": ("باطنية", 2, "تشخيص: نقص معادن"),
        "تشنج عضلي ليلي": ("باطنية", 4, "تشخيص: نقص مغنيسيوم")
    }
}

if "pg" not in st.session_state: st.session_state.pg = "login"

st.markdown('<div class="welcome-header">Welcome to AI Doctor 🩺</div>', unsafe_allow_html=True)

if st.session_state.pg == "login":
    st.markdown('<div style="max-width:500px; margin:auto; background:#0d0d0d; padding:35px; border-radius:20px; border:1px solid #40E0D0;">', unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:right;'>تسجيل الدخول</h3>", unsafe_allow_html=True)
    u_name = st.text_input("الأسم الكامل")
    u_age = st.number_input("العمر", 1, 110, 25)
    if st.button("دخول "):
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

        lat, lon = 33.315, 44.366 # الموقع الافتراضي
        if u_loc and 'coords' in u_loc:
            c_lat, c_lon = u_loc['coords'].get('latitude'), u_loc['coords'].get('longitude')
            if c_lat and c_lon: lat, lon = c_lat, c_lon
        
        matches = [d for d in DB["أطباء"] if d['s'] == spec]
        if matches:
            for d in matches: d['dist'] = round(math.sqrt((lat - d['lat'])*2 + (lon - d['lon'])*2) * 111, 1)
            matches = sorted(matches, key=lambda x: x['dist'])
            
            st.subheader(f"📍 الأطباء القريبين منك:")
            for d in matches:
                with st.container():
                    stars = "★" * d['r'] + "☆" * (5 - d['r'])
                    st.markdown(f'''<div class="doc-card">
                        <div class="star-rating">{stars}</div>
                        <span style="color:#40E0D0; font-size:20px; font-weight:bold;">{d['n']}</span>
                        <p>📍 {d['a']} | 📏 يبعد عنك {d['dist']} كم</p>
                        <div> المواعيد: {''.join([f'<span class="time-badge">{t}</span>' for t in d['t']])}</div>
                    </div>''', unsafe_allow_html=True)
                    if st.button(f"تأكيد الحجز عند {d['n']}", key=f"bk_{d['n']}"):
                        st.session_state.dn, st.session_state.da, st.session_state.pg = d['n'], d['a'], "success"
                        st.rerun()

elif st.session_state.pg == "success":
    st.markdown(f'''
        <div style="text-align:center; padding:50px; border:2px solid #40E0D0; border-radius:25px; background:#0d0d0d; margin-top:30px;">
            <h1 style="color:#40E0D0;">✅ تم الحجز بنجاح</h1>
            <p style="font-size:20px; margin-top:15px;">عزيزي <b>{st.session_state.u_name}</b>، تم تأكيد موعدك بنجاح.</p>
            <div style="background:#1a1a1a; padding:20px; border-radius:15px; margin: 20px auto; width: fit-content;">
                <p style="font-size:18px;">الطبيب: <b>{st.session_state.dn}</b></p>
                <p style="font-size:18px;">المنطقة: <b>{st.session_state.da}</b></p>
            </div>
            <p style="color:#888;">يرجى الالتزام بالموعد المحدد.</p>
        </div>
    ''', unsafe_allow_html=True)
    if st.button("العودة للفحص"):
        st.session_state.pg = "main"
        st.rerun()
