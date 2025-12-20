import streamlit as st
import sqlite3
import hashlib
import math
from datetime import date
from streamlit_js_eval import get_geolocation
import time

# ===== إعداد الصفحة =====
st.set_page_config(page_title="AI Doctor Emerald", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
* { font-family: 'Tajawal', sans-serif; direction: rtl; }
.stApp { background:#e0f2f1; color:#034d34; }
.main-card { max-width:700px; margin:auto; padding:25px; border-radius:15px; background:#ffffffcc; box-shadow:0 5px 15px rgba(0,0,0,0.05);}
.stButton>button { width:100%; height:3em; border-radius:10px; background:linear-gradient(135deg,#138a36,#71b280); color:white; font-weight:bold; }
.doc-card { background:#d0f0e5; padding:15px; border-radius:10px; margin-bottom:10px; border-left:5px solid #138a36;}
.emergency-box { background:#ffebee; color:#c62828; padding:10px; border-radius:10px; font-weight:bold; margin-bottom:15px; text-align:center; }
</style>
""", unsafe_allow_html=True)

# ===== قاعدة البيانات =====
DB_NAME="emerald_doctor.db"
def init_db():
    conn=sqlite3.connect(DB_NAME)
    c=conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS appointments (username TEXT, doctor TEXT, dt TEXT, tm TEXT)")
    conn.commit()
    conn.close()
init_db()

# ===== البيانات الطبية والأطباء =====
SYMPTOMS={
    "ألم في الصدر":{"spec":"قلب وباطنية","emergency":True},
    "ضيق تنفس":{"spec":"قلب وباطنية","emergency":True},
    "حمى شديدة":{"spec":"باطنية","emergency":False},
    "طفح جلدي وحكة":{"spec":"جلدية","emergency":False},
    "خمول عام":{"spec":"باطنية","emergency":False}
}

DOCTORS=[
    {"name":"د. علي الركابي","spec":"قلب وباطنية","lat":33.3128,"lon":44.3615},
    {"name":"د. سارة الحسني","spec":"جلدية","lat":33.3020,"lon":44.4210},
    {"name":"د. ليث السامرائي","spec":"باطنية","lat":33.2750,"lon":44.3750},
    {"name":"د. منى الفارس","spec":"أطفال","lat":33.3350,"lon":44.4410},
    {"name":"د. ياسر القيسي","spec":"قلب وباطنية","lat":33.3000,"lon":44.3800}
]

# ===== دوال =====
def hash_pwd(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

def haversine(lat1, lon1, lat2, lon2):
    R=6371
    dlat=math.radians(lat2-lat1)
    dlon=math.radians(lon2-lon1)
    a=math.sin(dlat/2)*2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)*2
    c=2*math.atan2(math.sqrt(a),math.sqrt(1-a))
    return R*c

# ===== الجلسة =====
if "logged_in" not in st.session_state: st.session_state.logged_in=False
if "user" not in st.session_state: st.session_state.user=""
if "diagnosis" not in st.session_state: st.session_state.diagnosis=None

# ===== تسجيل دخول / حساب جديد =====
if not st.session_state.logged_in:
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("تسجيل الدخول أو إنشاء حساب")
    tab=st.radio("اختر:",["تسجيل دخول","إنشاء حساب"])
    
    if tab=="تسجيل دخول":
        u=st.text_input("اسم المستخدم", key="login_user")
        p=st.text_input("كلمة المرور", type="password", key="login_pass")
        if st.button("دخول"):
            conn=sqlite3.connect(DB_NAME)
            res=conn.execute("SELECT * FROM users WHERE username=? AND password=?",(u,hash_pwd(p))).fetchone()
            conn.close()
            if res:
                st.session_state.logged_in=True
                st.session_state.user=u
                st.rerun()
            else: st.error("البيانات خاطئة")
            
    else:  # إنشاء حساب
        u=st.text_input("اسم مستخدم جديد", key="reg_user")
        p=st.text_input("كلمة المرور", type="password", key="reg_pass")
        if st.button("إنشاء الحساب"):
            if u and p:
                try:
                    conn=sqlite3.connect(DB_NAME)
                    conn.execute("INSERT INTO users VALUES (?,?)",(u,hash_pwd(p)))
                    conn.commit(); conn.close()
                    st.success("تم إنشاء الحساب! جاري تحويلك لتسجيل الدخول...")
                    time.sleep(1.5)
                    st.experimental_rerun()
                except sqlite3.IntegrityError:
                    st.error("الاسم مستخدم مسبقاً! جرب إضافة رقم (مثلاً user123)")
            else:
                st.warning("املأ جميع الحقول")
    st.markdown('</div>', unsafe_allow_html=True)

# ===== بعد تسجيل الدخول =====
else:
    with st.sidebar:
        st.write(f"مرحباً {st.session_state.user}")
        if st.button("تسجيل خروج"):
            st.session_state.logged_in=False
            st.session_state.user=""
            st.session_state.diagnosis=None
            st.rerun()
        menu=st.radio("القائمة:",["استشارة ذكية","مواعيدي"])
    
    # ---- استشارة ذكية ----
    if menu=="استشارة ذكية":
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.subheader("🔍 حدد أعراضك")
        selected=st.multiselect("الأعراض",list(SYMPTOMS.keys()))
        
        if st.button("تحليل"):
            if selected:
                is_em=any([SYMPTOMS[s]["emergency"] for s in selected])
                specs=list(set([SYMPTOMS[s]["spec"] for s in selected]))
                st.session_state.diagnosis={"em":is_em,"specs":specs}
            else:
                st.warning("اختر عرضاً واحداً على الأقل")
        
        if st.session_state.diagnosis:
            diag=st.session_state.diagnosis
            if diag["em"]:
                st.markdown('<div class="emergency-box">⚠️ حالة طارئة! توجّه لأقرب مستشفى.</div>', unsafe_allow_html=True)
            else:
                st.success(f"التخصصات المطلوبة: {', '.join(diag['specs'])}")
            
            st.write("📍 الأطباء المتاحون:")
            loc=get_geolocation()
            for doc in DOCTORS:
                if any(sp in doc["spec"] for sp in diag["specs"]) or diag["em"]:
                    dist_text=""
                    if loc:
                        dist=haversine(loc['coords']['latitude'],loc['coords']['longitude'],doc['lat'],doc['lon'])
                        dist_text=f" | يبعد {dist:.1f} كم"
                    st.markdown(f'<div class="doc-card"><b>{doc["name"]}</b> - {doc["spec"]}{dist_text}</div>', unsafe_allow_html=True)
                    c1,c2=st.columns(2)
                    with c1:
                        sel_date=st.date_input("اليوم", min_value=date.today(), key=f"d_{doc['name']}")
                    with c2:
                        sel_time=st.selectbox("الوقت",["04:00 PM","05:30 PM","07:00 PM"], key=f"t_{doc['name']}")
                    if st.button(f"حجز عند {doc['name']}", key=f"b_{doc['name']}"):
                        conn=sqlite3.connect(DB_NAME)
                        conn.execute("INSERT INTO appointments VALUES (?,?,?,?)",
                                     (st.session_state.user,doc['name'],str(sel_date),sel_time))
                        conn.commit(); conn.close()
                        st.success(f"تم حجز موعدك عند {doc['name']} بتاريخ {sel_date} الساعة {sel_time}!")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ---- مواعيدي ----
    elif menu=="مواعيدي":
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.subheader("📅 مواعيدك")
        conn=sqlite3.connect(DB_NAME)
        data=conn.execute("SELECT doctor, dt, tm FROM appointments WHERE username=? ORDER BY dt",(st.session_state.user,)).fetchall()
        conn.close()
        if data:
            for d,dt,tm in [(row[0],row[1],row[2]) for row in data]:
                st.markdown(f'<div class="doc-card"><b>{d}</b><br>التاريخ: {dt} | الوقت: {tm}</div>', unsafe_allow_html=True)
        else:
            st.info("لم تقم بحجز أي مواعيد بعد.")
        st.markdown('</div>', unsafe_allow_html=True)
