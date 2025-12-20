import streamlit as st
import math
import time
from datetime import datetime
from streamlit_js_eval import get_geolocation

# --- 1. التنسيق البصري ---
st.set_page_config(page_title="AI Doctor Premium", layout="wide")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    * { font-family: 'Tajawal', sans-serif; direction: rtl; }
    .stApp { background: #050a0b; color: #e0f2f1; }
    .portal-box { max-width: 800px; margin: auto; padding: 25px; background: rgba(255, 255, 255, 0.04); border-radius: 20px; border: 1px solid rgba(113, 178, 128, 0.2); }
    .emergency-box { background: #4a1a1a; border: 2px solid #ff4b4b; padding: 15px; border-radius: 12px; text-align: center; margin-bottom: 20px; }
    .doc-card { background: rgba(113, 178, 128, 0.1); padding: 12px; border-radius: 10px; border-right: 5px solid #71B280; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. البيانات الطبية ---
DISEASE_PROFILES = {
    "ألم صدر حاد": {"spec": "قلبية", "emergency": True},
    "ضيق نفس شديد": {"spec": "جهاز تنفسي", "emergency": True},
    "حمى وسعال": {"spec": "باطنية", "emergency": False},
    "طفح جلدي": {"spec": "جلدية", "emergency": False},
    "ألم مفاصل": {"spec": "مفاصل وعظام", "emergency": False}
}

DOCTORS = [
    {"name": "د. سامر (طوارئ الكندي)", "spec": "قلبية", "lat": 33.3474, "lon": 44.4101},
    {"name": "د. زينة (عيادة النجاة)", "spec": "باطنية", "lat": 33.3100, "lon": 44.3790},
    {"name": "د. عمر (مستشفى العالمي)", "spec": "جهاز تنفسي", "lat": 33.3623, "lon": 44.4023}
]

# --- 3. إدارة الجلسة (لحفظ النتائج) ---
if "diagnosis_result" not in st.session_state: st.session_state.diagnosis_result = None
if "auth" not in st.session_state: st.session_state.auth = True # مؤقت للتجربة

st.markdown("<h1 style='text-align:center; color:#71B280;'>AI Doctor Pro</h1>", unsafe_allow_html=True)

# واجهة التشخيص
if st.session_state.auth:
    _, col, _ = st.columns([1, 3, 1])
    with col:
        st.markdown('<div class="portal-box">', unsafe_allow_html=True)
        st.subheader("📋 تشخيص الحالة وتحديد الموعد")
        
        selected_symptoms = st.multiselect("اختر الأعراض التي تشعر بها:", list(DISEASE_PROFILES.keys()))
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("تحليل الحالة 🔍"):
                if selected_symptoms:
                    # منطق تحديد الحالة والطوارئ
                    is_emergency = any([DISEASE_PROFILES[s]["emergency"] for s in selected_symptoms])
                    specs = list(set([DISEASE_PROFILES[s]["spec"] for s in selected_symptoms]))
                    
                    # حفظ النتيجة في الجلسة لكي لا تختفي
                    st.session_state.diagnosis_result = {
                        "emergency": is_emergency,
                        "specs": specs,
                        "time": datetime.now().strftime("%H:%M")
                    }
                else:
                    st.warning("يرجى اختيار عرض واحد على الأقل")
        
        with col_btn2:
            if st.button("مسح النتائج 🗑️"):
                st.session_state.diagnosis_result = None
                st.rerun()

        # --- عرض النتائج (إذا كانت موجودة في الجلسة) ---
        if st.session_state.diagnosis_result:
            res = st.session_state.diagnosis_result
            st.write("---")
            
            if res["emergency"]:
                st.markdown('<div class="emergency-box">⚠️ <b>حالة طوارئ!</b> يرجى التوجه لأقرب مستشفى فوراً</div>', unsafe_allow_html=True)
            else:
                st.success(f"✅ الحالة مستقرة. الاختصاص المطلوب: {', '.join(res['specs'])}")

            # تحديد الموقع وعرض الأطباء
            st.write("📍 *الأطباء والاختصاصات المتاحة حالياً:*")
            loc = get_geolocation()
            
            for doc in DOCTORS:
                # فلترة الأطباء حسب الاختصاص المطلوب
                if any(s in doc["spec"] for s in res["specs"]) or res["emergency"]:
                    dist_str = ""
                    if loc:
                        dist = math.sqrt((loc['coords']['latitude']-doc['lat'])*2 + (loc['coords']['longitude']-doc['lon'])*2)*111
                        dist_str = f" | يبعد: {dist:.1f} كم"
                    
                    st.markdown(f"""
                    <div class="doc-card">
                        <b>{doc['name']}</b> - اختصاص {doc['spec']} {dist_str}<br>
                        <small>أقرب موعد متاح: اليوم {res['time']}</small>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"حجز موعد عند {doc['name']}", key=doc['name']):
                        st.balloons()
                        st.success(f"تم حجز موعدك بنجاح عند {doc['name']}")

        st.markdown('</div>', unsafe_allow_html=True)
