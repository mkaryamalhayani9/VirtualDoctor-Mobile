import streamlit as st
import sqlite3
import hashlib
import math
import time
from datetime import datetime
from streamlit_js_eval import get_geolocation

# --- 1. التصميم البصري الفخم ---
st.set_page_config(page_title="AI Doctor Premium", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    * { font-family: 'Tajawal', sans-serif; direction: rtl; }
    .stApp { background: #050a0b; color: #e0f2f1; }
    .main-header { text-align: center; color: #71B280; font-size: 35px; font-weight: 700; margin-bottom: 20px; }
    .portal-box { max-width: 600px; margin: auto; padding: 25px; background: rgba(255, 255, 255, 0.05); border-radius: 15px; border: 1px solid #71B28033; }
    .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; background: linear-gradient(135deg, #134E5E 0%, #71B280 100%); color: white; border: none; height: 3em; }
    .doc-card { background: rgba(113, 178, 128, 0.1); padding: 10px; border-radius: 8px; border-right: 4px solid #71B280; margin-top: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إدارة قاعدة البيانات (الحل النهائي لمشكلة الاسم مأخوذ) ---
# استخدام اسم ملف جديد وفريد لضمان تجاوز الذاكرة المؤقتة للسيرفر
DB_NAME = "final_fix_v10.db"

def setup_database():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # إنشاء الجدول إذا لم يكن موجوداً
    c.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)")
    conn.commit()
    conn.close()

setup_database()

# --- 3. البيانات الطبية المدمجة ---
SYMPTOMS_DATA = {
    "ألم في الصدر": {"spec": "أمراض القلب", "emergency": True},
    "ضيق تنفس": {"spec": "أمراض صدرية", "emergency": True},
    "حمى وسعال": {"spec": "باطنية", "emergency": False},
    "حكة وطفح جلدي": {"spec": "جلدية", "emergency": False},
    "ألم مفاصل": {"spec": "عظام ومفاصل", "emergency": False}
}

DOCTORS = [
    {"name": "د. أحمد (طوارئ)", "spec": "أمراض القلب", "lat": 33.34, "lon": 44.41},
    {"name": "د. ليلى (باطنية)", "spec": "باطنية", "lat": 33.31, "lon": 44.37},
    {"name": "د. حسن (جلدية)", "spec": "جلدية", "lat": 33.36, "lon": 44.40}
]

# --- 4. منطق الجلسة والتنقل ---
if "is_logged_in" not in st.session_state: st.session_state.is_logged_in = False
if "current_page" not in st.session_state: st.session_state.current_page = "login"
if "diagnosis_data" not in st.session_state: st.session_state.diagnosis_data = None

st.markdown('<h1 class="main-header">AI Doctor Pro</h1>', unsafe_allow_html=True)

# --- 5. واجهات التسجيل والدخول ---
if not st.session_state.is_logged_in:
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown('<div class="portal-box">', unsafe_allow_html=True)
        
        if st.session_state.current_page == "login":
            st.subheader("تسجيل الدخول")
            user_in = st.text_input("اسم المستخدم", key="l_user")
            pass_in = st.text_input("كلمة المرور", type="password", key="l_pass")
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button("دخول"):
                    hashed = hashlib.sha256(pass_in.encode()).hexdigest()
                    conn = sqlite3.connect(DB_NAME)
                    res = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (user_in, hashed)).fetchone()
                    conn.close()
                    if res:
                        st.session_state.is_logged_in = True
                        st.session_state.username = user_in
                        st.rerun()
                    else: st.error("تأكد من البيانات")
            with c2:
                if st.button("إنشاء حساب جديد"):
                    st.session_state.current_page = "signup"; st.rerun()

        elif st.session_state.current_page == "signup":
            st.subheader("إنشاء مستخدم جديد")
            new_user = st.text_input("اختر اسماً فريداً", key="s_user")
            new_pass = st.text_input("اختر كلمة مرور", type="password", key="s_pass")
            
            sc1, sc2 = st.columns(2)
            with sc1:
                if st.button("تأكيد التسجيل"):
                    if new_user and new_pass:
                        try:
                            hashed_p = hashlib.sha256(new_pass.encode()).hexdigest()
                            conn = sqlite3.connect(DB_NAME)
                            conn.execute("INSERT INTO users (username, password) VALUES (?,?)", (new_user, hashed_p))
                            conn.commit(); conn.close()
                            st.success("تم الإنشاء! جاري التحويل للدخول...")
                            time.sleep(1.5)
                            st.session_state.current_page = "login"; st.rerun()
                        except sqlite3.IntegrityError:
                            st.error("الاسم مأخوذ! جرب إضافة رقم للاسم (مثلاً: user123)")
                    else: st.warning("املأ الحقول")
            with sc2:
                if st.button("رجوع"):
                    st.session_state.current_page = "login"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- 6. واجهة الطبيب (بعد الدخول) ---
else:
    with st.sidebar:
        st.write(f"أهلاً {st.session_state.username}")
        if st.button("خروج"):
            st.session_state.is_logged_in = False; st.rerun()

    st.markdown('<div class="portal-box" style="max-width:850px;">', unsafe_allow_html=True)
    st.subheader("الاستشارة والبحث الذكي")
    
    selected_syms = st.multiselect("ما هي الأعراض؟", list(SYMPTOMS_DATA.keys()))
    
    if st.button("بدء التحليل الفوري 🔍"):
        if selected_syms:
            is_em = any([SYMPTOMS_DATA[s]["emergency"] for s in selected_syms])
            specs_needed = list(set([SYMPTOMS_DATA[s]["spec"] for s in selected_syms]))
            st.session_state.diagnosis_data = {"em": is_em, "specs": specs_needed}
        else: st.warning("اختر الأعراض")

    if st.session_state.diagnosis_data:
        diag = st.session_state.diagnosis_data
        if diag["em"]:
            st.error("⚠️ حالة طوارئ! توجه لأقرب مستشفى.")
        else:
            st.success(f"الاختصاص المطلوب: {', '.join(diag['specs'])}")

        st.write("---")
        st.write("📍 أقرب الأطباء المتاحين:")
        loc = get_geolocation()
        for doc in DOCTORS:
            if any(sp in doc["spec"] for sp in diag["specs"]) or diag["em"]:
                dist_txt = ""
                if loc:
                    d = math.sqrt((loc['coords']['latitude']-doc['lat'])*2 + (loc['coords']['longitude']-doc['lon'])*2)*111
                    dist_txt = f" | يبعد: {d:.1f} كم"
                st.markdown(f'<div class="doc-card"><b>{doc["name"]}</b> - {doc["spec"]} {dist_txt}</div>', unsafe_allow_html=True)
                if st.button(f"حجز عند {doc['name']}", key=doc['name']):
                    st.success("تم الحجز!")
    st.markdown('</div>', unsafe_allow_html=True)
