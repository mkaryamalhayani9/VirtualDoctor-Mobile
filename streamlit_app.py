import streamlit as st
import math
import google.generativeai as genai
import requests

# --- 1. إعدادات الذكاء الاصطناعي ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-pro')
except Exception as e:
    st.error(f"❌ خطأ اتصال بالذكاء الاصطناعي: {e}")

# --- 2. وظيفة الموقع الجغرافي ---
def detect_user_location_by_ip():
    try:
        response = requests.get('https://ipapi.co/json/', timeout=5).json()
        return {"city": response.get("city", "بغداد"), "region": response.get("region", "تحديد تلقائي"), "lat": response.get("latitude", 33.3152), "lon": response.get("longitude", 44.3661)}
    except:
        return {"city": "بغداد", "region": "اليرموك", "lat": 33.3152, "lon": 44.3661}

# --- 3. التصميم النهائي المعتمد (CSS) ---
st.set_page_config(page_title="AI Doctor", layout="centered")
st.markdown(r'''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');
    * { font-family: 'Tajawal', sans-serif; direction: rtl; text-align: right; }
    .stApp { background-color: #050505; color: #e0e0e0; }
    
    /* الهوية الفيروزية الرسمية */
    .app-title { text-align: center; color: #40E0D0; font-size: 42px; font-weight: 700; margin-bottom: 5px; }
    .welcome-label { text-align: center; color: #40E0D0; font-size: 18px; margin-bottom: 0px; opacity: 0.9; }
    .user-name-title { 
        color: #40E0D0; font-size: 45px; font-weight: 700; text-align: center; display: block; 
        margin-bottom: 30px; text-shadow: 0 4px 15px rgba(64,224,208,0.2);
    }
    
    /* المربعات الموحدة (إطار فيروزي صلب) */
    .main-card { 
        border: 2px solid #40E0D0; 
        background: rgba(64, 224, 208, 0.02); 
        padding: 22px; 
        border-radius: 15px; 
        margin-bottom: 20px; 
    }
    
    /* التنبيه الأصفر المتناسق */
    .alert-card { 
        border: 2px solid #f1c40f; 
        background: rgba(241, 196, 15, 0.05); 
        padding: 15px; 
        border-radius: 12px; 
        color: #f1c40f; 
        margin-bottom: 20px; 
    }
    
    .location-tag { border: 1px dashed #40E0D0; padding: 10px; border-radius: 10px; text-align: center; color: #40E0D0; margin-bottom: 20px; }

    /* تنسيق المواعيد الأفقية */
    [data-testid="column"] { flex: 1 !important; min-width: 85px !important; }
    .stButton button { width: 100% !important; border-radius: 8px !important; font-weight: 500; }
    
    .cyan-bold { color: #40E0D0; font-weight: bold; }
    .leaf-icon { font-size: 28px; color: #40E0D0; text-align: center; display: block; margin: 10px 0; }
    </style>
    ''', unsafe_allow_html=True)

# --- 4. محاكاة قاعدة البيانات ---
DATA = {
    "أطباء": [
        {"n": "د. علي الركابي", "s": "قلبية", "a": "الحارثية", "lat": 33.3222, "lon": 44.3585, "stars": 5, "slots": {"03:00 PM": True, "04:30 PM": False, "06:00 PM": True}, "phone": "07701234567"},
        {"n": "د. سارة الجبوري", "s": "قلبية", "a": "المنصور", "lat": 33.3251, "lon": 44.3482, "stars": 4, "slots": {"03:30 PM": True, "05:00 PM": True, "06:30 PM": False}, "phone": "07801112223"},
        {"n": "د. مريم القيسي", "s": "مفاصل", "a": "الكرادة", "lat": 33.3135, "lon": 44.4291, "stars": 5, "slots": {"04:00 PM": True, "05:30 PM": True, "07:00 PM": False}, "phone": "07901231234"}
    ]
}

def calculate_dist(lat1, lon1, lat2, lon2):
    return math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2) * 111.13

if 'step' not in st.session_state: st.session_state.step = 1

# --- المرحلة 1: صفحة الدخول ---
if st.session_state.step == 1:
    st.markdown("<div class='app-title'>AI Doctor 🩺</div>", unsafe_allow_html=True)
    user_loc = detect_user_location_by_ip()
    st.session_state.detected_location = user_loc
    
    st.markdown(f'<div class="location-tag">📍 الموقع الحالي: {user_loc["city"]} - {user_loc["region"]}</div>', unsafe_allow_html=True)
    st.markdown('<div class="alert-card">⚠️ <b>تنبيه استشاري:</b> هذا النظام أداة مساعدة ذكية، ولا يغني عن المراجعة الطبية المباشرة.</div>', unsafe_allow_html=True)
    
    name = st.text_input("الأسم الكامل")
    phone = st.text_input("رقم الهاتف")
    if st.button("دخول النظام", use_container_width=True):
        if name and phone:
            st.session_state.p_info = {"name": name, "phone": phone}
            st.session_state.step = 2; st.rerun()

