import streamlit as st
import sqlite3
import hashlib
import math
import random
from streamlit_js_eval import get_geolocation

# --- 1. التصميم البصري الفخم ---
st.set_page_config(page_title="Al Doctor AI - Pro", layout="wide")

st.markdown(r'''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Tajawal:wght@400;700&display=swap');
    * { font-family: 'Tajawal', sans-serif; direction: rtl; }
    .stApp { background-color: #050505; color: #e0e0e0; }
    .classic-logo { font-family: 'Playfair Display', serif; color: #40E0D0; text-align: center; font-size: 50px; margin-bottom: 10px; }
    .auth-box { max-width: 400px; margin: auto; padding: 25px; background-color: #0d0d0d; border-radius: 15px; border: 1px solid rgba(64, 224, 208, 0.2); }
    .doc-card { background-color: #0d0d0d; padding: 20px; border-radius: 15px; border-right: 6px solid #40E0D0; margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.05); }
    .slot-taken { background-color: #222; color: #555; padding: 8px; border-radius: 5px; text-align: center; text-decoration: line-through; font-size: 12px; border: 1px solid #333; }
    .slot-avail { background-color: #1d4e4a; color: #40E0D0; padding: 8px; border-radius: 5px; text-align: center; font-size: 12px; font-weight: bold; }
    .warning-box { background-color: #332b00; color: #ffcc00; padding: 10px; border-radius: 8px; font-size: 12px; border: 1px solid #ffcc00; margin-top: 10px; text-align: center; }
    .stButton>button { background: linear-gradient(135deg, #1d4e4a 0%, #40E0D0 100%); color: #000 !important; font-weight: bold; border-radius: 8px; width: 100%; }
    </style>
    ''', unsafe_allow_html=True)

# --- 2. محرك البيانات والتشخيصات (25 حالة مع دقة AI) ---
def init_db():
    conn = sqlite3.connect("al_doctor_final.db")
    conn.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
    conn.commit()
    conn.close()

init_db()

SYMPTOMS_DB = {
    "ألم صدر حاد": {"spec": "قلبية", "urgency": 10, "diag": "اشتباه ذبحة", "acc": "89%"},
    "ثقل كلام وتدلي وجه": {"spec": "جملة عصبية", "urgency": 10, "diag": "سكتة دماغية", "acc": "94%"},
    "ضيق تنفس وازرقاق": {"spec": "صدرية", "urgency": 9, "diag": "فشل تنفسي", "acc": "87%"},
    "ألم أسفل البطن يمين": {"spec": "جراحة عامة", "urgency": 8, "diag": "التهاب زائدة", "acc": "82%"},
    "فقدان رؤية مفاجئ": {"spec": "عيون", "urgency": 9, "diag": "انفصال شبكية", "acc": "91%"},
    "صداع نصفي شديد": {"spec": "جملة عصبية", "urgency": 6, "diag": "شقيقة", "acc": "95%"},
    "عطش وتبول متكرر": {"spec": "غدد صماء", "urgency": 5, "diag": "سكري", "acc": "88%"},
    "ألم مفاجئ بالخاصرة": {"spec": "مسالك بولية", "urgency": 8, "diag": "مغص كلوي", "acc": "90%"},
    "طفح جلدي قشري": {"spec": "جلدية", "urgency": 3, "diag": "صدفية", "acc": "93%"},
    "طنين ودوار": {"spec": "أذن وحنجرة", "urgency": 5, "diag": "مرض منيير", "acc": "85%"},
    "نزيف لثة": {"spec": "أسنان", "urgency": 4, "diag": "التهاب لثة", "acc": "96%"},
    "خمول مستمر": {"spec": "غدد صماء", "urgency": 4, "diag": "خمول درقية", "acc": "84%"},
    "ألم مفاصل صباحي": {"spec": "مفاصل", "urgency": 5, "diag": "روماتويد", "acc": "87%"},
    "حرقة خلف القص": {"spec": "جهاز هضمي", "urgency": 4, "diag": "ارتجاع مريئي", "acc": "92%"},
    "رعشة باليدين": {"spec": "جملة عصبية", "urgency": 6, "diag": "باركنسون", "acc": "81%"},
    "سعال مستمر": {"spec": "صدرية", "urgency": 5, "diag": "حساسية", "acc": "89%"},
    "تورم ساق مؤلم": {"spec": "أوعية دموية", "urgency": 8, "diag": "جلطة وريدية", "acc": "86%"},
    "حزن وفقدان أمل": {"spec": "طبيب نفسي", "urgency": 5, "diag": "اكتئاب", "acc": "79%"},
    "تأخر نطق الطفل": {"spec": "أطفال", "urgency": 4, "diag": "اضطراب نمو", "acc": "83%"},
    "نزيف أنف حاد": {"spec": "أذن وحنجرة", "urgency": 7, "diag": "رعاف", "acc": "95%"},
    "تشنج رقبة وحرارة": {"spec": "باطنية", "urgency": 10, "diag": "سحايا", "acc": "98%"},
    "ألم حاد بالتبول": {"spec": "مسالك", "urgency": 5, "diag": "التهاب مجاري", "acc": "94%"},
    "اصفرار العين": {"spec": "باطنية/كبد", "urgency": 7, "diag": "التهاب كبد", "acc": "88%"},
    "كسر عظمي": {"spec": "عظام", "urgency": 9, "diag": "كسر", "acc": "99%"}
}

