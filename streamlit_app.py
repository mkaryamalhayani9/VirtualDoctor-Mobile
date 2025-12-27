import streamlit as st
import math
import google.generativeai as genai
import requests

# --- 1. إعدادات الذكاء الاصطناعي (تحديث للموديل لضمان الاستقرار) ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # استخدام موديل flash لسرعة الاستجابة وتجنب أخطاء الـ NotFound
        model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"❌ خطأ اتصال بالذكاء الاصطناعي: {e}")

# --- 2. وظيفة الموقع (تعديل: حذف اليرموك كافتراضي) ---
def detect_user_location_by_ip():
    try:
        response = requests.get('https://ipapi.co/json/', timeout=3).json()
        return {
            "city": response.get("city", "بغداد"),
            "region": response.get("region", "تحديد تلقائي"),
            "lat": response.get("latitude", 33.3152),
            "lon": response.get("longitude", 44.3661)
        }
    except:
        # إرجاع قيم عامة دون فرض منطقة معينة
        return {"city": "بغداد", "region": "تحديد تلقائي", "lat": 33.3152, "lon": 44.3661}

# --- 3. التصميم المعتمد (رسمي، مريح، وفيروزي) ---
st.set_page_config(page_title="AI Doctor", layout="centered")
st.markdown(r'''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');
    * { font-family: 'Tajawal', sans-serif; direction: rtl; text-align: right; }
    .stApp { background-color: #050505; color: #e0e0e0; }
    
    /* العناوين والترحيب باللون الفيروزي الرسمي */
    .app-title { text-align: center; color: #40E0D0; font-size: 42px; font-weight: 700; margin-bottom: 5px; }
    .welcome-note { text-align: center; color: #40E0D0; font-size: 19px; opacity: 0.8; margin-bottom: 0px; }
    .user-name-title { 
        color: #40E0D0; font-size: 45px; font-weight: 700; text-align: center; display: block; 
        margin-bottom: 30px; text-shadow: 0 4px 20px rgba(64,224,208,0.2);
    }
    
    /* الإطارات المتصلة (نفس مربع التشخيص لراحة العين) */
    .standard-card { 
        border: 2px solid #40E0D0; 
        background: rgba(64, 224, 208, 0.02); 
        padding: 22px; 
        border-radius: 15px; 
        margin-bottom: 20px; 
    }
    
    /* إطار التنبيه الأصفر (متصل وليس منقط) */
    .warning-card { 
        border: 2px solid #f1c40f; 
        background: rgba(241, 196, 15, 0.05); 
        padding: 15px; 
        border-radius: 12px; 
        color: #f1c40f; 
        margin-bottom: 20px; 
    }
    
    .location-box { border: 1px dashed #40E0D0; padding: 10px; border-radius: 10px; text-align: center; color: #40E0D0; margin-bottom: 20px; }

    /* المواعيد الأفقية */
    [data-testid="column"] { flex: 1 !important; min-width: 85px !important; }
    .stButton button { width: 100% !important; border-radius: 8px !important; font-weight: 500; }
    
    .highlight-cyan { color: #40E0D0; font-weight: bold; }
    .nature-icon { font-size: 30px; color: #40E0D0; text-align: center; display: block; margin: 10px 0; }
    </style>
    ''', unsafe_allow_html=True)

# --- 4. قاعدة البيانات ---
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
    
    st.markdown(f'<div class="location-box">📍 الموقع الحالي: {user_loc["city"]} - {user_loc["region"]}</div>', unsafe_allow_html=True)
    st.markdown('<div class="warning-card">⚠️ <b>تنبيه استشاري رسمي:</b> هذا النظام أداة مساعدة، ولا يغني عن الفحص السريري المباشر أو زيارة المشفى.</div>', unsafe_allow_html=True)
    
    name = st.text_input("الأسم الكامل")
    phone = st.text_input("رقم الهاتف")
    if st.button("دخول النظام", use_container_width=True):
        if name and phone:
            st.session_state.p_info = {"name": name, "phone": phone}
            st.session_state.step = 2; st.rerun()

