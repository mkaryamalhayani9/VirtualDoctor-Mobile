import streamlit as st
import sqlite3
import os

# --- 1. التنسيق البصري (Elite Emerald UI) ---
st.set_page_config(page_title="AI Doctor Premium", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    * { font-family: 'Tajawal', sans-serif; direction: rtl; }
    .stApp { background: #050a0b; color: #e0f2f1; }
    
    /* العنوان الرئيسي في المنتصف */
    .main-header {
        text-align: center;
        color: #71B280;
        font-size: 45px;
        font-weight: 700;
        margin-bottom: 10px;
        letter-spacing: 1px;
    }

    /* حاوية النموذج المتوسطة */
    .form-container {
        max-width: 450px;
        margin: auto;
        padding: 25px;
        background: rgba(255, 255, 255, 0.03);
        border-radius: 15px;
        border: 1px solid rgba(113, 178, 128, 0.1);
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }

    /* تصغير حقول الإدخال */
    .stTextInput>div>div>input {
        background: #0d1b1e !important;
        color: white !important;
        border-radius: 8px !important;
        height: 40px !important;
    }

    /* الأزرار المتجاورة */
    .stButton>button {
        width: 100% !important;
        border-radius: 8px !important;
        background: linear-gradient(135deg, #134E5E 0%, #71B280 100%) !important;
        color: white !important;
        font-weight: bold !important;
        height: 45px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إدارة قاعدة البيانات (حل جذري لمشكلة الاسم مأخوذ) ---
# قمت بتغيير اسم الملف لضمان إنشاء قاعدة بيانات جديدة تماماً لا تحتوي على الأسماء القديمة
DB_FILE = "doctor_v2_system.db"

def init_db():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (u TEXT PRIMARY KEY, p TEXT)")
    conn.commit()
    conn.close()

init_db()

# --- 3. إدارة التنقل ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "page" not in st.session_state: st.session_state.page = "login"

# --- 4. الواجهة الرسومية ---

# العنوان دائماً في المنتصف في الأعلى
st.markdown('<h1 class="main-header">AI Doctor</h1>', unsafe_allow_html=True)

if not st.session_state.logged_in:
    # جعل النموذج في منتصف الشاشة أفقياً
    _, col_mid, _ = st.columns([1, 1.4, 1])
    
    with col_mid:
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        
        if st.session_state.page == "login":
            st.markdown("<h3 style='text-align:center;'>تسجيل الدخول</h3>", unsafe_allow_html=True)
            u = st.text_input("اسم المستخدم", placeholder="ادخل الاسم")
            p = st.text_input("كلمة المرور", type="password", placeholder="ادخل الرمز")
            
            # أزرار الدخول وإنشاء حساب جنب بعض
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("دخول"):
                    conn = sqlite3.connect(DB_FILE)
                    res = conn.execute("SELECT * FROM users WHERE u=? AND p=?", (u, p)).fetchone()
                    conn.close()
                    if res:
                        st.session_state.logged_in = True
                        st.session_state.user = u
                        st.rerun()
                    else: st.error("بيانات غير صحيحة")
            with btn_col2:
                if st.button("إنشاء حساب جديد"):
                    st.session_state.page = "signup"
                    st.rerun()

        elif st.session_state.page == "signup":
            st.markdown("<h3 style='text-align:center;'>إنشاء حساب جديد</h3>", unsafe_allow_html=True)
            nu = st.text_input("اسم المستخدم الجديد", key="reg_u")
            np = st.text_input("كلمة المرور الجديدة", type="password", key="reg_p")
            
            # أزرار التأكيد والرجوع جنب بعض
            reg_col1, reg_col2 = st.columns(2)
            with reg_col1:
                if st.button("تأكيد"):
                    if nu and np:
                        try:
                            conn = sqlite3.connect(DB_FILE)
                            conn.execute("INSERT INTO users VALUES (?,?)", (nu, np))
                            conn.commit(); conn.close()
                            st.success("تم التسجيل! يمكنك الدخول الآن")
                            st.session_state.page = "login"
                            # ننتظر ثانية ليرى المستخدم النجاح قبل الريرن اليدوي أو التلقائي
                        except sqlite3.IntegrityError:
                            st.error("عذراً، هذا الاسم مأخوذ بالفعل")
                    else: st.warning("املأ الحقول")
            with reg_col2:
                if st.button("رجوع"):
                    st.session_state.page = "login"
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

# --- 5. بعد تسجيل الدخول ---
else:
    st.sidebar.markdown(f"## مرحباً {st.session_state.user}")
    if st.sidebar.button("تسجيل خروج"):
        st.session_state.logged_in = False
        st.rerun()
    
    st.info("لقد تم الدخول بنجاح إلى نظام AI Doctor")
