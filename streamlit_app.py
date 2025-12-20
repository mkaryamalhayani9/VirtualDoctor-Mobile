import streamlit as st
import sqlite3
import math
from datetime import date
from streamlit_js_eval import get_geolocation

# --- 1. التصميم (Classic Emerald Portal) ---
st.set_page_config(page_title="Emerald Medical Portal", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@500;700&display=swap');
    * { font-family: 'Tajawal', sans-serif; direction: rtl; }
    .stApp { background: #050a0b; color: #e0f2f1; }
    
    /* حاوية متوسطة الحجم ومرتبة */
    .portal-box {
        max-width: 550px;
        margin: 40px auto;
        padding: 35px;
        background: rgba(255, 255, 255, 0.04);
        border-radius: 20px;
        border: 1px solid rgba(113, 178, 128, 0.2);
        box-shadow: 0 15px 45px rgba(0,0,0,0.5);
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #134E5E 0%, #71B280 100%);
        color: white; border-radius: 12px; height: 3.5em; border: none; 
        font-weight: 700; width: 100%; font-size: 16px;
    }
    h2 { color: #71B280; text-align: center; font-size: 28px; margin-bottom: 25px; }
    .stTextInput>div>div>input { text-align: right; background: #0d1b1e !important; color: white !important; border-radius: 10px; }
    
    /* تصميم البطاقات الصغيرة للمحتوى */
    .info-card {
        background: rgba(113, 178, 128, 0.1);
        padding: 15px;
        border-radius: 12px;
        border-right: 5px solid #71B280;
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إدارة قاعدة البيانات ---
def get_db():
    # اتصال يضمن عدم القفل
    return sqlite3.connect("virtual_doctor.db", check_same_thread=False)

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (u TEXT PRIMARY KEY, p TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS docs (name TEXT, spec TEXT, lat REAL, lon REAL)")
    c.execute("CREATE TABLE IF NOT EXISTS appts (u TEXT, d TEXT, dt TEXT, tm TEXT)")
    
    # تأكد من وجود أطباء
    c.execute("SELECT COUNT(*) FROM docs")
    if c.fetchone()[0] == 0:
        c.executemany("INSERT INTO docs VALUES (?,?,?,?)", [
            ("د. هاشم العبيدي", "قلب وباطنية", 33.3128, 44.3615),
            ("د. ميساء الخزرجي", "جلدية", 33.3020, 44.4210),
            ("د. زيد الحكيم", "طوارئ وعام", 33.2750, 44.3750)
        ])
    conn.commit()
    conn.close()

init_db()

# --- 3. إدارة الجلسة والتنقل ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "page" not in st.session_state: st.session_state.page = "login"

# --- 4. واجهات تسجيل الدخول والإنشاء (Centered Design) ---
if not st.session_state.logged_in:
    _, col_center, _ = st.columns([1, 2, 1])
    
    with col_center:
        st.markdown('<div class="portal-box">', unsafe_allow_html=True)
        
        if st.session_state.page == "login":
            st.markdown("<h2>تسجيل الدخول</h2>", unsafe_allow_html=True)
            u_name = st.text_input("اسم المستخدم", key="log_u")
            u_pass = st.text_input("كلمة المرور", type="password", key="log_p")
            
            if st.button("دخول"):
                conn = get_db()
                res = conn.execute("SELECT * FROM users WHERE u=? AND p=?", (u_name, u_pass)).fetchone()
                conn.close()
                if res:
                    st.session_state.logged_in = True
                    st.session_state.user = u_name
                    st.rerun()
                else:
                    st.error("بيانات الدخول غير صحيحة")
            
            st.write("---")
            if st.button("لا تملك حساب؟ إنشاء حساب جديد"):
                st.session_state.page = "signup"
                st.rerun()

        elif st.session_state.page == "signup":
            st.markdown("<h2>إنشاء حساب جديد</h2>", unsafe_allow_html=True)
            new_u = st.text_input("اختر اسم مستخدم جديد", key="sig_u")
            new_p = st.text_input("اختر كلمة مرور قوية", type="password", key="sig_p")
            
            if st.button("تأكيد التسجيل"):
                if new_u and new_p:
                    try:
                        conn = get_db()
                        conn.execute("INSERT INTO users (u, p) VALUES (?,?)", (new_u, new_p))
                        conn.commit()
                        conn.close()
                        st.success(f"تم تسجيل {new_u} بنجاح! يمكنك الدخول الآن.")
                        st.session_state.page = "login"
                        # لا نضع rerun هنا ليرى المستخدم رسالة النجاح
                    except sqlite3.IntegrityError:
                        st.error("هذا الاسم مأخوذ فعلياً، جرب إضافة أرقام أو اسم آخر.")
                else:
                    st.warning("يرجى ملء كافة الحقول")
            
            if st.button("العودة لشاشة الدخول"):
                st.session_state.page = "login"
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

# --- 5. واجهة الخدمات (بعد الدخول) ---
else:
    with st.sidebar:
        st.markdown(f"### مرحباً د. {st.session_state.user}")
        menu = st.radio("انتقل إلى:", ["التشخيص والحجز", "مواعيدي المحفوظة", "تسجيل الخروج"])
    
    if menu == "التشخيص والحجز":
        st.markdown('<div class="portal-box" style="max-width:800px;">', unsafe_allow_html=True)
        st.markdown("<h2>بوابة التشخيص الذكي</h2>", unsafe_allow_html=True)
        
        syms = st.multiselect("اختر الأعراض التي تشعر بها:", ["ألم في الصدر", "ضيق تنفس", "صداع شديد", "طفح جلدي"])
        
        if st.button("تحليل الموقف وإيجاد أقرب عيادة"):
            loc = get_geolocation()
            if loc:
                u_lat, u_lon = loc['coords']['latitude'], loc['coords']['longitude']
                conn = get_db()
                docs = conn.execute("SELECT * FROM docs").fetchall()
                conn.close()
                
                st.markdown("### الأطباء المتاحون بالقرب منك:")
                for d in docs:
                    dist = math.sqrt((u_lat-d[2])*2 + (u_lon-d[3])*2)*111
                    st.markdown(f"""
                    <div class="info-card">
                        <b>{d[0]}</b> - تخصص {d[1]}<br>
                        المسافة التقريبية: {dist:.1f} كم
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # الحجز
                    d_date = st.date_input("اختر تاريخ الموعد", min_value=date.today(), key=f"date_{d[0]}")
                    if st.button(f"تثبيت موعد عند {d[0]}", key=f"btn_{d[0]}"):
                        conn = get_db()
                        conn.execute("INSERT INTO appts VALUES (?,?,?,?)", (st.session_state.user, d[0], str(d_date), "10:00 AM"))
                        conn.commit(); conn.close()
                        st.success("تم تثبيت موعدك بنجاح!")
            else:
                st.warning("يرجى تفعيل خدمة الموقع GPS لإظهار الأطباء الأقرب لك.")
        st.markdown('</div>', unsafe_allow_html=True)

    elif menu == "تسجيل الخروج":
        st.session_state.logged_in = False
        st.session_state.page = "login"
        st.rerun()
