import streamlit as st
import hashlib
import math
import time
from datetime import date
from streamlit_js_eval import get_geolocation

# --- 1. التنسيق البصري (Elite Emerald UI) ---
st.set_page_config(page_title="AI Doctor Premium", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    * { font-family: 'Tajawal', sans-serif; direction: rtl; }
    .stApp { background: #050a0b; color: #e0f2f1; }
    
    .main-header { text-align: center; color: #71B280; font-size: 42px; font-weight: 700; margin-top: 20px; }
    
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

# --- 2. البيانات الطبية (المنطق من كودك) ---
DISEASE_PROFILES = {
    "الإنفلونزا الموسمية": {"حمى": 2, "سعال": 1, "آلام الجسم": 1.5, "تعب": 2},
    "نزلات البرد": {"سعال": 1, "احتقان": 1.5, "سيلان": 1.5, "حلق": 1},
    "التهاب رئوي": {"حمى": 2, "سعال": 2, "ضيق نفس": 2, "ألم صدر": 1.5},
    "COVID-19": {"حمى": 1.8, "سعال": 1.5, "فقدان شم": 2, "فقدان تذوق": 2, "ضيق نفس": 1.5},
    "تسمم غذائي": {"غثيان": 2, "قيء": 2, "إسهال": 2, "ألم بطن": 1.5}
}
SYMPTOMS = sorted(list(set([s for p in DISEASE_PROFILES.values() for s in p.keys()])))

DOCTORS = [
    {"name": "د. سامر الحديثي", "spec": "طب عام", "lat": 33.3128, "lon": 44.3615},
    {"name": "د. زينة القيسي", "spec": "جلدية", "lat": 33.3100, "lon": 44.3790},
    {"name": "د. عمر العبيدي", "spec": "باطنية", "lat": 33.3260, "lon": 44.3650}
]

def softmax(x):
    exps = [math.exp(v) for v in x]; s = sum(exps) or 1.0
    return [e/s for e in exps]

# --- 3. إدارة الجلسة (بدلاً من الخزن الدائم) ---
if "auth" not in st.session_state: st.session_state.auth = False
if "temp_users" not in st.session_state: st.session_state.temp_users = {}
if "page" not in st.session_state: st.session_state.page = "login"

st.markdown('<h1 class="main-header">AI Doctor</h1>', unsafe_allow_html=True)

# --- 4. واجهات الدخول والإنشاء ---
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
                    if u in st.session_state.temp_users and st.session_state.temp_users[u] == p:
                        st.session_state.auth = True; st.session_state.user = u; st.rerun()
                    else: st.error("المستخدم غير موجود أو كلمة المرور خطأ")
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
                if st.button("تأكيد"):
                    if nu and np:
                        st.session_state.temp_users[nu] = np
                        st.success("تم الإنشاء بنجاح! جاري التحويل...")
                        time.sleep(1.2)
                        st.session_state.page = "login"; st.rerun()
                    else: st.warning("املأ الحقول")
            with sc2:
                if st.button("رجوع"):
                    st.session_state.page = "login"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- 5. واجهة التشخيص الذكي ---
else:
    with st.sidebar:
        st.write(f"أهلاً {st.session_state.user}")
        if st.button("تسجيل خروج"):
            st.session_state.auth = False; st.rerun()
    
    st.markdown('<div class="portal-box" style="max-width:850px;">', unsafe_allow_html=True)
    st.subheader("الاستشارة الطبية الذكية")
    
    selected = st.multiselect("اختر الأعراض التي تشعر بها:", SYMPTOMS)
    
    if st.button("بدء الفحص 🔍"):
        if selected:
            scores = []
            diseases = list(DISEASE_PROFILES.keys())
            for d in diseases:
                score = sum([DISEASE_PROFILES[d].get(s, 0) for s in selected])
                scores.append(score)
            probs = softmax(scores)
            idx = max(range(len(probs)), key=lambda i: probs[i])
            
            st.markdown(f"### التشخيص المبدئي: *{diseases[idx]}*")
            st.write(f"نسبة الاحتمالية: {probs[idx]*100:.1f}%")
            
            # رصد الموقع
            loc = get_geolocation()
            if loc:
                lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
                st.write("---")
                st.subheader("الأطباء المتاحون في منطقتك:")
                for d in DOCTORS:
                    dist = math.sqrt((lat-d['lat'])*2 + (lon-d['lon'])*2)*111
                    st.markdown(f"""<div class="doc-card">
                        <b>{d['name']}</b> | {d['spec']}<br>يبعد: {dist:.1f} كم
                    </div>""", unsafe_allow_html=True)
            else:
                st.warning("يرجى تفعيل الـ GPS لإظهار المسافات")
        else: st.warning("اختر عرضاً واحداً على الأقل")
    st.markdown('</div>', unsafe_allow_html=True)
