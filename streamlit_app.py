import streamlit as st
import sqlite3
import os
import hashlib
from datetime import datetime

# ---------------------
# إعداد الصفحة والـ CSS
# ---------------------
st.set_page_config(page_title="طبيب افتراضي AI", layout="centered", icon="⚕️")

# بسيطة لتجميل الصفحة
st.markdown(
    """
    <style>
    .main {background-color: #f7fbfc;}
    .card {
        border-radius: 12px;
        padding: 18px;
        background: linear-gradient(180deg, #ffffff 0%, #f4fbff 100%);
        box-shadow: 0 6px 18px rgba(0,0,0,0.06);
        margin-bottom: 16px;
    }
    .small-muted { color: #6b7280; font-size: 0.9rem; }
    .brand { color: #037f8c; font-weight: 700; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------
# إعداد قاعدة البيانات
# ---------------------
DB_PATH = "virtual_doctor_streamlit.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    # users
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
    ''')
    # doctors
    cur.execute('''
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialty TEXT NOT NULL,
            is_available INTEGER NOT NULL DEFAULT 1
        );
    ''')
    # appointments
    cur.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            doctor_id INTEGER NOT NULL,
            appointment_date TEXT NOT NULL,
            appointment_time TEXT NOT NULL,
            diagnosis TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (doctor_id) REFERENCES doctors(id)
        );
    ''')
    # إضافة أطباء افتراضيين إن لم يكونوا
    cur.execute("SELECT COUNT(*) as c FROM doctors")
    if cur.fetchone()["c"] == 0:
        doctors = [
            ("د. أحمد علي", "عام", 1),
            ("د. فاطمة يوسف", "باطنية", 1),
            ("د. مريم خالد", "جلدية", 1),
            ("د. حسن سالم", "أطفال", 1),
            ("د. علي محمود", "قلب", 1),
        ]
        cur.executemany("INSERT INTO doctors (name, specialty, is_available) VALUES (?, ?, ?)", doctors)
    conn.commit()
    conn.close()

init_db()

# ---------------------
# بيانات الأعراض والأمراض
# ---------------------
SYMPTOMS = [
    "حمى", "سعال", "بلغم", "ضيق نفس", "صداع", "ألم في الصدر",
    "آلام في الجسم", "تعب شديد", "احتقان الأنف", "سيلان الأنف",
    "التهاب الحلق", "فقدان الشم", "فقدان التذوق", "غثيان",
    "قيء", "إسهال", "ألم بطن", "طفح جلدي", "حكة", "تورّم",
    "دوخة", "خفقان قلب", "تشنج", "نزيف بسيط", "آلام المفاصل"
]  # 25 عرض

DISEASES = [
    "الإنفلونزا الموسمية",
    "نزلات البرد",
    "التهاب رئوي",
    "حساسية مَرَضية",
    "التسمم الغذائي",
    "التهاب حلقي حاد",
    "COVID-19",
    "صداع نصفي",
    "التهاب جلدي تماسي",
    "التهاب المعدة والأمعاء"
]  # 10 أمراض

# تعريف بروفايل لكل مرض: قائمة مؤشرات الأعراض المهمة (أوزان بسيطة)
# المفتاح: اسم المرض -> dict: symptom -> weight
DISEASE_PROFILES = {
    "الإنفلونزا الموسمية": {"حمى":2, "سعال":1, "آلام في الجسم":1.5, "تعب شديد":2, "صداع":1},
    "نزلات البرد": {"سعال":1, "احتقان الأنف":1.5, "سيلان الأنف":1.5, "التهاب الحلق":1},
    "التهاب رئوي": {"حمى":2, "سعال":2, "بلغم":2, "ضيق نفس":2, "ألم في الصدر":1.5},
    "حساسية مَرَضية": {"عطاس":0, "احتقان الأنف":1.5, "سيلان الأنف":1.5, "حكة":1.8, "حكة في العين":0},
    "التسمم الغذائي": {"غثيان":2, "قيء":2, "إسهال":2, "ألم بطن":1.5},
    "التهاب حلقي حاد": {"التهاب الحلق":2, "حمى":1, "صداع":0.8},
    "COVID-19": {"حمى":1.8, "سعال":1.5, "فقدان الشم":2, "فقدان التذوق":2, "ضيق نفس":1.5},
    "صداع نصفي": {"صداع":2, "غثيان":1.2, "تعب شديد":0.8, "دوخة":0.8},
    "التهاب جلدي تماسي": {"طفح جلدي":2, "حكة":1.8, "تورّم":0.8},
    "التهاب المعدة والأمعاء": {"غثيان":1.5, "قيء":1.5, "إسهال":2, "ألم بطن":1.2}
}

# ---------------------
# دوال مساعدة
# ---------------------
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def get_user_by_username(username):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    return row

def create_user(username, email, password):
    conn = get_connection()
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()
    try:
        cur.execute(
            "INSERT INTO users (username, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
            (username, email, hash_password(password), now)
        )
        conn.commit()
        return True, None
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def verify_user(username, password):
    user = get_user_by_username(username)
    if not user:
        return False, None
    return hash_password(password) == user["password_hash"], user

def softmax(x):
    import math
    exps = [math.exp(v) for v in x]
    s = sum(exps) or 1.0
    return [e / s for e in exps]

def diagnose_with_profiles(selected_symptoms):
    # انشأ قائمة درجات لكل مرض
    scores = []
    for disease in DISEASES:
        profile = DISEASE_PROFILES.get(disease, {})
        score = 0.0
        # مجموع الأوزان للأعراض المختارة
        for s in selected_symptoms:
            weight = profile.get(s, 0.0)
            score += weight
        # قاعدة بسيطة: أضف عامل اعتماد على عدد الأعراض العامة
        scores.append(score)
    probs = softmax(scores)
    top_idx = max(range(len(probs)), key=lambda i: probs[i])
    disease_name = DISEASES[top_idx]
    confidence = probs[top_idx] * 100
    return disease_name, confidence, probs

# ---------------------
# واجهات المستخدم (Pages) الرئيسية
# ---------------------
def show_header():
    col1, col2 = st.columns([1,4])
    with col1:
        st.image("https://img.icons8.com/?size=512&id=12584&format=png", width=72)
    with col2:
        st.markdown("<div class='brand'>طبيب افتراضي AI</div>", unsafe_allow_html=True)
        st.markdown("<div class='small-muted'>تشخيص أولي ذكي، تسجيل، وحجز مواعيد</div>", unsafe_allow_html=True)
    st.markdown("---")

def register_page():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("إنشاء حساب جديد")
    with st.form("register_form"):
        username = st.text_input("اسم المستخدم")
        email = st.text_input("البريد الإلكتروني")
        password = st.text_input("كلمة المرور", type="password")
        password2 = st.text_input("تأكيد كلمة المرور", type="password")
        submitted = st.form_submit_button("سجل الآن")
    if submitted:
        if not username or not email or not password:
            st.error("يرجى ملء كل الحقول.")
        elif password != password2:
            st.error("كلمتا المرور غير متطابقتين.")
        else:
            ok, err = create_user(username, email, password)
            if ok:
                st.success("تم إنشاء الحساب! يمكنك الآن تسجيل الدخول.")
            else:
                st.error(f"فشل التسجيل: {err}")
    st.markdown("</div>", unsafe_allow_html=True)

def login_page():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("تسجيل الدخول")
    with st.form("login_form"):
        username = st.text_input("اسم المستخدم")
        password = st.text_input("كلمة المرور", type="password")
        submitted = st.form_submit_button("دخول")
    if submitted:
        ok, user = verify_user(username, password)
        if ok:
            # حفظ جلسة مبسطة
            st.session_state["logged_in"] = True
            st.session_state["username"] = user["username"]
            st.success("تم تسجيل الدخول بنجاح.")
            st.experimental_rerun()
        else:
            st.error("اسم المستخدم أو كلمة المرور غير صحيحة.")
    st.markdown("</div>", unsafe_allow_html=True)

def logout():
    st.session_state.pop("logged_in", None)
    st.session_state.pop("username", None)
    st.success("تم تسجيل الخروج.")

# صفحة التشخيص
def consultation_page():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("استشارة طبية — اختر الأعراض")
    st.markdown("اختر الأعراض التي تشعرين بها (يمكن اختيار أكثر من واحد).")
    with st.form("consult_form"):
        # عرض الأعراض في أعمدة
        cols = st.columns(3)
        selected = []
        for i, s in enumerate(SYMPTOMS):
            c = cols[i % 3]
            if c.checkbox(s, key=f"sym_{i}"):
                selected.append(s)
        submitted = st.form_submit_button("تشخيص الآن 🔍")
    if submitted:
        if len(selected) == 0:
            st.warning("يرجى اختيار عرض واحد على الأقل.")
        else:
            disease, confidence, probs = diagnose_with_profiles(selected)
            st.markdown("---")
            st.markdown(f"### نتيجة التشخيص: *{disease}*")
            st.markdown(f"*نسبة الثقة:* {confidence:.1f}%")
            st.markdown("#### التفاصيل (احتمالات للأمراض):")
            for i, d in enumerate(DISEASES):
                st.write(f"- {d}: {probs[i]*100:.1f}%")
            # زر لحجز موعد مع تمرير التشخيص
            if st.button("حجز موعد مع تشخيص محفوظ"):
                st.session_state["last_diagnosis"] = disease
                st.experimental_rerun()
    st.markdown("</div>", unsafe_allow_html=True)

def booking_page():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("حجز مواعيد")
    conn = get_connection()
    cur = conn.cursor()
    # احصل على بيانات المستخدم
    username = st.session_state.get("username")
    cur.execute("SELECT id FROM users WHERE username = ?", (username,))
    user = cur.fetchone()
    if not user:
        st.error("المستخدم غير موجود. الرجاء تسجيل الدخول.")
        conn.close()
        return
    user_id = user["id"]
    # جلب الأطباء المتاحين
    cur.execute("SELECT id, name, specialty FROM doctors WHERE is_available = 1")
    doctors = cur.fetchall()
    if not doctors:
        st.info("لا يوجد أطباء متاحين حالياً.")
        conn.close()
        st.markdown("</div>", unsafe_allow_html=True)
        return
    # نموذج الحجز
    with st.form("booking_form"):
        doc_options = {f"{d['name']} — {d['specialty']}": d["id"] for d in doctors}
        choice = st.selectbox("اختر الطبيب", options=list(doc_options.keys()))
        date = st.date_input("تاريخ الموعد")
        time = st.time_input("وقت الموعد")
        reason = st.text_input("ملاحظات / تشخيص (اختياري)", value=st.session_state.get("last_diagnosis", ""))
        submitted = st.form_submit_button("احجز الآن")
    if submitted:
        doctor_id = doc_options[choice]
        now = datetime.utcnow().isoformat()
        cur.execute(
            "INSERT INTO appointments (user_id, doctor_id, appointment_date, appointment_time, diagnosis, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, date.isoformat(), time.isoformat(timespec="minutes"), reason, now)
        )
        conn.commit()
        st.success(f"تم حجز الموعد مع {choice} في {date} الساعة {time.strftime('%H:%M')}.")
    # عرض مواعيد المستخدم
    st.markdown("---")
    st.markdown("### مواعيدي القادمة:")
    cur.execute("""
        SELECT a.id, d.name, d.specialty, a.appointment_date, a.appointment_time, a.diagnosis
        FROM appointments a JOIN doctors d ON a.doctor_id = d.id
        WHERE a.user_id = ?
        ORDER BY a.appointment_date, a.appointment_time
    """, (user_id,))
    rows = cur.fetchall()
    if not rows:
        st.info("لا توجد مواعيد محفوظة.")
    else:
        for r in rows:
            st.markdown(f"- *{r['name']} — {r['specialty']}* | {r['appointment_date']} — {r['appointment_time']}  \n  التشخيص: {r['diagnosis'] or '—'}")
    conn.close()
    st.markdown("</div>", unsafe_allow_html=True)

def profile_page():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("الملف الشخصي")
    username = st.session_state.get("username")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT username, email, created_at FROM users WHERE username = ?", (username,))
    user = cur.fetchone()
    if user:
        st.write(f"- اسم المستخدم: *{user['username']}*")
        st.write(f"- البريد الإلكتروني: *{user['email']}*")
        st.write(f"- منذ: *{user['created_at'][:10]}*")
    else:
        st.error("خطأ في جلب بيانات المستخدم.")
    conn.close()
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------
# تطبيق التنقّل الرئيسي
# ---------------------
def main():
    show_header()

    # شريط جانبي للحساب و التنقّل
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    with st.sidebar:
        st.markdown("## القائمة")
        if st.session_state["logged_in"]:
            st.markdown(f"*مرحباً، {st.session_state['username']}*")
            nav = st.radio("", ["الاستشارة", "حجز موعد", "الملف الشخصي", "تسجيل خروج"], index=0)
        else:
            nav = st.radio("", ["تسجيل دخول", "إنشاء حساب"], index=0)

    # صفحات
    if not st.session_state["logged_in"]:
        if nav == "تسجيل دخول":
            login_page()
        elif nav == "إنشاء حساب":
            register_page()
    else:
        if nav == "الاستشارة":
            consultation_page()
        elif nav == "حجز موعد":
            booking_page()
        elif nav == "الملف الشخصي":
            profile_page()
        elif nav == "تسجيل خروج":
            logout()

    # تلميحات سفلية
    st.markdown("---")
    st.markdown("<div class='small-muted'>ملاحظة: هذا تطبيق تشخيص مبدئي ولا يغني عن استشارة الطبيب المختص. © 2025</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()