import streamlit as st
import math
from streamlit_js_eval import get_geolocation

# --- 1. الإعدادات والتنسيق (فيروزي وأسود) ---
st.set_page_config(page_title="AI Doctor Baghdad", layout="centered")

st.markdown(r'''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&family=Playfair+Display:wght@700&display=swap');
    * { font-family: 'Tajawal', sans-serif; direction: rtl; }
    .stApp { background-color: #050505; color: #e0e0e0; }
    .welcome-title { font-family: 'Playfair Display', serif; font-size: 42px; text-align: center; color: #40E0D0; margin-bottom: 5px; }
    .welcome-sub { text-align: center; color: #40E0D0; font-size: 12px; margin-bottom: 40px; letter-spacing: 3px; opacity: 0.7; }
    .slot-box { padding: 12px; text-align: center; border-radius: 8px; font-weight: bold; font-size: 14px; margin-bottom: 10px; }
    .slot-booked { background: rgba(255, 255, 255, 0.05); border: 1px solid #333; color: #555; }
    .doc-card { background-color: #0d0d0d; padding: 20px; border-radius: 15px; border-right: 8px solid #40E0D0; border: 1px solid #333; margin-bottom: 15px; }
    .disclaimer-card { background: rgba(255, 0, 0, 0.05); border: 1px solid #ff4b4b; padding: 15px; border-radius: 10px; color: #ff4b4b; text-align: center; margin: 20px 0; }
    .stButton>button { background-color: transparent; color: #40E0D0 !important; border: 1px solid #40E0D0 !important; border-radius: 8px; width: 100%; transition: 0.3s; }
    .stButton>button:hover { background-color: #40E0D0 !important; color: #000 !important; }
    </style>
    ''', unsafe_allow_html=True)

# --- 2. قاعدة البيانات ---
AREAS = {
    "المنصور": (33.3251, 44.3482), "الحارثية": (33.3222, 44.3585), "الكرادة": (33.3135, 44.4291),
    "الجادرية": (33.2801, 44.3905), "الأعظمية": (33.3652, 44.3751), "زيونة": (33.3401, 44.4502)
}

DATA = {
    "أطباء": [
        {"n": "د. علي الركابي", "s": "قلبية", "desc": "استشاري قسطرة وأمراض قلب معقدة", "a": "الحارثية", "lat": 33.3222, "lon": 44.3585, "stars": 5},
        {"n": "د. عمر الخفاجي", "s": "جملة عصبية", "desc": "جراح دماغ وفقرات - بورد عراقي", "a": "الجادرية", "lat": 33.2801, "lon": 44.3905, "stars": 5},
        {"n": "د. مريم القيسي", "s": "مفاصل", "desc": "أخصائية الروماتزم وحقن المفاصل", "a": "الكرادة", "lat": 33.3135, "lon": 44.4291, "stars": 5},
        {"n": "د. حسن الهاشمي", "s": "باطنية", "desc": "أخصائي أمراض هضمية وكبد", "a": "الأعظمية", "lat": 33.3652, "lon": 44.3751, "stars": 5},
        {"n": "د. زينة الحسني", "s": "جلدية", "desc": "أخصائية أمراض الجلد والليزر", "a": "زيونة", "lat": 33.3401, "lon": 44.4502, "stars": 5}
    ],
    "أعراض": {
        "ألم حاد ومفاجئ في الصدر": ("قلبية", 10, "🚨 طوارئ: اشتباه ذبحة صدرية"),
        "ثقل في الكلام وخدر جانبي": ("جملة عصبية", 10, "🚨 طوارئ: اشتباه سكتة دماغية"),
        "ألم مفاصل وتيبس صباحي": ("مفاصل", 5, "التشخيص: التهاب مفاصل روماتزمي"),
        "ألم بطن يمين حاد جداً": ("باطنية", 9, "🚨 طوارئ: اشتباه زائدة دودية"),
        "اصفرار في العين والجلد": ("باطنية", 7, "التشخيص: يرقان - كبد فيروسي"),
        "عطش شديد وتبول متكرر": ("باطنية", 5, "التشخيص: اضطراب سكر الدم"),
        "طفح جلدي شديد وحكة": ("جلدية", 4, "التشخيص: حساسية جلدية حادة"),
        "سعال جاف مستمر": ("باطنية", 5, "التشخيص: تحسس قصبي")
        # (يمكن إضافة بقية الـ 30 عارضاً هنا بنفس النمط)
    }
}

# --- 3. الدوال ---
if 'step' not in st.session_state: st.session_state.step = 1

def calculate_dist(lat1, lon1, lat2, lon2):
    return f"{math.sqrt((lat1-lat2)*2 + (lon1-lon2)*2)*111.13:.1f} كم"

# --- 4. الصفحات ---

