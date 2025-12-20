import streamlit as st
import sqlite3
import hashlib
import math
from streamlit_js_eval import get_geolocation

# --- 1. إعدادات الصفحة والتصميم ---
st.set_page_config(page_title="AI Doctor Baghdad", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    * { font-family: 'Tajawal', sans-serif; direction: rtl; }
    .stApp { background: #0b1218; color: #e0f2f1; }
    .main-header { text-align: center; color: #00d2ff; font-size: 32px; font-weight: 700; padding: 20px; }
    .portal-box { max-width: 800px; margin: auto; padding: 25px; background: rgba(255, 255, 255, 0.05); border-radius: 15px; border: 1px solid #00d2ff33; }
    .doc-card { background: rgba(0, 210, 255, 0.08); padding: 15px; border-radius: 12px; border-right: 6px solid #00d2ff; margin-bottom: 12px; }
    .emergency-card { border-right: 6px solid #ff4b4b; background: rgba(255, 75, 75, 0.12); border: 1px solid #ff4b4b44; }
    .stButton>button { width: 100%; border-radius: 10px; background: linear-gradient(135deg, #00d2ff 0%, #3a7bd5 100%); color: white; border: none; height: 3.2em; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إدارة قاعدة البيانات (حل مشكلة الاسم المأخوذ) ---
def init_db():
    conn = sqlite3.connect("medical_baghdad.db")
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
    conn.commit()
    conn.close()

def register_user(user, pwd):
    conn = sqlite3.connect("medical_baghdad.db")
    c = conn.cursor()
    try:
        if not user or not pwd: return "empty"
        hashed_pwd = hashlib.sha256(pwd.encode()).hexdigest()
        c.execute('INSERT INTO users VALUES (?,?)', (user, hashed_pwd))
        conn.commit()
        return "success"
    except sqlite3.IntegrityError:
        return "taken" # الاسم مأخوذ
    finally:
        conn.close()

def login_user(user, pwd):
    conn = sqlite3.connect("medical_baghdad.db")
    c = conn.cursor()
    hashed_pwd = hashlib.sha256(pwd.encode()).hexdigest()
    c.execute('SELECT * FROM users WHERE username=? AND password=?', (user, hashed_pwd))
    data = c.fetchone()
    conn.close()
    return data

init_db()

# --- 3. التشخيصات الموسعة وأطباء بغداد ---
SYMPTOMS_DB = {
    "ألم ضاغط في الصدر يمتد للذراع": {"diag": "اشتباه بنوبة قلبية حادة", "spec": "أمراض القلب", "emergency": True},
    "ضيق تنفس شديد مفاجئ": {"diag": "اشتباه بفشل تنفسي أو أزمة ربو", "spec": "أمراض صدرية", "emergency": True},
    "فقدان توازن مع ثقل في الكلام": {"diag": "اشتباه بجلطة دماغية", "spec": "جملة عصبية", "emergency": True},
    "ألم شديد في الجانب السفلي للأذن": {"diag": "التهاب الأذن الوسطى", "spec": "أنف وأذن وحنجرة", "emergency": False},
    "ألم أسفل الظهر مع تنمل الساق": {"diag": "انزلاق غضروفي (دسك)", "spec": "مفاصل وعظام", "emergency": False},
    "عطش شديد وتبول متكرر": {"diag": "اضطراب في مستويات السكر", "spec": "غدد صماء", "emergency": False},
    "احمرار العين مع تشوش الرؤية": {"diag": "التهاب قرنية أو ارتفاع ضغط العين", "spec": "عيون", "emergency": False}
}

DOCTORS_BAGHDAD = [
    {"name": "د. علي الركابي", "spec": "أمراض القلب", "area": "المنصور", "lat": 33.325, "lon": 44.348},
    {"name": "د. مريم القيسي", "spec": "أمراض القلب", "area": "الكرادة", "lat": 33.300, "lon": 44.420},
    {"name": "مستشفى الجملة العصبية", "spec": "جملة عصبية", "area": "الرصافة", "lat": 33.340, "lon": 44.400},
    {"name": "د. عمر الجبوري", "spec": "عيون", "area": "الأعظمية", "lat": 33.365, "lon": 44.380},
    {"name": "د. سارة لؤي", "spec": "جلدية", "area": "زيونة", "lat": 33.330, "lon": 44.450},
    {"name": "د. نور الدين", "spec": "مفاصل وعظام", "area": "الحارثية", "lat": 33.320, "lon": 44.360},
    {"name": "مركز طوارئ مدينة الطب", "spec": "طوارئ", "area": "باب المعظم", "lat": 33.350, "lon": 44.385},
]

# حل مشكلة الحساب: التأكد من وجود أرقام قبل الحساب
def calculate_distance(u_lat, u_lon, d_lat, d_lon):
    try:
        return math.sqrt((float(u_lat) - float(d_lat))*2 + (float(u_lon) - float(d_lon))*2) * 111
    except:
        return 999 # قيمة افتراضية في حال الخطأ

# --- 4. واجهة المستخدم المنطقية ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown('<h1 class="main-header">طبيبي الذكي - بغداد</h1>', unsafe_allow_html=True)
    auth_tab1, auth_tab2 = st.tabs(["تسجيل دخول", "إنشاء حساب جديد"])
    
    with auth_tab1:
        u = st.text_input("اسم المستخدم", key="login_u")
        p = st.text_input("كلمة المرور", type="password", key="login_p")
        if st.button("دخول"):
            if login_user(u, p):
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("عذراً، تأكد من اسم المستخدم أو كلمة المرور")
            
    with auth_tab2:
        new_u = st.text_input("اختر اسم مستخدم جديد", key="reg_u")
        new_p = st.text_input("اختر كلمة مرور", type="password", key="reg_p")
        if st.button("تسجيل الحساب"):
            status = register_user(new_u, new_p)
            if status == "success":
                st.success("تم التسجيل بنجاح! انتقل لتبويب تسجيل الدخول.")
            elif status == "taken":
                st.error("⚠️ هذا الاسم مأخوذ بالفعل، جرب اسماً آخر (مثلاً أضف رقماً).")
            else:
                st.warning("يرجى ملء جميع الحقول")

else:
    # --- واجهة الفحص والـ GPS ---
    st.markdown('<h1 class="main-header">مركز الفحص والتشخيص الفوري 🏥</h1>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.info("مرحباً بك في نظام طبيب بغداد الذكي")
        if st.button("تسجيل خروج"):
            st.session_state.logged_in = False
            st.rerun()

    st.markdown('<div class="portal-box">', unsafe_allow_html=True)
    st.subheader("اختر الأعراض التي تعاني منها:")
    selected_symptoms = st.multiselect("يمكنك اختيار أكثر من عرض:", list(SYMPTOMS_DB.keys()))
    
    # الحصول على الموقع (GPS)
    location = get_geolocation()
    
    if st.button("تحليل الحالة وعرض الأطباء 🔎"):
        if not selected_symptoms:
            st.warning("⚠️ يرجى اختيار عرض واحد على الأقل للتشخيص.")
        elif not location:
            st.error("📍 يرجى تفعيل الـ GPS في المتصفح للسماح لنا بتحديد أقرب طبيب في بغداد.")
        else:
            # استخراج الإحداثيات بأمان لمنع الـ ValueError
            try:
                u_lat = location['coords']['latitude']
                u_lon = location['coords']['longitude']
                
                is_emergency = any(SYMPTOMS_DB[s]["emergency"] for s in selected_symptoms)
                specs = list(set(SYMPTOMS_DB[s]["spec"] for s in selected_symptoms))
                diags = list(set(SYMPTOMS_DB[s]["diag"] for s in selected_symptoms))
                
                st.info(f"*التشخيص المتوقع:* {', '.join(diags)}")
                
                if is_emergency:
                    st.error("🚨 *حالة طارئة جداً!* تم ترتيب الأطباء حسب الأولوية القصوى (القلب والطوارئ) بغض النظر عن المسافة.")

                # تصفية وترتيب الأطباء
                results = []
                for d in DOCTORS_BAGHDAD:
                    dist = calculate_distance(u_lat, u_lon, d["lat"], d["lon"])
                    
                    # منطق الأولوية: إذا كانت طوارئ، نعطي الأولوية لتخصص الطوارئ والقلب
                    priority = 0
                    if is_emergency and (d["spec"] == "أمراض القلب" or d["spec"] == "طوارئ"):
                        priority = 1
                    
                    # إظهار الطبيب إذا كان تخصصه مطلوباً أو إذا كانت هناك حالة طوارئ
                    if d["spec"] in specs or priority == 1:
                        d_info = d.copy()
                        d_info["dist"] = dist
                        d_info["priority"] = priority
                        results.append(d_info)
                
                # الترتيب: الأولوية أولاً (للطوارئ) ثم المسافة الأقرب
                results.sort(key=lambda x: (-x["priority"], x["dist"]))
                
                st.write("### النتائج (الأطباء والمستشفيات المتاحة):")
                for doc in results:
                    is_em_card = "emergency-card" if doc["priority"] == 1 else ""
                    st.markdown(f"""
                    <div class="doc-card {is_em_card}">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 1.2em;"><b>{doc['name']}</b></span>
                            <span style="background: #00d2ff; color: black; padding: 2px 8px; border-radius: 5px; font-size: 0.8em;">{doc['area']}</span>
                        </div>
                        <div style="margin-top: 10px;">
                            <span>التخصص: {doc['spec']}</span> | 
                            <span>📍 يبعد عنك: <b>{doc['dist']:.2f} كم</b></span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            except Exception as e:
                st.error("حدث خطأ في قراءة بيانات الموقع. يرجى تحديث الصفحة والمحاولة مرة أخرى.")

    st.markdown('</div>', unsafe_allow_html=True)
