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

# --- 3. التصميم المطور CSS (مراجعة شاملة) ---
st.set_page_config(page_title="AI Doctor", layout="centered")
st.markdown(r'''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    
    /* الأساسيات */
    * { font-family: 'Tajawal', sans-serif; direction: rtl; text-align: right; }
    .stApp { background-color: #050505; color: #e0e0e0; }
    
    /* الإطارات الموحدة (فيروزي منقط) */
    .custom-frame { 
        border: 2px dashed #40E0D0; 
        background: rgba(64, 224, 208, 0.03); 
        padding: 20px; 
        border-radius: 15px; 
        margin-bottom: 20px; 
    }
    
    /* إطار التنبيه (أصفر منقط) */
    .warning-frame { 
        border: 2px dashed #f1c40f; 
        background: rgba(241, 196, 15, 0.05); 
        padding: 15px; 
        border-radius: 12px; 
        color: #f1c40f; 
        margin-bottom: 20px; 
    }
    
    /* مربع التوصية الذكية */
    .recommend-box { 
        border: 2px solid #40E0D0; 
        border-right: 10px solid #40E0D0;
        background: rgba(64, 224, 208, 0.1); 
        padding: 15px; 
        border-radius: 15px; 
        margin-bottom: 25px; 
    }

    /* العناوين والترحيب */
    .page-title { text-align: center; color: #40E0D0; font-size: 35px; font-weight: 700; margin-bottom: 10px; }
    .user-highlight { 
        color: #40E0D0; 
        font-size: 38px; 
        font-weight: bold; 
        text-align: center; 
        display: block; 
        margin: 10px 0 25px 0; 
        text-shadow: 0 0 15px rgba(64,224,208,0.2);
    }
    
    /* إجبار الأزرار لتكون أفقية تماماً */
    [data-testid="column"] { 
        flex: 1 !important; 
        min-width: 80px !important; 
    }
    .stButton button { 
        width: 100% !important; 
        font-size: 13px !important; 
        border-radius: 8px !important; 
        padding: 2px !important;
    }

    .bold-cyan { color: #40E0D0; font-weight: bold; }
    </style>
    ''', unsafe_allow_html=True)

# --- 4. قاعدة البيانات ---
DATA = {
    "أطباء": [
        {"n": "د. علي الركابي", "s": "قلبية", "a": "الحارثية", "lat": 33.3222, "lon": 44.3585, "stars": 5, "slots": {"03:00": True, "04:30": False, "06:00": True}, "phone": "07701234567"},
        {"n": "د. سارة الجبوري", "s": "قلبية", "a": "المنصور", "lat": 33.3251, "lon": 44.3482, "stars": 4, "slots": {"03:30": True, "05:00": True, "06:30": False}, "phone": "07801112223"},
        {"n": "د. مريم القيسي", "s": "مفاصل", "a": "الكرادة", "lat": 33.3135, "lon": 44.4291, "stars": 5, "slots": {"04:00": True, "05:30": True, "07:00": False}, "phone": "07901231234"}
    ]
}

def calculate_dist(lat1, lon1, lat2, lon2):
    return math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2) * 111.13

if 'step' not in st.session_state: st.session_state.step = 1

# --- المرحلة 1: الدخول ---
if st.session_state.step == 1:
    st.markdown("<div class='page-title'>AI Doctor 🩺</div>", unsafe_allow_html=True)
    user_loc = detect_user_location_by_ip()
    st.session_state.detected_location = user_loc
    
    st.markdown(f'<div class="custom-frame" style="text-align:center;">📍 موقعك الحالي: {user_loc["city"]} - {user_loc["region"]}</div>', unsafe_allow_html=True)
    st.markdown('<div class="warning-frame">⚠️ <b>تنبيه استشاري:</b> هذا النظام أداة مساعدة ذكية، ولا يغني عن الفحص الطبي المباشر أو زيارة المستشفى.</div>', unsafe_allow_html=True)
    
    name = st.text_input("الأسم الكامل")
    phone = st.text_input("رقم الهاتف")
    
    if st.button("دخول النظام", use_container_width=True):
        if name and phone:
            st.session_state.p_info = {"name": name, "phone": phone}
            st.session_state.step = 2
            st.rerun()

