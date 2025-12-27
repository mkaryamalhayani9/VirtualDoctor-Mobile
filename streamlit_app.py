import streamlit as st
import math
import google.generativeai as genai
import requests

# --- 1. إعدادات الذكاء الاصطناعي ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        model = genai.GenerativeModel(models[0])
except Exception as e:
    st.error(f"❌ خطأ اتصال بالذكاء الاصطناعي: {e}")

# --- 2. وظيفة الموقع ---
def detect_user_location_by_ip():
    try:
        response = requests.get('https://ipapi.co/json/', timeout=5).json()
        return {
            "city": response.get("city", "بغداد"),
            "region": response.get("region", "تحديد تلقائي"),
            "lat": response.get("latitude", 33.3152),
            "lon": response.get("longitude", 44.3661)
        }
    except:
        return {"city": "بغداد", "region": "اليرموك", "lat": 33.3152, "lon": 44.3661}

# --- 3. التصميم CSS (اعتماد نمط المربعات الموحد) ---
st.set_page_config(page_title="AI Doctor", layout="centered")
st.markdown(r'''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');
    * { font-family: 'Tajawal', sans-serif; direction: rtl; text-align: right; }
    .stApp { background-color: #050505; color: #e0e0e0; }
    
    /* نمط المربع الموحد (مثل مربع الموقع) */
    .custom-card {
        background: rgba(64, 224, 208, 0.05);
        padding: 20px;
        border-radius: 15px;
        border: 1px dashed #40E0D0;
        margin-bottom: 20px;
    }
    
    .main-title { text-align: center; color: #ffffff; font-weight: 700; margin-bottom: 20px; }
    .welcome-header { text-align: center; margin-bottom: 30px; }
    .user-name { color: #40E0D0; font-size: 28px; font-weight: bold; display: block; }
    
    .emergency-box {
        border: 1px solid #ff4b4b;
        background: rgba(255, 75, 75, 0.1);
        color: #ff4b4b;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        margin-top: 10px;
    }

    /* تنسيق أزرار المواعيد لتكون أفقية */
    [data-testid="column"] {
        display: flex;
        justify-content: center;
    }
    .stButton button {
        width: 100% !important;
        border-radius: 10px !important;
        white-space: nowrap !important;
    }
    
    .percentage-text { color: #40E0D0; font-weight: bold; font-size: 20px; }
    </style>
    ''', unsafe_allow_html=True)

# --- 4. قاعدة البيانات ---
DATA = {
    "أطباء": [
        {"n": "د. علي الركابي", "s": "قلبية", "a": "الحارثية", "lat": 33.3222, "lon": 44.3585, "stars": 5, "slots": {"03:00 PM": True, "04:30 PM": False, "06:00 PM": True, "07:30 PM": True}, "phone": "07701234567"},
        {"n": "د. سارة الجبوري", "s": "قلبية", "a": "المنصور", "lat": 33.3251, "lon": 44.3482, "stars": 4, "slots": {"03:30 PM": True, "05:00 PM": True, "06:30 PM": False}, "phone": "07801112223"},
        {"n": "د. مريم القيسي", "s": "مفاصل", "a": "الكرادة", "lat": 33.3135, "lon": 44.4291, "stars": 5, "slots": {"04:00 PM": True, "05:30 PM": True, "07:00 PM": False}, "phone": "07901231234"}
    ]
}

def calculate_dist(lat1, lon1, lat2, lon2):
    return math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2) * 111.13

if 'step' not in st.session_state: st.session_state.step = 1

# --- المرحلة 1: الدخول ---
if st.session_state.step == 1:
    st.markdown("<h1 class='main-title'>🩺 AI Doctor</h1>", unsafe_allow_html=True)
    
    with st.spinner("جاري تحديد موقعك..."):
        user_loc = detect_user_location_by_ip()
        st.session_state.detected_location = user_loc

    st.markdown(f'<div class="custom-card" style="text-align:center;">📍 موقعك الحالي: {user_loc["city"]} - {user_loc["region"]}</div>', unsafe_allow_html=True)
    
    st.markdown('''<div style="background: rgba(255, 255, 255, 0.02); border-right: 4px solid #f1c40f; padding: 15px; border-radius: 8px; font-size: 0.85rem; color: #bbb; margin-bottom: 20px;">⚠️ <b>تنبيه استشاري:</b> هذا النظام هو أداة مساعدة تعمل بالذكاء الاصطناعي، ولا يعتبر بديلاً عن الفحص الطبي المباشر.</div>''', unsafe_allow_html=True)
    
    name = st.text_input("الأسم الكامل")
    phone = st.text_input("رقم الهاتف")
    
    if st.button("دخول النظام", use_container_width=True):
        if name and phone:
            st.session_state.p_info = {"name": name, "phone": phone}
            st.session_state.step = 2
            st.rerun()

