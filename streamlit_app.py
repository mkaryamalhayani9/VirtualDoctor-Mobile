import streamlit as st
import sqlite3
import hashlib
import math
import time
from datetime import datetime
from streamlit_js_eval import get_geolocation

# --- 1. التصميم البصري (Emerald Elite UI) ---
st.set_page_config(page_title="AI Doctor Premium", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    * { font-family: 'Tajawal', sans-serif; direction: rtl; }
    .stApp { background: #050a0b; color: #e0f2f1; }
    .main-header { text-align: center; color: #71B280; font-size: 40px; font-weight: 700; margin-bottom: 20px; }
    .portal-box { max-width: 650px; margin: auto; padding: 30px; background: rgba(255, 255, 255, 0.04); border-radius: 20px; border: 1px solid rgba(113, 178, 128, 0.2); }
    .emergency-banner { background: #631a1a; padding: 15px; border-radius: 12px; border: 2px solid #ff4b4b; text-align: center; margin: 10px 0; }
    .doc-card { background: rgba(113, 178, 128, 0.1); padding: 12px; border-radius: 10px; border-right: 5px solid #71B280; margin-top: 10px; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3.2em; font-weight: bold; background: linear-gradient(135deg, #134E5E 0%, #71B280 100%); color: white; border: none; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إعداد قاعدة البيانات (حل مشكلة الاسم مأخوذ باستخدام نسخة فريدة) ---
DB_NAME = "ai_doc_v9.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (u TEXT PRIMARY KEY, p TEXT)")
    conn.commit()
    conn.close()

init_db()

# --- 3. البيانات الطبية ---
SYMPTOMS_DB = {
    "ألم حاد في الصدر": {"spec": "أمراض القلب والشرايين", "level": "High"},
    "صعوبة شديدة في التنفس": {"spec": "الأمراض الصدرية / الطوارئ", "level": "High"},
    "حمى شديدة (أكثر من 39)": {"spec": "الباطنية", "level": "Medium"},
    "طفح جلدي وحكة": {"spec": "الجلدية والتجميل", "level": "Low"},
    "غثيان وقيء مستمر": {"spec": "الجهاز الهضمي", "level": "Medium"},
    "ألم أسفل الظهر": {"spec": "المفاصل والكسور", "level": "Low"},
    "صداع نصفي حاد": {"spec": "الأعصاب", "level": "Medium"}
}

DOCTORS = [
    {"name": "د. علي الهاشمي", "spec": "أمراض القلب والشرايين", "lat": 33.3474, "lon": 44.4101},
    {"name": "د. سارة المنصور", "spec": "الجلدية والتجميل", "lat": 33.3128, "lon": 44.3615},
    {"name": "د. عمر العبيدي", "spec": "الأمراض الصدرية / الطوارئ", "lat": 33.3020, "lon": 44.3790}
]

# --- 4. إدارة الجلسة ---
if "auth" not in st.session_state: st.session_state.auth = False
if "page" not in st.session_state: st.session_state.page = "login"
if "diag_res" not in st.session_state: st.session_state.diag_res = None

st.markdown('<h1 class="main-header">AI Doctor Pro</h1>', unsafe_allow_html=True)

# --- 5. واجهة تسجيل الدخول والإنشاء ---
if not st.session_state.auth:
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown('<div class="portal-box">', unsafe_allow_html=True)
        if st.session_state.page == "login":
            st.subheader("تسجيل الدخول")
            u = st.text_input("اسم المستخدم")
            p = st.text_input("كلمة المرور", type="password")
            st.write("")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("دخول"):
                    hp = hashlib.sha256(p.encode()).hexdigest()
                    conn = sqlite3.connect(DB_NAME)
                    user = conn.execute("SELECT * FROM users WHERE u=? AND p=?", (u, hp)).fetchone()
                    conn.close()
                    if user:
                        st.session_state.auth = True; st.session_state.username = u; st.rerun()
                    else: st.error("بيانات خاطئة")
            with c2:
                if st.button("حساب جديد"):
                    st.session_state.page = "signup"; st.rerun()

        elif st.session_state.page == "signup":
            st.subheader("إنشاء حساب جديد")
            nu = st.text_input("اختار اسم مستخدم")
            np = st.text_input("اختار كلمة مرور", type="password")
            st.write("")
            sc1, sc2 = st.columns(2)
            with sc1:
                if st.button("تأكيد"):
                    if nu and np:
                        try:
                            hnp = hashlib.sha256(np.encode()).hexdigest()
                            conn = sqlite3.connect(DB_NAME)
                            conn.execute("INSERT INTO users VALUES (?,?)", (nu, hnp))
                            conn.commit(); conn.close()
                            st.success("تم بنجاح! جاري التحويل...")
                            time.sleep(1.2); st.session_state.page = "login"; st.rerun()
                        except: st.error("عذراً، هذا الاسم مأخوذ")
            with sc2:
                if st.button("رجوع"):
                    st.session_state.page = "login"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- 6. واجهة التشخيص بعد الدخول ---
else:
    with st.sidebar:
        st.write(f"مرحباً، {st.session_state.username}")
        if st.button("خروج"):
            st.session_state.auth = False; st.rerun()

    st.markdown('<div class="portal-box" style="max-width:900px;">', unsafe_allow_html=True)
    st.subheader("تحليل الحالة والبحث عن طبيب")
    
    selected = st.multiselect("اختر الأعراض:", list(SYMPTOMS_DB.keys()))
    
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("بدء الفحص 🔍"):
            if selected:
                is_h = any([SYMPTOMS_DB[s]["level"] == "High" for s in selected])
                specs = list(set([SYMPTOMS_DB[s]["spec"] for s in selected]))
                st.session_state.diag_res = {"emergency": is_h, "specs": specs, "time": datetime.now().strftime("%H:%M")}
            else: st.warning("حدد عرضاً")
    with col_b:
        if st.button("تصفير 🗑️"):
            st.session_state.diag_res = None; st.rerun()

    if st.session_state.diag_res:
        res = st.session_state.diag_res
        if res["emergency"]:
            st.markdown('<div class="emergency-banner">⚠️ <b>حالة طوارئ!</b> يرجى مراجعة أقرب مستشفى فوراً</div>', unsafe_allow_html=True)
        else:
            st.success(f"الاختصاص المطلوب لمراجعتك: {', '.join(res['specs'])}")

        # عرض الأطباء والمواقع
        st.write("📍 *الأطباء المتاحون لموقعك واختصاصك:*")
        loc = get_geolocation()
        for doc in DOCTORS:
            if any(s in doc["spec"] for s in res["specs"]) or res["emergency"]:
                d_str = "جاري تحديد المسافة..."
                if loc:
                    dist = math.sqrt((loc['coords']['latitude']-doc['lat'])*2 + (loc['coords']['longitude']-doc['lon'])*2)*111
                    d_str = f"يبعد {dist:.1f} كم"
                
                st.markdown(f'<div class="doc-card"><b>{doc["name"]}</b><br>الاختصاص: {doc["spec"]} | {d_str}</div>', unsafe_allow_html=True)
                if st.button(f"حجز موعد {doc['name']}", key=doc['name']):
                    st.success("تم الحجز بنجاح!")
    st.markdown('</div>', unsafe_allow_html=True)