# --- المرحلة 2: التشخيص والتحليل ---
elif st.session_state.step == 2:
    st.markdown(f'<div style="text-align:center; font-size:20px;">Welcome to AI Doctor ⛑️</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="user-highlight">{st.session_state.p_info["name"]}</div>', unsafe_allow_html=True)
    
    text = st.text_area("اشرح حالتك الصحية باختصار:", placeholder="مثال: أشعر بضيق تنفس وألم جهة الصدر...")

    if st.button("بدء تحليل الحالة", use_container_width=True):
        with st.spinner("جاري تحليل بياناتك..."):
            u_lat = st.session_state.detected_location['lat']
            u_lon = st.session_state.detected_location['lon']
            
            # محرك ذكي لاختيار الطبيب الأنسب (الأقرب والأعلى تقييماً)
            spec = "قلبية" if any(w in text for w in ["قلب", "صدر", "نفس"]) else "مفاصل" if "مفصل" in text else "باطنية"
            possible_docs = [d for d in DATA["أطباء"] if d['s'] == spec] or DATA["أطباء"]
            for d in possible_docs: d['d_km'] = calculate_dist(u_lat, u_lon, d['lat'], d['lon'])
            
            best_doc = sorted(possible_docs, key=lambda x: (x['d_km'], -x['stars']))[0]
            first_slot = next((t for t, s in best_doc['slots'].items() if s), "أقرب وقت")

            prompt = (f"حلل في سطرين: '{text}'. اذكر التشخيص المبدئي واجعل النسبة المئوية *Bold*. "
                      f"إذا كانت الحالة خطيرة، ابدأ بـ 🔴 حالة طارئة.")
            response = model.generate_content(prompt)
            
            st.session_state.diag_res = response.text.replace("%", "*%*")
            st.session_state.best_advice = f"💡 *توصية AI Doctor:* ننصحك بمراجعة <span class='bold-cyan'>{best_doc['n']}</span> في موعد <span class='bold-cyan'>{first_slot}</span> (الخيار الأفضل حسب موقعك)."
            st.session_state.diag_ready = True

    if st.session_state.get('diag_ready'):
        # عرض التشخيص (إطار فيروزي منقط)
        st.markdown(f'<div class="custom-frame"><b>التشخيص المتوقع:</b><br>{st.session_state.diag_res}</div>', unsafe_allow_html=True)
        # مربع التوصية الذكية
        st.markdown(f'<div class="recommend-box">{st.session_state.best_advice}</div>', unsafe_allow_html=True)
        
        st.write("### 👨‍⚕️ الأطباء المتاحون بجانبك:")
        for d in DATA["أطباء"]:
            dist = calculate_dist(st.session_state.detected_location['lat'], st.session_state.detected_location['lon'], d['lat'], d['lon'])
            st.markdown(f'''
                <div class="custom-frame" style="margin-bottom:10px;">
                    <b style="color:#40E0D0; font-size:18px;">{d['n']}</b> | {d['s']}<br>
                    <span style="color:#f1c40f;">{"⭐" * d['stars']}</span> | يبعد {dist:.1f} كم 📍 | {d['a']}
                </div>
            ''', unsafe_allow_html=True)
            
            # المواعيد الأفقية
            slots = d['slots']
            cols = st.columns(len(slots))
            for i, (time, is_open) in enumerate(slots.items()):
                with cols[i]:
                    if is_open:
                        if st.button(f"✅ {time}", key=f"{d['n']}-{time}"):
                            st.session_state.selected_doc = d
                            st.session_state.final_time = time
                            st.session_state.step = 3
                            st.rerun()
                    else:
                        st.button(f"🔒 {time}", key=f"{d['n']}-{time}-l", disabled=True)

# --- المرحلة 3: النجاح ---
elif st.session_state.step == 3:
    st.markdown(f'''
        <div class="custom-frame" style="text-align:center; border-style:solid;">
            <div style="font-size:60px; margin-bottom:10px;">
            <h2 style="color:#40E0D0; margin-bottom:20px;">تم تثبيت حجزك بنجاح</h2>
            <div style="text-align:right; line-height:2.2;">
                <p>👤 <b>المريض:</b> {st.session_state.p_info['name']}</p>
                <p>👨‍⚕️ <b>الطبيب:</b> {st.session_state.selected_doc['n']}</p>
                <p>🕒 <b>الموعد:</b> اليوم الساعة {st.session_state.final_time}</p>
                <p>📍 <b>العنوان:</b> {st.session_state.selected_doc['a']}</p>
                <p>📞 <b>للتواصل:</b> <span style="color:#40E0D0;">{st.session_state.selected_doc['phone']}</span></p>
            </div>
            <p style="margin-top:20px; color:#888;">مع تمنياتنا لك بالشفاء العاجل 🎉</p>
        </div>
    ''', unsafe_allow_html=True)
    if st.button("العودة للرئيسية", use_container_width=True):
        st.session_state.step = 1
        st.rerun()