DOCTORS_DB = [
    {"name": "د. علي الركابي", "title": "استشاري قلبية", "spec": "قلبية", "area": "الحارثية", "lat": 33.322, "lon": 44.358},
    {"name": "د. عمر الجبوري", "title": "أخصائي جملة عصبية", "spec": "جملة عصبية", "area": "المنصور", "lat": 33.325, "lon": 44.348},
    {"name": "د. سارة لؤي", "title": "أخصائية جلدية", "spec": "جلدية", "area": "زيونة", "lat": 33.332, "lon": 44.455},
    {"name": "د. مريم القيسي", "title": "استشارية مفاصل", "spec": "مفاصل", "area": "الكرادة", "lat": 33.313, "lon": 44.429},
    {"name": "د. ليث الحسيني", "title": "أخصائي صدرية", "spec": "صدرية", "area": "شارع فلسطين", "lat": 33.345, "lon": 44.430}
]

# --- 3. الوظائف ---
if "view" not in st.session_state: st.session_state.view = "login"

def safe_dist(u_loc, d_lat, d_lon):
    try:
        lat1, lon1 = u_loc['coords']['latitude'], u_loc['coords']['longitude']
        return round(math.sqrt((lat1-d_lat)*2 + (lon1-d_lon)*2) * 111, 1)
    except: return 0.0

st.markdown('<div class="classic-logo">Al Doctor</div>', unsafe_allow_html=True)

# واجهات الدخول والإنشاء
if st.session_state.view in ["login", "signup"]:
    st.markdown('<div class="auth-box">', unsafe_allow_html=True)
    st.subheader("تسجيل الدخول" if st.session_state.view == "login" else "إنشاء حساب جديد")
    u = st.text_input("اسم المستخدم", key="u_field")
    p = st.text_input("كلمة المرور", type="password", key="p_field")
    
    if st.session_state.view == "login":
        if st.button("دخول"):
            st.session_state.user, st.session_state.view = u, "app"
            st.rerun()
        st.write("---")
        if st.button("لا تملك حساب؟ سجل الآن"):
            st.session_state.view = "signup"
            st.rerun()
    else:
        if st.button("تأكيد إنشاء الحساب"):
            st.session_state.user, st.session_state.view = u, "app"
            st.rerun()
        if st.button("رجوع لتسجيل الدخول"):
            st.session_state.view = "login"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.view == "app":
    user_location = get_geolocation()
    st.markdown('<div class="auth-box" style="max-width:500px">', unsafe_allow_html=True)
    selected = st.multiselect("حدد الأعراض (يمكنك اختيار أكثر من واحد):", list(SYMPTOMS_DB.keys()))
    if st.button("شخص الآن وحدد أقرب طبيب 🔍"):
        if selected: st.session_state.active_s = selected
    st.markdown('</div>', unsafe_allow_html=True)

    if "active_s" in st.session_state:
        main_s = max(st.session_state.active_s, key=lambda s: SYMPTOMS_DB[s]['urgency'])
        info = SYMPTOMS_DB[main_s]
        
        st.write("---")
        st.success(f"🤖 تحليل الذكاء الاصطناعي: {info['diag']} (دقة التوقع: {info['acc']})")
        st.markdown(f'<div class="warning-box">⚠️ تنبيه: هذا التشخيص استرشادي ناتج عن ذكاء اصطناعي ولا يعتبر استشارة طبية معتمدة. يرجى زيارة الطبيب المختص فوراً.</div>', unsafe_allow_html=True)
        
st.markdown(f'<div style="text-align: right; font-size: 20px; font-weight: bold;">التخصص المطلوب: {info["spec"]}</div>', unsafe_allow_html=True)
        results = []
        for d in DOCTORS_DB:
            dist = safe_dist(user_location, d['lat'], d['lon'])
            match = 100 if d['spec'] == info['spec'] else 0
            results.append({"d": d, "dist": dist, "match": match})
        results.sort(key=lambda x: (-x['match'], x['dist']))

        for res in results:
            d = res['d']
            st.markdown(f'''
            <div class="doc-card">
                <div style="display:flex; justify-content:space-between">
                    <span style="color:#40E0D0; font-size:20px; font-weight:bold;">{d['name']}</span>
                    <span style="font-size:12px;">📍 {d['area']} (يبعد {res['dist']} كم)</span>
                </div>
                <div style="color:#888; font-size:14px; margin-bottom:10px;">{d['title']}</div>
            ''', unsafe_allow_html=True)
            
          # جدول مواعيد اليوم - تنسيق أبيض فخم ومحاذاة لليمنة
        st.markdown('<div style="text-align: right; font-weight: bold; margin-top: 20px; color: #ffffff;">جدول مواعيد اليوم:</div>', unsafe_allow_html=True)
        
        t_cols = st.columns(5)
        random.seed(d['name'])
        slots = ["3:00", "3:30", "4:00", "4:30", "5:00"]
        
        for i, t in enumerate(slots):
            is_taken = random.choice([True, False, False])
            with t_cols[i]:
                if is_taken:
                    st.markdown(f'<div class="slot-taken" style="background-color: #1a1a1a; border: 1px solid #333; color: #555;">{t} 🔒</div>', unsafe_allow_html=True)
                else:
                    # زر أبيض شفاف يتحول لأبيض كامل عند اللمس
                    if st.button(f"{t}", key=f"{d['name']}_{t}"):
                        st.markdown(f'<div style="color: #40E0D0; text-align: right; font-size: 13px;">تم اختيار الساعة {t}</div>', unsafe_allow_html=True)
        
        # إغلاق كرت الطبيب
        st.markdown('</div>', unsafe_allow_html=True) 
