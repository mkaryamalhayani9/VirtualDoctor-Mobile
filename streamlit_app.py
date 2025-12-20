import streamlit as st
import sqlite3
import hashlib
import math
import random
from datetime import datetime, time
from streamlit_js_eval import get_geolocation

# --- 1. التصميم البصري الفخم ---
st.set_page_config(page_title="Al Doctor Premium AI", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    * { font-family: 'Tajawal', sans-serif; direction: rtl; }
    .stApp { background: #050505; color: #e0e0e0; }
    .classic-logo { color: #40E0D0; text-align: center; font-size: 40px; font-weight: bold; margin-bottom: 20px; }
    .auth-box { max-width: 380px; margin: auto; padding: 20px; background: #0d0d0d; border-radius: 12px; border: 1px solid #40E0D033; }
    .doc-card …
[10:29 PM, 12/20/2025] M. K. Al-Hayani: import streamlit as st
import sqlite3
import hashlib
from datetime import datetime, time, timedelta
import random
from streamlit_js_eval import get_geolocation

# --- 1. الإعدادات والتصميم ---
st.set_page_config(page_title="Al Doctor AI - v9", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    * { font-family: 'Tajawal', sans-serif; direction: rtl; }
    .stApp { background: #050505; color: #e0e0e0; }
    .doc-card { 
        background: #0d0d0d; padding: 20px; border-radius: 15px; 
        border-right: 6px solid #40E0D0; margin-bottom: 15px; border: 1px solid #ffffff05;
    }
    .time-slot {
        display: inline-block; padding: 8px 12px; margin: 5px; border-radius: 5px;
        font-size: 13px; font-weight: bold; cursor: pointer;
    }
    .slot-available { background: #1d4e4a; color: #40E0D0; border: 1px solid #40E0D0; }
    .slot-taken { background: #222; color: #555; border: 1px solid #333; text-decoration: line-through; cursor: not-allowed; }
    .emergency-tag { background: #ff4b4b; color: white; padding: 4px 10px; border-radius: 5px; font-size: 12px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. محرك توليد المواعيد الوهمي ---
def get_appointment_slots(doc_id):
    # نستخدم doc_id كبذرة (seed) لتبقى المواعيد ثابتة خلال الجلسة
    random.seed(doc_id)
    slots = []
    start_h = 9
    for i in range(12): # 12 موعد خلال اليوم
        t = f"{start_h + (i//2)}:{'00' if i%2==0 else '30'}"
        is_taken = random.choice([True, False])
        slots.append({"time": t, "taken": is_taken})
    return slots

# --- 3. قاعدة البيانات الطبية الموسعة ---
MEDICAL_LOGIC = {
    "ألم صدر": {"spec": "قلبية", "urgency": 10},
    "ضيق تنفس": {"spec": "صدرية", "urgency": 9},
    "صداع شديد": {"spec": "جملة عصبية", "urgency": 7},
    "ألم بطن": {"spec": "جراحة عامة", "urgency": 6},
    "تشوش رؤية": {"spec": "عيون", "urgency": 8}
}

# بيانات المستشفيات الفعلية في بغداد (تقريبية للموقع)
HOSPITALS = [
    {"name": "مستشفى ابن الهيثم", "spec": "عيون", "lat": 33.313, "lon": 44.429, "type": "حكومي"},
    {"name": "مستشفى عشتار الأهلي", "spec": "عام", "lat": 33.313, "lon": 44.434, "type": "أهلي"},
    {"name": "مركز ابن البيطار", "spec": "قلبية", "lat": 33.327, "lon": 44.388, "type": "تخصصي"},
    {"name": "مستشفى ابن سينا", "spec": "عام", "lat": 33.311, "lon": 44.406, "type": "تخصصي"},
    {"name": "مستشفى الراهبات", "spec": "عام", "lat": 33.307, "lon": 44.422, "type": "أهلي"}
]

# --- 4. واجهة المستخدم ---
st.title("🏥 نظام Al Doctor للحجز الذكي")

# تحديد الموقع
loc = get_geolocation()
if not loc:
    st.warning("الرجاء السماح بالوصول للموقع لتحديد أقرب مستشفى.")
else:
    u_lat = loc['coords']['latitude']
    u_lon = loc['coords']['longitude']

    # 1. اختيار عدة أعراض
    symptoms = st.multiselect("ما هي الأعراض التي تعاني منها؟ (يمكنك اختيار أكثر من عارض)", 
                             list(MEDICAL_LOGIC.keys()))

    if symptoms:
        # حساب أقصى درجة طوارئ بين الأعراض المختارة
        max_urgency = max([MEDICAL_LOGIC[s]['urgency'] for s in symptoms])
        specs_needed = list(set([MEDICAL_LOGIC[s]['spec'] for s in symptoms]))

        st.subheader("📍 المراكز المتاحة (مرتبة حسب الأقرب لك)")
        
        # حساب المسافة وترتيب النتائج
        import math
        def dist(l1, o1, l2, o2): return math.sqrt((l1-l2)*2 + (o1-o2)*2) * 111

        sorted_hospitals = sorted(HOSPITALS, key=lambda h: dist(u_lat, u_lon, h['lat'], h['lon']))

        for h in sorted_hospitals:
            d_km = dist(u_lat, u_lon, h['lat'], h['lon'])
            
            with st.container():
                st.markdown(f"""
                <div class="doc-card">
                    <div style="display:flex; justify-content:space-between">
                        <b style="color:#40E0D0; font-size:18px">{h['name']}</b>
                        <span>⏱️ يبعد عنك {d_km:.1f} كم</span>
                    </div>
                    <p>{h['type']} - تخصص: {h['spec']}</p>
                    {"<span class='emergency-tag'>🚨 متاح للطوارئ فوراً</span>" if max_urgency > 8 else ""}
                </div>
                """, unsafe_allow_html=True)
                
                # عرض المواعيد
                st.write("*جدول المواعيد لليوم:*")
                slots = get_appointment_slots(h['name']) # توليد مواعيد ثابتة لكل مركز
                
                cols = st.columns(6)
                for idx, s in enumerate(slots):
                    with cols[idx % 6]:
                        if s['taken']:
                            st.markdown(f'<div class="time-slot slot-taken">{s["time"]}</div>', unsafe_allow_html=True)
                        else:
                            if st.button(s['time'], key=f"{h['name']}_{s['time']}"):
                                st.success(f"تم تأكيد حجزك في {h['name']} الساعة {s['time']}")
                                st.balloons()
