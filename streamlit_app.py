import streamlit as st
import math
import random
from streamlit_js_eval import get_geolocation

# --- 1. التصميم البصري ---
st.set_page_config(page_title="Al Doctor AI - Pro", layout="wide")

st.markdown(r'''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    * { font-family: 'Tajawal', sans-serif; direction: rtl; }
    .stApp { background-color: #050505; color: #e0e0e0; }
    .classic-logo { color: #40E0D0; text-align: center; font-size: 50px; font-weight: bold; margin-bottom: 10px; }
    .auth-box { max-width: 600px; margin: auto; padding: 25px; background-color: #0d0d0d; border-radius: 15px; border: 1px solid rgba(64, 224, 208, 0.2); text-align: right; }
    .doc-card { background-color: #0d0d0d; padding: 20px; border-radius: 15px; border-right: 6px solid #40E0D0; margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.05); }
    .slot-taken { background-color: #1a1a1a; color: #555; padding: 8px; border-radius: 5px; text-align: center; text-decoration: line-through; font-size: 12px; border: 1px solid #333; }
    .warning-box { background-color: #332b00; color: #ffcc00; padding: 10px; border-radius: 8px; font-size: 12px; border: 1px solid #ffcc00; margin-top: 10px; text-align: center; }
    .stars { color: #FFD700; font-size: 18px; margin-top: 5px; }
    .stButton>button { 
        background: linear-gradient(135deg, #1d4e4a 0%, #40E0D0 100%) !important; 
        color: #000 !important; font-weight: bold; border-radius: 8px; width: 100%; border: none;
    }
    </style>
    ''', unsafe_allow_html=True)

# --- 2. البيانات الكاملة (24 عرضاً) ---
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
    "ألم حاد بالتبول": {"spec": "مسالك بولية", "urgency": 5, "diag": "التهاب مجاري", "acc": "94%"},
    "اصفرار العين": {"spec": "باطنية/كبد", "urgency": 7, "diag": "التهاب كبد", "acc": "88%"},
    "كسر عظمي": {"spec": "عظام", "urgency": 9, "diag": "كسر", "acc": "99%"}
}

DOCTORS_DB = [
    {"name": "د. علي الركابي", "title": "استشاري قلبية", "spec": "قلبية", "area": "الحارثية", "lat": 33.322, "lon": 44.358, "stars": 5},
    {"name": "د. عمر الجبوري", "title": "أخصائي جملة عصبية", "spec": "جملة عصبية", "area": "المنصور", "lat": 33.325, "lon": 44.348, "stars": 4},
    {"name": "د. سارة لؤي", "title": "أخصائية جلدية", "spec": "جلدية", "area": "زيونة", "lat": 33.332, "lon": 44.455, "stars": 5},
    {"name": "د. مريم القيسي", "title": "استشارية مفاصل", "spec": "مفاصل", "area": "الكرادة", "lat": 33.313, "lon": 44.429, "stars": 4},
    {"name": "د. ليث الحسيني", "title": "أخصائي صدرية", "spec": "صدرية", "area": "شارع فلسطين", "lat": 33.345, "lon": 44.430, "stars": 5}
]

# --- 3. محرك الحسابات ---
def calculate_safe_dist(u_loc, d_lat, d_lon):
    try:
        if u_loc and 'coords' in u_loc:
            lat1 = u_loc['coords'].get('latitude')
            lon1 = u_loc['coords'].get('longitude')
            if lat1 is not None and lon1 is not None:
                return round(math.sqrt((lat1 - d_lat)*2 + (lon1 - d_lon)*2) * 111, 1)
    except: pass
    return 999.0

st.markdown('<div class="classic-logo">Al Doctor</div>', unsafe_allow_html=True)
user_location = get_geolocation()

st.markdown('<div class="auth-box">', unsafe_allow_html=True)
selected = st.multiselect("حدد الأعراض الظاهرة:", list(SYMPTOMS_DB.keys()))
if st.button("شخص الآن وحدد الأقرب 🔍"):
    if selected: st.session_state.active_s = selected
st.markdown('</div>', unsafe_allow_html=True)

if "active_s" in st.session_state:
    main_s = max(st.session_state.active_s, key=lambda s: SYMPTOMS_DB[s]['urgency'])
    info = SYMPTOMS_DB[main_s]
    
    st.write("---")
    st.success(f"🤖 تحليل الذكاء الاصطناعي: {info['diag']} (دقة التوقع: {info['acc']})")
    st.markdown(f'<div class="warning-box">⚠️ تنبيه: هذا التشخيص استرشادي ولا يعتبر استشارة طبية معتمدة.</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="text-align: right; font-size: 20px; font-weight: bold; margin-top:15px; color:#40E0D0;">التخصص المطلوب: {info["spec"]}</div>', unsafe_allow_html=True)
    
    # الترتيب حسب الأقرب
    results = []
    for d in DOCTORS_DB:
        dist = calculate_safe_dist(user_location, d['lat'], d['lon'])
        results.append({"d": d, "dist": dist})
    results.sort(key=lambda x: x['dist'])

    for res in results:
        d = res['d']
        dist_label = f"{res['dist']} كم" if res['dist'] < 900 else "يرجى تفعيل الموقع"
        
        st.markdown(f'''
        <div class="doc-card">
            <div style="display:flex; justify-content:space-between">
                <div>
                    <span style="color:#40E0D0; font-size:22px; font-weight:bold;">{d['name']}</span>
                    <div class="stars">{"⭐" * d['stars']}</div>
                </div>
                <div style="text-align: left;">
                    <span style="font-size:14px; color:#bbb;">📍 {d['area']}</span><br>
                    <span style="font-size:14px; color:#40E0D0;">📏 يبعد عنك: {dist_label}</span>
                </div>
            </div>
            <div style="color:#888; font-size:15px; margin-top:5px;">{d['title']}</div>
        ''', unsafe_allow_html=True)
        
        # جدول المواعيد
        st.markdown('<div style="text-align: right; font-weight: bold; margin-top: 15px;">المواعيد المتاحة اليوم:</div>', unsafe_allow_html=True)
        cols = st.columns(5)
        times = ["3:00", "3:30", "4:00", "4:30", "5:00"]
        for i, t in enumerate(times):
            random.seed(d['name'] + t)
            is_taken = random.choice([True, False, False])
            with cols[i]:
                if is_taken:
                    st.markdown(f'<div class="slot-taken">{t} 🔒</div>', unsafe_allow_html=True)
                else:
                    if st.button(f"{t}", key=f"{d['name']}_{t}"):
                        st.balloons()
                        st.info(f"تم حجز موعدك عند {d['name']} الساعة {t}")
        st.markdown('</div>', unsafe_allow_html=True)
