
import streamlit as st
import math
import google.generativeai as genai

# --- 1. إعداد الذكاء الاصطناعي (بنفس طريقتك الناجحة) ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # نستخدم البحث التلقائي عن الموديل لضمان عدم حدوث خطأ 404
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        model = genai.GenerativeModel(models[0])
    else:
        st.error("⚠️ لم يتم العثور على المفتاح في Secrets")
except Exception as e:
    st.error(f"❌ فشل الاتصال بمحرك الذكاء الاصطناعي: {e}")

# --- 2. التنسيق (نفس ألوانك وتصميمك مع إضافة شكل النجوم) ---
st.set_page_config(page_title="AI Doctor Baghdad", layout="centered")

st.markdown(r'''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    * { font-family: 'Tajawal', sans-serif; direction: rtl; text-align: center; }
    .stApp { background-color: #050505; color: #e0e0e0; }
    .welcome-title { font-size: 38px; color: #40E0D0; font-weight: bold; }
    .diag-box { padding: 20px; border-radius: 15px; background: rgba(64, 224, 208, 0.05); border: 1px solid #40E0D0; text-align: right; }
    .doc-card { background-color: #0d0d0d; padding: 20px; border-radius: 15px; border-bottom: 4px solid #40E0D0; margin: 15px 0; text-align: right; }
    .star-color { color: #FFD700; }
    .time-badge { background: #40E0D0; color: black; padding: 5px 10px; border-radius: 5px; font-weight: bold; margin: 2px; display: inline-block; cursor: pointer; }
    </style>
    ''', unsafe_allow_html=True)

# --- 3. قاعدة البيانات المحدثة (نجوم + أوقات) ---
# ملاحظة: الموقع الآن يتم تحديثه تلقائياً لمركز بغداد لتقليل الخطوات على المريض
AREAS_COORDS = {"بغداد - المركز": (33.3152, 44.3661)}

DATA = {
    "أطباء": [
        {"n": "د. علي الركابي", "s": "قلبية", "a": "الحارثية", "lat": 33.3222, "lon": 44.3585, "stars": 5, "slots": ["04:00 PM", "05:00 PM"]},
        {"n": "د. سارة الجبوري", "s": "قلبية", "a": "المنصور", "lat": 33.3251, "lon": 44.3482, "stars": 4, "slots": ["06:00 PM", "07:30 PM"]},
        {"n": "د. ليث ثامر خزعل", "s": "جملة عصبية", "a": "المنصور", "lat": 33.3251, "lon": 44.3482, "stars": 5, "slots": ["04:30 PM", "08:15 PM"]},
        {"n": "د. مريم القيسي", "s": "مفاصل", "a": "الكرادة", "lat": 33.3135, "lon": 44.4291, "stars": 5, "slots": ["05:00 PM", "06:00 PM"]},
        {"n": "د. طه العسكري", "s": "باطنية", "a": "اليرموك", "lat": 33.3121, "lon": 44.3610, "stars": 3, "slots": ["09:00 PM"]}
    ]
}

def calculate_dist(lat1, lon1, lat2, lon2):
    return math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2) * 111.13

if 'step' not in st.session_state: st.session_state.step = 1

# --- الصفحة 1: الدخول (الموقع تلقائي) ---
if st.session_state.step == 1:
    st.markdown('<div class="welcome-title">AI Doctor 🩺</div>', unsafe_allow_html=True)
    name = st.text_input("الأسم الكامل")
    # الموقع يتحدد تلقائياً لمركز بغداد لتوفير التعب على المريض
    st.info("📍 يتم تحديد موقعك حالياً في: بغداد")
    
    if st.button("دخول النظام"):
        if name:
            st.session_state.p_name = name
            st.session_state.u_coords = AREAS_COORDS["بغداد - المركز"]
            st.session_state.step = 2
            st.rerun()
        else:
            st.error("يرجى إدخال الاسم")

# --- الصفحة 2: التحليل والترتيب الذكي ---
elif st.session_state.step == 2:
    st.subheader(f"أهلاً بك {st.session_state.p_name} 👨‍⚕️")
    text = st.text_area("اشرح حالتك بالتفصيل:")

    if st.button("تحليل الحالة"):
        with st.spinner("جاري التحليل الذكي..."):
            try:
                prompt = f"حلل الحالة: '{text}'. حدد الاختصاص (قلبية، باطنية، جملة عصبية، مفاصل)."
                response = model.generate_content(prompt)
                res_text = response.text
                
                st.session_state.spec = "باطنية"
                for s in ["قلبية", "باطنية", "جملة عصبية", "مفاصل"]:
                    if s in res_text:
                        st.session_state.spec = s
                        break
                st.session_state.diag_msg = res_text
                st.session_state.diag_ready = True
            except Exception as e:
                st.error(f"خطأ: {e}")

    if st.session_state.get('diag_ready'):
        st.markdown(f'<div class="diag-box">{st.session_state.diag_msg}</div>', unsafe_allow_html=True)
        
        # --- الترتيب الذكي (الأقرب مسافة والاعلى تقييماً) ---
        st.write(f"### الأطباء المقترحون (الأقرب لك في بغداد):")
        u_lat, u_lon = st.session_state.u_coords
        
        # فلترة وترتيب الأطباء
        matches = [d for d in DATA["أطباء"] if d['s'] == st.session_state.spec]
        for d in matches:
            d['current_dist'] = calculate_dist(u_lat, u_lon, d['lat'], d['lon'])
        
        # ترتيب حسب الأقرب ثم النجوم
        sorted_docs = sorted(matches, key=lambda x: (x['current_dist'], -x['stars']))

        for d in sorted_docs:
            st.markdown(f'''<div class="doc-card">
                <span style="float:left;">{d['current_dist']:.1f} كم 📍</span>
                <b>{d['n']}</b> <span class="star-color">{"★" * d['stars']}</span><br>
                <small>العنوان: {d['a']}</small><br>
                <div style="margin-top:10px;">اختر وقتاً للحجز:</div>
            </div>''', unsafe_allow_html=True)
            
            # عرض المواعيد كأزرار
            cols = st.columns(len(d['slots']))
            for i, slot in enumerate(d['slots']):
                if cols[i].button(slot, key=f"{d['n']}-{slot}"):
                    st.session_state.selected_doc = d
                    st.session_state.final_time = slot
                    st.session_state.step = 3
                    st.rerun()

# --- الصفحة 3: النجاح ---
elif st.session_state.step == 3:
    st.balloons()
    st.markdown(f'''
        <div style="border: 2px solid #40E0D0; padding: 30px; border-radius: 20px; background: rgba(64,224,208,0.1);">
            <h2 style="color: #40E0D0;">تم الحجز بنجاح ✅</h2>
            <p>المريض: <b>{st.session_state.p_name}</b></p>
            <p>الطبيب: <b>{st.session_state.selected_doc['n']}</b></p>
            <p>الوقت: <b>{st.session_state.final_time}</b></p>
            <p>الموقع: <b>{st.session_state.selected_doc['a']}</b></p>
        </div>
    ''', unsafe_allow_html=True)
    if st.button("بدء من جديد"):
        st.session_state.step = 1
        st.rerun()
