import streamlit as st
import sqlite3
import hashlib
import math
import time
from datetime import datetime, date
from streamlit_js_eval import get_geolocation

# --- 1. التنسيق البصري (Premium Emerald UI) ---
st.set_page_config(page_title="AI Doctor Premium", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    * { font-family: 'Tajawal', sans-serif; direction: rtl; }
    .stApp { background: #050a0b; color: #e0f2f1; }
    
    .main-header { text-align: center; color: #71B280; font-size: 42px; font-weight: 700; margin-top: 10px; }
    
    .portal-box {
        max-width: 500px; margin: auto; padding: 30px;
        background: rgba(255, 255, 255, 0.04); border-radius: 20px;
        border: 1px solid rgba(113, 178, 128, 0.2);
        box-shadow: 0 15px 45px rgba(0,0,0,0.6);
    }

    .stButton>button {
        width: 100%; border-radius: 12px; height: 3.2em; font-weight: bold;
        background: linear-gradient(135deg, #134E5E 0%, #71B280 100%); color: white; border: none;
    }
    
    .stTextInput>div>div>input {
        background: #0d1b1e !important; color: white !important;
        text-align: right; border-radius: 10px !important;
    }

    .doc-card {
        background: rgba(113, 178, 128, 0.1); padding: 15px; border-radius: 12px;
        border-right: 5px solid #71B280; margin-top: 15px; text-align: right;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. البيانات والمنطق الطبي ---
DB_FILE = "medical_system_v4.db"

DISEASE_PROFILES = {
    "الإنفلونزا الموسمية": {"حمى": 2, "سعال": 1, "آلام الجسم": 1.5, "تعب": 2},
    "نزلات البرد": {"سعال": 1, "احتقان": 1.5, "سيلان": 1.5, "حلق": 1},
    "التهاب رئوي": {"حمى": 2, "سعال": 2, "ضيق نفس": 2, "ألم صدر": 1.5},
    "COVID-19": {"حمى": 1.8, "سعال": 1.5, "فقدان شم": 2, "فقدان تذوق": 2, "ضيق نفس": 1.5},
    "تسمم غذائي": {"غثيان": 2, "قيء": 2, "إسهال": 2, "ألم بطن": 1.5}
}

SYMPTOMS = sorted(list(set([s for p in DISEASE_PROFILES.values() for s in p.keys()])))

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (u TEXT PRIMARY KEY, p TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS docs (name TEXT, spec TEXT, lat REAL, lon REAL)")
    c.execute("SELECT COUNT(*) FROM docs")
    if c.fetchone()[0] == 0:
        c.executemany("INSERT INTO docs VALUES (?,?,?,?)", [
            ("د. سامر الحديثي", "طب عام", 33.3128, 44.3615),
            ("د. زينة القيسي", "جلدية", 33.3100, 44.3790),
            ("د. عمر العبيدي", "باطنية", 33.3260, 44.3650)
        ])
    conn.commit()
    conn.close()

def softmax(x):
    exps = [math.exp(v) for v in x]; s = sum(exps) or 1.0
    return [e/s for e in exps]

init_db()

# --- 3. إدارة الجلسة ---
if "auth" not in st.session_state: st.session_state.auth = False
if "page" not in st.session_state: st.session_state.page = "login"

st.markdown('<h1 class="main-header">AI Doctor</h1>', unsafe_allow_html=True)

# --- 4. واجهة الدخول والإنشاء ---
if not st.session_state.auth:
    _, col, _ = st.columns([1, 1.8, 1])
    with col:
        st.markdown('<div class="portal-box">', unsafe_allow_html=True)
        if st.session_state.page == "login":
            st.markdown("<h3 style='text-align:center;'>تسجيل الدخول</h3>", unsafe_allow_html=True)
            u = st.text_input("اسم المستخدم")
            p = st.text_input("كلمة المرور", type="password")
            st.write("")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("دخول"):
                    hp = hashlib.sha256(p.encode()).hexdigest()
                    conn = sqlite3.connect(DB_FILE)
                    res = conn.execute("SELECT * FROM users WHERE u=? AND p=?", (u, hp)).fetchone()
                    conn.close()
                    if res:
                        st.session_state.auth = True; st.session_state.user = u; st.rerun()
                    else: st.error("خطأ في البيانات")
            with c2:
                if st.button("حساب جديد"):
                    st.session_state.page = "signup"; st.rerun()

        elif st.session_state.page == "signup":
            st.markdown("<h3 style='text-align:center;'>إنشاء حساب جديد</h3>", unsafe_allow_html=True)
            nu = st.text_input("اسم المستخدم الجديد")
            np = st.text_input("كلمة المرور الجديدة", type="password")
            st.write("")
            sc1, sc2 = st.columns(2)
            with sc1:
                if st.button("تأكيد التسجيل"):
                    if nu and np:
                        try:
                            hnp = hashlib.sha256(np.encode()).hexdigest()
                            conn = sqlite3.connect(DB_FILE)
                            conn.execute("INSERT INTO users VALUES (?,?)", (nu, hnp))
                            conn.commit(); conn.close()
                            st.success("تم الإنشاء! جاري التحويل...")
                            time.sleep(1.5)
                            st.session_state.page = "login"; st.rerun()
                        except: st.error("الاسم مأخوذ")
            with sc2:
                if st.button("رجوع"):
                    st.session_state.page = "login"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- 5. واجهة التشخيص بعد الدخول ---
else:
    with st.sidebar:
        st.markdown(f"### مرحباً {st.session_state.user}")
        if st.button("تسجيل خروج"):
            st.session_state.auth = False; st.rerun()
    
    st.markdown('<div class="portal-box" style="max-width:800px;">', unsafe_allow_html=True)
    st.subheader("الاستشارة الطبية الذكية")
    
    selected = st.multiselect("اختر الأعراض التي تشعر بها:", SYMPTOMS)
    
    if st.button("تحليل الحالة 🔍"):
        if selected:
            # خوارزمية التشخيص
            scores = []
            diseases = list(DISEASE_PROFILES.keys())
            for d in diseases:
                profile = DISEASE_PROFILES[d]
                score = sum([profile.get(s, 0) for s in selected])
                scores.append(score)
            probs = softmax(scores)
            top_idx = max(range(len(probs)), key=lambda i: probs[i])
            
            st.markdown(f"### التشخيص المبدئي: *{diseases[top_idx]}*")
            st.progress(probs[top_idx])
            st.write(f"نسبة التأكد: {probs[top_idx]*100:.1f}%")
            
            # رصد الموقع والأطباء
            loc = get_geolocation()
            if loc:
                u_lat, u_lon = loc['coords']['latitude'], loc['coords']['longitude']
                conn = sqlite3.connect(DB_FILE)
                docs = conn.execute("SELECT * FROM docs").fetchall()
                conn.close()
                
                st.write("---")
                st.subheader("أقرب الأطباء المتاحين:")
                for d in docs:
                    dist = math.sqrt((u_lat-d[2])*2 + (u_lon-d[3])*2)*111
                    st.markdown(f"""
                    <div class="doc-card">
                        <b>{d[0]}</b> | تخصص: {d[1]}<br>
                        المسافة: {dist:.1f} كم
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"حجز موعد عند {d[0]}", key=d[0]):
                        st.success("تم إرسال طلب الحجز بنجاح!")
            else:
                st.warning("يرجى تفعيل الـ GPS لإظهار الأطباء الأقرب إليك")
        else:
            st.warning("يرجى اختيار عرض واحد على الأقل")
    st.markdown('</div>', unsafe_allow_html=True)