# --- المرحلة 2: التشخيص واختيار الطبيب ---
elif st.session_state.step == 2:
    st.markdown(f'<div class="welcome-label">Welcome to AI Doctor ⛑️</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="user-name-title">{st.session_state.p_info["name"]}</div>', unsafe_allow_html=True)
    
    text = st.text_area("اشرح حالتك الصحية باختصار:")

    if st.button("بدء تحليل الحالة", use_container_width=True):
        with st.spinner("جاري التحليل الفني..."):
            spec = "قلبية" if any(w in text for w in ["قلب", "صدر", "نفس"]) else "باطنية"
            matches = [d for d in DATA["أطباء"] if d['s'] == spec] or DATA["أطباء"]
            u_loc = st.session_state.detected_location
            for d in matches: d['d_km'] = calculate_dist(u_loc['lat'], u_loc['lon'], d['lat'], d['lon'])
            
            best_doc = sorted(matches, key=lambda x: (x['d_km'], -x['stars']))[0]
            first_slot = next((t for t, s in best_doc['slots'].items() if s), "3:00 PM")

            prompt = f"حلل بدقة: '{text}'. اذكر التشخيص والنسبة المئوية (Bold). انصح بمراجعة {best_doc['n']}."
            response = model.generate_content(prompt)
            st.session_state.diag_res = response.text.replace("%", "*%*")
            st.session_state.ai_rec = f"💡 *توصية ذكية:* ننصحك بحجز موعد عند <span class='cyan-bold'>{best_doc['n']}</span> في موعد <span class='cyan-bold'>{first_slot}</span>."
            st.session_state.diag_ready = True

    if st.session_state.get('diag_ready'):
        st.markdown(f'<div class="main-card"><b>التشخيص المبدئي:</b><br>{st.session_state.diag_res}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="main-card" style="border-right: 8px solid #40E0D0;">{st.session_state.ai_rec}</div>', unsafe_allow_html=True)
        
        st.write("### قائمة الأطباء المتاحين:")
        for d in DATA["أطباء"]:
            dist = calculate_dist(st.session_state.detected_location['lat'], st.session_state.detected_location['lon'], d['lat'], d['lon'])
            st.markdown(f'''
                <div class="main-card">
                    <b style="color:#40E0D0; font-size:18px;">{d['n']}</b> | <small>{d['s']}</small><br>
                    <span style="color:#f1c40f;">{"⭐" * d['stars']}</span> | يبعد {dist:.1f} كم 📍
                </div>
            ''', unsafe_allow_html=True)
            
            cols = st.columns(len(d['slots']))
            for i, (time, is_open) in enumerate(d['slots'].items()):
                with cols[i]:
                    if is_open:
                        if st.button(f"✅ {time}", key=f"{d['n']}-{time}"):
                            st.session_state.selected_doc = d; st.session_state.final_time = time; st.session_state.step = 3; st.rerun()
                    else: st.button(f"🔒 {time}", key=f"{d['n']}-{time}-l", disabled=True)

# --- المرحلة 3: صفحة النجاح الرسمية ---
elif st.session_state.step == 3:
    st.markdown(f'''
        <div class="main-card" style="text-align:center;">
            <div class="leaf-icon">🌿</div>
            <h2 style="color:#40E0D0;">تأكيد موعد الحجز</h2>
            <div style="text-align:right; line-height:2.2; margin-top:20px;">
                <p>👤 <b>المريض:</b> {st.session_state.p_info['name']}</p>
                <p>👨‍⚕️ <b>الطبيب:</b> {st.session_state.selected_doc['n']}</p>
                <p>🕒 <b>الموعد:</b> {st.session_state.final_time}</p>
                <p>📍 <b>العنوان:</b> {st.session_state.selected_doc['a']}</p>
                <p>📞 <b>للتواصل:</b> <span class="cyan-bold">{st.session_state.selected_doc['phone']}</span></p>
            </div>
            <div class="leaf-icon">🌿</div>
            <p style="color:#888; font-size:14px;">تمنياتنا لك بالشفاء العاجل</p>
        </div>
    ''', unsafe_allow_html=True)
    if st.button("العودة للرئيسية", use_container_width=True): st.session_state.step = 1; st.rerun()