# --- المرحلة 2: التحليل والعرض ---
elif st.session_state.step == 2:
    st.markdown(f'<div class="welcome-note">Welcome to AI Doctor ⛑️</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="user-name-title">{st.session_state.p_info["name"]}</div>', unsafe_allow_html=True)
    
    text = st.text_area("اشرح حالتك الصحية باختصار:", placeholder="مثال: أشعر بضيق تنفس وألم جهة الصدر...")

    if st.button("بدء تحليل الحالة", use_container_width=True):
        with st.spinner("جاري التحليل الذكي..."):
            u_lat = st.session_state.detected_location['lat']
            u_lon = st.session_state.detected_location['lon']
            spec = "قلبية" if any(w in text for w in ["قلب", "صدر", "نفس"]) else "مفاصل" if "مفصل" in text else "باطنية"
            matches = [d for d in DATA["أطباء"] if d['s'] == spec] or DATA["أطباء"]
            for d in matches: d['d_km'] = calculate_dist(u_lat, u_lon, d['lat'], d['lon'])
            
            best_doc = sorted(matches, key=lambda x: (x['d_km'], -x['stars']))[0]
            first_slot = next((t for t, s in best_doc['slots'].items() if s), "3:00 PM")

            prompt = f"حلل بدقة: '{text}'. اذكر التشخيص والنسبة المئوية (Bold). انصح بزيارة {best_doc['n']}."
            response = model.generate_content(prompt)
            st.session_state.diag_res = response.text.replace("%", "*%*")
            st.session_state.ai_advice = f"💡 *التوصية:* ننصحك بحجز موعد عند <span class='highlight-cyan'>{best_doc['n']}</span> في موعد <span class='highlight-cyan'>{first_slot}</span>."
            st.session_state.diag_ready = True

    if st.session_state.get('diag_ready'):
        # إطارات متصلة (Solid) للتشخيص والتوصية
        st.markdown(f'<div class="standard-card"><b>التشخيص المبدئي:</b><br>{st.session_state.diag_res}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="standard-card" style="border-right: 10px solid #40E0D0;">{st.session_state.ai_advice}</div>', unsafe_allow_html=True)
        
        st.write("### قائمة الأطباء المتاحين:")
        for d in DATA["أطباء"]:
            dist = calculate_dist(st.session_state.detected_location['lat'], st.session_state.detected_location['lon'], d['lat'], d['lon'])
            st.markdown(f'''
                <div class="standard-card">
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

# --- المرحلة 3: صفحة النجاح (الغصن 🌿) ---
elif st.session_state.step == 3:
    st.markdown(f'''
        <div class="standard-card" style="text-align:center;">
            <div class="nature-icon">🌿</div>
            <h2 style="color:#40E0D0; margin-bottom:20px;">تم تأكيد حجز الموعد</h2>
            <div style="text-align:right; line-height:2.2;">
                <p>👤 <b>المريض:</b> {st.session_state.p_info['name']}</p>
                <p>👨‍⚕️ <b>الطبيب المختص:</b> {st.session_state.selected_doc['n']}</p>
                <p>🕒 <b>وقت الموعد:</b> اليوم الساعة {st.session_state.final_time}</p>
                <p>📍 <b>العنوان:</b> {st.session_state.selected_doc['a']}</p>
                <p>📞 <b>للتواصل:</b> <span class="highlight-cyan">{st.session_state.selected_doc['phone']}</span></p>
            </div>
            <div class="nature-icon">🌿</div>
            <p style="color:#888; font-size:14px; margin-top:10px;">نتمنى لك تمام الصحة والعافية</p>
        </div>
    ''', unsafe_allow_html=True)
    if st.button("العودة للرئيسية", use_container_width=True): st.session_state.step = 1; st.rerun()
