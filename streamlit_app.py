import streamlit as st
import sqlite3
from datetime import date

# --- 1. التصميم (Compact Emerald UI) ---
st.set_page_config(page_title="Emerald Portal", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    * { font-family: 'Tajawal', sans-serif; direction: rtl; }
    .stApp { background: #050a0b; color: #e0f2f1; }
    
    /* تصغير حجم حاوية الكتابة */
    .stTextInput>div>div>input {
        text-align: right; 
        background: #0d1b1e !important; 
        color: white !important;
        height: 35px; /* تصغير الارتفاع */
        font-size: 14px;
    }
    
    /* حاوية المحتوى المتوسطة */
    .login-card {
        max-width: 450px; /* حجم أصغر ومرتب */
        margin: 60px auto;
        padding: 30px;
        background: rgba(255, 255, 255, 0.03);
        border-radius: 15px;
        border: 1px solid rgba(113, 178, 128, 0.2);
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }

    /* تنسيق الأزرار لتكون بجانب بعضها */
    .stButton>button {
        background: linear-gradient(135deg, #134E5E 0%, #71B280 100%);
        color: white; border-radius: 8px; border: none; font-weight: bold;
        transition: 0.3s;
    }
    
    h2 { color: #71B280; text-align: center; font-size: 22px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. تهيئة قاعدة البيانات ---
def init_db():
    conn = sqlite3.connect("virtual_doctor.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (u TEXT PRIMARY KEY, p TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS appts (u TEXT, d TEXT, dt TEXT, tm TEXT)")
    conn.commit()
    conn.close()

init_db()

# --- 3. إدارة التنقل ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "page" not in st.session_state: st.session_state.page = "login"

# --- 4. واجهة الدخول / الإنشاء ---
if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1.5, 1])
    
    with col_mid:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        
        if st.session_state.page == "login":
            st.markdown("<h2>تسجيل الدخول</h2>", unsafe_allow_html=True)
            u = st.text_input("اسم المستخدم", placeholder="ادخل اسمك")
            p = st.text_input("كلمة المرور", type="password", placeholder="ادخل الرمز")
            
            # وضع الأزرار بجانب بعضها باستخدام col1, col2
            c1, c2 = st.columns(2)
            with c1:
                if st.button("دخول"):
                    conn = sqlite3.connect("virtual_doctor.db")
                    res = conn.execute("SELECT * FROM users WHERE u=? AND p=?", (u, p)).fetchone()
                    conn.close()
                    if res:
                        st.session_state.logged_in = True
                        st.session_state.user = u
                        st.rerun()
                    else: st.error("خطأ بالبيانات")
            with c2:
                if st.button("إنشاء حساب"):
                    st.session_state.page = "signup"
                    st.rerun()

        elif st.session_state.page == "signup":
            st.markdown("<h2>حساب جديد</h2>", unsafe_allow_html=True)
            nu = st.text_input("اسم المستخدم الجديد")
            np = st.text_input("كلمة المرور الجديدة")
            
            sc1, sc2 = st.columns(2)
            with sc1:
                if st.button("تأكيد"):
                    if nu and np:
                        try:
                            conn = sqlite3.connect("virtual_doctor.db")
                            conn.execute("INSERT INTO users VALUES (?,?)", (nu, np))
                            conn.commit(); conn.close()
                            st.success("تم!")
                            st.session_state.page = "login"
                            st.rerun()
                        except: st.error("الاسم مأخوذ")
            with sc2:
                if st.button("رجوع"):
                    st.session_state.page = "login"
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

# --- 5. الصفحة الرئيسية بعد الدخول ---
else:
    with st.sidebar:
        st.write(f"أهلاً {st.session_state.user}")
        if st.button("خروج"):
            st.session_state.logged_in = False
            st.rerun()
    
    st.markdown('<div class="login-card" style="max-width:800px;">', unsafe_allow_html=True)
    st.markdown("<h2>بوابة الخدمات</h2>", unsafe_allow_html=True)
    st.write("أنت الآن داخل النظام بنجاح.")
    st.markdown('</div>', unsafe_allow_html=True)