# --- المرحلة 2: التحليل والعرض ---
elif st.session_state.step == 2:
    st.markdown(f'''
        <div class="welcome-header">
            <span style="font-size:18px;">🚨 Welcome to AI Doctor</span>
            <span class="user-name">{st.session_state.p_info["name"]}</span>
        </div>
    ''', unsafe_allow_html=True)
    
    text = st.text_area("اشرح حالتك الصحية باختصار:", placeholder="مثال: أشعر بضيق تنفس وألم في الصدر...")

    if st.button("بدء التحليل", use_container_width=True):
        with st.spinner("جاري التحليل..."):
            prompt = (
                f"حلل في سطرين فقط: '{text}'. حدد التشخيص المبدئي والنسبة المئوية ليقينك بوضوح. "
                f"ثم اختر الطبيب الأنسب (القرب والخبرة). إذا كانت الحالة خطرة أضف (🔴 حالة طارئة)."
            )
            response = model.generate_content(prompt)
            st.session_state.diag_res = response.text
            st.session_state.diag_ready = True

    if st.session_state.get('diag_ready'):
        # عرض التشخيص في مربع يشبه مربع الموقع
        diag_html = st.session_state.diag_res.replace("حالة طارئة", '<div class="emergency-box">🔴 حالة طارئة - توجه للمشفى فوراً</div>')
        st.markdown(f'<div class="custom-card"><b>التشخيص المبدئي:</b><br>{diag_html}</div>', unsafe_allow_html=True)
        
        st.write("### الأطباء المتاحون (الأقرب والأعلى تقييماً):")
        
        u_lat, u_lon = st.session_state.detected_location['lat'], st.session_state.detected_location['lon']
        # عرض جميع الأطباء وترتيبهم حسب القرب
        matches = DATA["أطباء"]
        for d in matches: d['d_km'] = calculate_dist(u_lat, u_lon, d['lat'], d['lon'])
        sorted_docs = sorted(matches, key=lambda x: x['d_km'])

        for d in sorted_docs:
            with st.container():
                st.markdown(f'''
                    <div class="custom-card" style="margin-bottom:10px; border-style: solid; border-width: 0 0 0 4px;">
                        <b style="color:#40E0D0; font-size:18px;">{d['n']}</b> <span style="background:#40E0D0; color:black; padding:2px 6px; border-radius:4px; font-size:11px;">{d['s']}</span><br>
                        <span style="color:#f1c40f;">{"⭐" * d['stars']}</span> | يبعد {d['d_km']:.1f} كم عنك<br>
                        <small style="color:#888;">📍 {d['a']}</small>
                    </div>
                ''', unsafe_allow_html=True)
                
                # عرض المواعيد أفقياً (الحجوزات بصف واحد)
                slots = d['slots']
                cols = st.columns(len(slots))
                for i, (slot, is_open) in enumerate(slots.items()):
                    if is_open:
                        if cols[i].button(f"✅ {slot}", key=f"b-{d['n']}-{slot}"):
                            st.session_state.selected_doc = d
                            st.session_state.final_time = slot
                            st.session_state.step = 3
                            st.rerun()
                    else:
                        cols[i].button(f"🔒 {slot}", key=f"l-{d['n']}-{slot}", disabled=True)

# --- المرحلة 3: صفحة النجاح ---
elif st.session_state.step == 3:
    st.markdown(f'''
        <div class="custom-card" style="text-align:center; border-style:solid; border-color:#40E0D0;">
            <h2 style="color:#40E0D0;">تم الحجز بنجاح ✅</h2>
            <hr style="border-color:#222;">
            <div style="text-align:right;">
                <p>👤 المريض: <b>{st.session_state.p_info['name']}</b></p>
                <p>👨‍⚕️ الطبيب المختص: {st.session_state.selected_doc['n']}</p>
                <p>⏰ وقت الحجز: {st.session_state.final_time}</p>
                <p>📍 العنوان: {st.session_state.selected_doc['a']}</p>
                <p>📞 هاتف العيادة: {st.session_state.selected_doc['phone']}</p>
            </div>
        </div>
    ''', unsafe_allow_html=True)
    if st.button("العودة للرئيسية", use_container_width=True):
        st.session_state.step = 1
        st.rerun()
