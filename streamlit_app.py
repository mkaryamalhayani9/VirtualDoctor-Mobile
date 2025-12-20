import streamlit as st
import sqlite3
import hashlib
import math
import random
from streamlit_js_eval import get_geolocation

# --- 1. التصميم البصري الفخم ---
st.set_page_config(page_title="Al Doctor AI - Pro", layout="wide")

st.markdown(r'''
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Tajawal:wght@400;700&display=swap');
* { font-family: 'Tajawal', sans-serif; direction: rtl; }
.stApp { background-color: #050505; color: #e0e0e0; }
.classic-logo { font-family: 'Playfair Display', serif; color: #40E0D0; text-align: center; font-size: 50px; margin-bottom: 10px; }
.auth-box { max-width: 400px; margin: auto; padding: 25px; background-color: #0d0d0d; border-radius: 15px; border: 1px solid rgba(64, 224, 208, 0.2); }
.doc-card { background-color: #0d0d0d; padding: 20px; border-radius: 15px; border-right: 6px solid #40E0D0; margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.05); }
.slot-taken { background-color: #222; color: #555; padding: 8px; border-radius: 5px; text-align: center; text-decoration: line-through; font-size: 12px; border: 1px solid #333; }
.slot-avail { background-color: #1d4e4a; color: #40E0D0; padding: 8px; border-radius: 5px; text-align: center; font-size: 12px; font-weight: bold; }
.warning-box { background-color: #332b00; color: #ffcc00; padding: 10px; border-radius: 8px; font-size: 12px; border: 1px solid #ffcc00; margin-top: 10px; text-align: center; }
.stButton>button { background: linear-gradient(135deg, #1d4e4a 0%, #40E0D0 100%); color: #000 !important; font-weight: bold; border-radius: 8px; width: 100%; }
</style>
''', unsafe_allow_html=True)

# --- 2. قاعدة البيانات ---
def init_db():
    conn = sqlite3.connect("al_doctor_final.db")
    conn.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
    conn.commit()
    conn.close()

init_db()

# --- قواعد البيانات ---
SYMPTOMS_DB = {
    "ألم صدر حاد": {"spec": "قلبية", "urgency": 10, "diag": "اشتباه ذبحة", "acc": "89%"},
    "ثقل كلام وتدلي وجه": {"spec": "جملة عصبية", "urgency": 10, "diag": "سكتة دماغية", "acc": "94%"},
    "ضيق تنفس وازرقاق": {"spec": "صدرية", "urgency": 9, "diag": "فشل تنفسي", "acc": "87%"},
    "طفح جلدي قشري": {"spec": "جلدية", "urgency": 3, "diag": "صدفية", "acc": "93%"},
}

DOCTORS_DB = [
    {"name": "د. علي الركابي", "title": "استشاري قلبية", "spec": "قلبية", "area": "الحارثية", "lat": 33.322, "lon": 44.358},
    {"name": "د. عمر الجبوري", "title": "أخصائي جملة عصبية", "spec": "جملة عصبية", "area": "المنصور", "lat": 33.325, "lon": 44.348},
    {"name": "د. سارة لؤي", "title": "أخصائية جلدية", "spec": "جلدية", "area": "زيونة", "lat": 33.332, "lon": 44.455},
]

# --- وظائف ---
if "view" not in st.session_state:
    st.session_state.view = "login"

def safe_dist(u_loc, d_lat, d_lon):
    try:
        lat1, lon1 = u_loc['coords']['latitude'], u_loc['coords']['longitude']
        return round(math.sqrt((lat1-d_lat)*2 + (lon1-d_lon)*2) * 111, 1)
    except:
        return 0.0

st.markdown('<div class="classic-logo">Al Doctor</div>', unsafe_allow_html=True)

# --- واجهة التطبيق ---
if st.session_state.view == "app":

    user_location = get_geolocation()

    st.markdown('<div class="auth-box" style="max-width:500px">', unsafe_allow_html=True)
    selected = st.multiselect("حدد الأعراض:", list(SYMPTOMS_DB.keys()))
    if st.button("شخص الآن وحدد أقرب طبيب 🔍"):
        if selected:
            st.session_state.active_s = selected
    st.markdown('</div>', unsafe_allow_html=True)

    if "active_s" in st.session_state:
        main_s = max(st.session_state.active_s, key=lambda s: SYMPTOMS_DB[s]['urgency'])
        info = SYMPTOMS_DB[main_s]

        st.success(f"🤖 تحليل الذكاء الاصطناعي: {info['diag']} (دقة {info['acc']})")
        st.markdown(f'<div class="warning-box">⚠️ هذا تشخيص استرشادي فقط</div>', unsafe_allow_html=True)

        st.markdown(f'<div style="font-size:20px;font-weight:bold;">التخصص المطلوب: {info["spec"]}</div>', unsafe_allow_html=True)

        for d in DOCTORS_DB:
            if d['spec'] == info['spec']:
                st.markdown(f'''
                <div class="doc-card">
                    <b>{d['name']}</b><br>
                    {d['title']} – {d['area']}
                </div>
                ''', unsafe_allow_html=True)
