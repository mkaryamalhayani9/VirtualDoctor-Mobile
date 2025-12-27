import streamlit as st
import math
import google.generativeai as genai
import requests

# --- 1. إعدادات الذكاء الاصطناعي ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # اختيار أول موديل يدعم توليد المحتوى
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

# --- 3. التصميم المطور (CSS) ---
st.set_page_config(page_title="AI Doctor Baghdad", layout="centered")

st.markdown(r'''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Tajawal', sans-serif;
        direction: rtl;
        text-align: right;
    }
    
    .stApp { background-color: #080808; color: #e0e0e0; }
    
    /* تنبيه الموقع */
    .location-banner { 
        background: rgba(64, 224, 208, 0.05); 
        padding: 12px; 
        border-radius: 10px; 
        border: 1px dashed #40E0D0; 
        color: #40E0D0; 
        text-align: center; 
        margin-bottom: 10px; 
    }
    
    /* إخلاء المسؤولية الاحترافي */
    .disclaimer-box {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid #333;
        border-right: 4px solid #f1c40f;
        padding: 15px;
        border-radius: 8px;
        font-size: 0.85rem;
        color: #bbb;
        margin-bottom: 25px;
        line-height: 1.6;
    }

    .emergency-alert { 
        color: #ff4b4b; 
        font-weight: bold; 
        border: 1px solid #ff4b4b; 
        padding: 10px; 
        border-radius: 8px; 
        background: rgba(255, 75, 75, 0.1);
        display: block;
        margin: 10px 0;
    }

    /* كارت الطبيب */
    .doc-card { 
        background: #121212; 
        padding: 20px; 
        border-radius: 18px; 
        border: 1px solid #222; 
        margin-bottom: 20px; 
        transition: 0.3s;
    }
    .doc-card:hover { border-color: #40E0D0; box-shadow: 0 4px 15px rgba(64, 224, 208, 0.1); }
    
    .star-rating { color: #f1c40f; font-size: 0.9rem; margin: 5px 0; }
    .spec-label { color: #40E0D0; font-weight: bold; font-size: 0.9rem; }
    
    .success-panel { 
        border: 1px solid #40E0D0; 
        padding: 30px; 
        border-radius: 20px; 
        background: linear-gradient(145deg, #0d0d0d, #151515); 
        text-align: center; 
    }
    </style>
    ''', unsafe_allow_html=True)

# --- 4. البيانات ---
DATA = {
    "أطباء": [
        {"n": "د. علي الركابي", "s": "قلبية", "a": "الحارثية", "lat": 33.3222, "lon": 44.3585, "stars": 5, "slots": {"04:00 PM": True, "05:00 PM": False, "06:00 PM": True}, "phone": "07701234567"},
        {"n": "د. سارة الجبوري", "s": "قلبية", "a": "المنصور", "lat": 33.3251, "lon": 44.3482, "stars": 4, "slots": {"06:00 PM": True, "07:30 PM": True}, "phone": "07801112223"},
        {"n": "د. مريم القيسي", "s": "مفاصل", "a": "الكرادة", "lat": 33.3135, "lon": 44.4291, "stars": 5, "slots": {"05:00 PM": True, "08:00 PM": False}, "phone": "07901231234"},
        {"n": "د. طه العسكري", "s": "باطنية", "a": "اليرموك", "lat": 33.3121, "lon": 44.3610, "stars": 3, "slots": {"09:00 PM": True, "10:00 PM": False}, "phone": "07801212123"}
    ]
}

def calculate_dist(lat1, lon1, lat2, lon2):
    return math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2) * 111.13

if 'step' not in st.session_state: st.session_state.step = 1

# --- المرحلة 1: تسجيل الدخول ---
if st.session_state.step == 1:
    st.markdown("<h2 style='text-align:center;'>نظام التشخيص الذكي 🩺</h2>", unsafe_allow_html=True)
    
    with st.spinner("جاري تحديد موقعك..."):
        user_loc = detect_user_location_by_ip()
        st.session_state.detected_location = user_loc

    st.markdown(f'<div class="location-banner">📍 موقعك المكتشف: {user_loc["city"]} - {user_loc["region"]}</div>', unsafe_allow_html=True)
    
    st.markdown('''
        <div class="disclaimer-box">
            <b>تنبيه استشاري:</b> هذا النظام يعتمد على الذكاء الاصطناعي لتقديم توجيهات أولية فقط. 
            المعلومات المقدمة هنا <b>لا تغني عن زيارة الطبيب المختص</b> أو الحصول على تشخيص طبي نهائي. 
            في الحالات الطارئة، يرجى التوجه لأقرب مستشفى فوراً.
        </div>
    ''', unsafe_allow_html=True)
    
    name = st.text_input("الأسم الكامل")
    phone = st.text_input("رقم الهاتف")
    
    if st.button("دخول النظام", use_container_width=True):
        if name and phone:
            st.session_state.p_info = {"name": name, "phone": phone}
            st.session_state.step = 2
            st.rerun()
        else:
            st.warning("يرجى ملء البيانات للمتابعة")