# الصفحة 1: المعلومات
if st.session_state.step == 1:
    st.markdown('<div class="welcome-title">Welcome to AI Doctor 🩺</div>', unsafe_allow_html=True)
    st.markdown('<div class="welcome-sub">BAGHDAD PREMIUM HEALTHCARE</div>', unsafe_allow_html=True)
    with st.form("p_info"):
        name = st.text_input("الأسم الكامل")
        u_area = st.selectbox("اختر منطقتك الحالية:", list(AREAS.keys()))
        phone = st.text_input("رقم الهاتف")
        if st.form_submit_button("دخول النظام"):
            if name and phone:
                st.session_state.p_data = {"name": name, "area": u_area, "phone": phone}
                loc = get_geolocation()
                st.session_state.u_coords = (loc['coords']['latitude'], loc['coords']['longitude']) if loc and 'coords' in loc else AREAS[u_area]
                st.session_state.step = 2
                st.rerun()
            else: st.error("يرجى ملء كافة الحقول")

# الصفحة 2: التشخيص وإخلاء المسؤولية
elif st.session_state.step == 2:
    st.markdown('<div class="welcome-title" style="font-size:30px;">فحص الأعراض</div>', unsafe_allow_html=True)
    sel = st.selectbox("بماذا تشعر؟", ["اختر..."] + list(DATA["أعراض"].keys()))
    if sel != "اختر...":
        spec, urg, diag = DATA["أعراض"][sel]
        st.session_state.selected_spec = spec
        st.info(f"*التحليل الأولي:* {diag}")
        
        st.markdown(f'''
            <div class="disclaimer-card">
                <b>⚠️ إخلاء مسؤولية طبي هام</b><br>
                هذا التشخيص استرشادي فقط. في حالات الطوارئ الحادة يرجى الاتصال بـ <b>122</b> فوراً.
            </div>
        ''', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ رجوع"): st.session_state.step = 1; st.rerun()
        with col2:
            if st.button("عرض الأطباء المختصين"): st.session_state.step = 3; st.rerun()

# الصفحة 3: الأطباء وحجز المربعات
elif st.session_state.step == 3:
    st.markdown(f'<div class="welcome-title" style="font-size:28px;">أطباء {st.session_state.selected_spec}</div>', unsafe_allow_html=True)
    u_lat, u_lon = st.session_state.u_coords
    matches = [d for d in DATA["أطباء"] if d['s'] == st.session_state.selected_spec]
    
    for d in matches:
        dist = calculate_dist(u_lat, u_lon, d['lat'], d['lon'])
        st.markdown(f'''
            <div class="doc-card">
                <div style="display:flex; justify-content:space-between;">
                    <span style="font-size:20px; color:#40E0D0;"><b>{d['n']}</b></span>
                    <span style="color:#aaa; font-size:14px;">📏 {dist}</span>
                </div>
                <div style="color:#FFD700; font-size:14px;">{"⭐" * d['stars']} | اختصاص {d['s']}</div>
                <div style="font-size:13px; margin-top:5px; color:#bbb;">{d['desc']}</div>
            </div>
        ''', unsafe_allow_html=True)
        
        st.write("🕒 اختر وقت الحجز المتاح:")
        slots = {"04:00 PM": True, "05:00 PM": False, "06:00 PM": True, "07:00 PM": False, "08:00 PM": True, "09:00 PM": False}
        cols = st.columns(3)
        for i, (time_str, available) in enumerate(slots.items()):
            with cols[i % 3]:
                if available:
                    if st.button(f"✅ {time_str}", key=f"t_{d['n']}_{time_str}"):
                        st.session_state.final = {"doc": d['n'], "time": time_str, "area": d['a']}
                        st.toast(f"جاري تأكيد حجزك عند {d['n']}...") # رسالة منبثقة سريعة
                        st.session_state.step = 4
                        st.rerun()
                else:
                    st.markdown(f'<div class="slot-box slot-booked">🔒 {time_str}</div>', unsafe_allow_html=True)

    if st.button("⬅️ السابق"): st.session_state.step = 2; st.rerun()

# الصفحة 4: رسالة تم الحجز النهائية
elif st.session_state.step == 4:
    f, p = st.session_state.final, st.session_state.p_data
    st.markdown(f'''
        <div style="border: 2px solid #40E0D0; border-radius: 20px; padding: 40px; text-align: center; background: #000;">
            <h1 style="color:#40E0D0; font-size:40px;">✅ تم الحجز بنجاح</h1>
            <p style="font-size:20px;">شكراً لثقتك بنا يا <b>{p['name']}</b></p>
            <div style="background:#111; padding:25px; border-radius:15px; margin:25px 0; border:1px solid #333; text-align:right; display:inline-block; width:100%;">
                <p>👨‍⚕️ الطبيب: {f['doc']}</p>
                <p>⏰ الموعد: اليوم - {f['time']}</p>
                <p>📍 الموقع: بغداد - {f['area']}</p>
                <p>📞 رقم تواصل العيادة: سيصلك برسالة نصية إلى {p['phone']}</p>
            </div>
            <p style="color:#888;">يرجى الحضور قبل الموعد بـ 10 دقائق.</p>
        </div>
    ''', unsafe_allow_html=True)
    if st.button("العودة للرئيسية"):
        st.session_state.step = 1
        st.rerun()