# --- المرحلة 2: التحليل والعرض ---
elif st.session_state.step == 2:
    st.markdown(f"<h3>أهلاً بك، {st.session_state.p_info['name']} 👋</h3>", unsafe_allow_html=True)
    text = st.text_area("صف لي ما تشعر به (الأعراض):", placeholder="مثال: أشعر بألم في الصدر مع ضيق تنفس...")

    if st.button("بدء تحليل الحالة", use_container_width=True):
        with st.spinner("يتم الآن تحليل الأعراض ومطابقة الأطباء..."):
            prompt = (
                f"حلل بدقة وبلهجة طبية محترمة: '{text}'. "
                f"حدد الاختصاص الأنسب، التشخيص المبدئي، ونسبة اليقين. "
                f"إذا كان هناك خطر، ابدأ بكلمة (🔴 حالة طارئة)."
            )
            response = model.generate_content(prompt)
            st.session_state.diag_res = response.text
            
            # استنتاج التخصص
            st.session_state.spec = "باطنية"
            for s in ["قلبية", "باطنية", "مفاصل", "جملة عصبية"]:
                if s in response.text: st.session_state.spec = s; break
            st.session_state.diag_ready = True

    if st.session_state.get('diag_ready'):
        res_html = st.session_state.diag_res.replace("حالة طارئة", '<span class="emergency-alert">🔴 حالة طارئة - يرجى مراجعة الطوارئ فوراً</span>')
        st.markdown(f'<div style="background:#1a1a1a; padding:20px; border-radius:15px; border-right:5px solid #40E0D0; margin-bottom:30px;">{res_html}</div>', unsafe_allow_html=True)
        
        st.subheader("الأطباء المقترحون حسب موقعك وتخصصك:")
        
        u_lat = st.session_state.detected_location['lat']
        u_lon = st.session_state.detected_location['lon']
        
        matches = [d for d in DATA["أطباء"] if d['s'] == st.session_state.spec]
        for d in matches: d['d_km'] = calculate_dist(u_lat, u_lon, d['lat'], d['lon'])
        sorted_docs = sorted(matches, key=lambda x: x['d_km'])

        for d in sorted_docs:
            stars = "⭐" * d['stars']
            st.markdown(f'''
                <div class="doc-card">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                        <div>
                            <b style="font-size:1.2rem; color:#40E0D0;">{d['n']}</b><br>
                            <span class="spec-label">أخصائي {d['s']}</span><br>
                            <div class="star-rating">{stars} (تقييم المرضى)</div>
                            <small>📍 {d['a']} • يبعد عنك {d['d_km']:.1f} كم</small>
                        </div>
                    </div>
                </div>
            ''', unsafe_allow_html=True)
            
            # ترتيب المواعيد أفقياً بشكل احترافي
            slots = d['slots']
            cols = st.columns(len(slots))
            for i, (time, status) in enumerate(slots.items()):
                with cols[i]:
                    if status:
                        if st.button(f"✅ {time}", key=f"{d['n']}-{time}"):
                            st.session_state.selected_doc = d
                            st.session_state.final_time = time
                            st.session_state.step = 3
                            st.rerun()
                    else:
                        st.button(f"🔒 {time}", key=f"{d['n']}-{time}-locked", disabled=True)

# --- المرحلة 3: التأكيد ---
elif st.session_state.step == 3:
    st.markdown(f'''
        <div class="success-panel">
            <h2 style="color:#40E0D0;">تم تثبيت موعدك ✅</h2>
            <p>السيد/ة <b>{st.session_state.p_info['name']}</b>، تم حجز الموعد بنجاح.</p>
            <div style="background:rgba(255,255,255,0.05); padding:20px; border-radius:15px; margin:20px 0; text-align:right;">
                <p>👨‍⚕️ <b>الطبيب:</b> {st.session_state.selected_doc['n']}</p>
                <p>🕒 <b>الوقت:</b> {st.session_state.final_time}</p>
                <p>📍 <b>العنوان:</b> {st.session_state.selected_doc['a']}</p>
                <p>📞 <b>رقم العيادة:</b> {st.session_state.selected_doc['phone']}</p>
            </div>
            <p style="font-size:0.9rem; color:#888;">يرجى الحضور قبل الموعد بـ 10 دقائق. تمنياتنا لك بالشفاء.</p>
        </div>
    ''', unsafe_allow_html=True)
    
    if st.button("العودة للرئيسية"):
        st.session_state.step = 1
        st.rerun()
