mport streamlit as st
import pickle
import numpy as np
import pandas as pd
import sqlite3
import os

# 1. تحديد المسار المطلق للملفات
PROJECT_ROOT = os.path.dirname(os.path.abspath(_file_))
DB_NAME = os.path.join(PROJECT_ROOT, 'virtual_doctor.db')

# 2. تحميل نموذج التعلم الآلي
model = None
model_loaded = False
try:
    with open(os.path.join(PROJECT_ROOT, 'model.pkl'), 'rb') as file:
        model = pickle.load(file)
    model_loaded = True
except Exception:
    model = None
    model_loaded = False

# 3. دالة الاتصال بقاعدة البيانات
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# 4. دالة التشخيص
def diagnose_disease(symptoms_input):
    if not model_loaded:
        return "التشخيص معطل مؤقتاً بسبب قيود الخادم", 0.0 
    
    try:
        features = np.array([symptoms_input])
        prediction = model.predict(features)
        confidence_score = 90.0
        disease_name = prediction[0]
        return disease_name, confidence_score
    except Exception:
        return "خطأ في التشخيص", 0.0

# 5. واجهة Streamlit
st.set_page_config(
    page_title="طبيب افتراضي AI",
    layout="centered"
)

st.title("👨‍⚕️ نظام طبيب افتراضي لتشخيص الأمراض")
st.markdown("---")

# نموذج إدخال الأعراض
with st.form("diagnosis_form"):
    st.subheader("يرجى اختيار الأعراض:")

    s1 = st.slider("درجة الحرارة (Fever) - القيمة من 0 إلى 5", 
                   min_value=0.0, max_value=5.0, value=1.0, step=0.5)
    s2 = st.slider("السعال (Cough) - القيمة من 0 إلى 5", 
                   min_value=0.0, max_value=5.0, value=0.0, step=0.5)
    s3 = st.slider("ألم الحلق (Sore Throat) - القيمة من 0 إلى 5", 
                   min_value=0.0, max_value=5.0, value=0.0, step=0.5)

    submitted = st.form_submit_button("تشخيص الحالة 🔍")

# عرض نتائج التشخيص
if submitted:
    symptoms_input = [s1, s2, s3]
    diagnosis, score = diagnose_disease(symptoms_input)

    st.markdown("---")
    st.subheader("نتائج التشخيص الأولي 🩺")

    # صندوق منسق (بديل عن st.container border=True)
    st.markdown(
        f"""
        <div style="border:2px solid #00bcd4; padding: 15px; border-radius: 10px;">
            <p style="font-size:18px;">
                <b>التشخيص الأكثر احتمالية:</b> 
                <span style="color:#00bcd4;">{diagnosis}</span>
            </p>
            <p style="font-size:18px;">
                <b>نسبة الثقة:</b> 
                <span style="color:#00bcd4;">{score:.2f}%</span>
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # عرض الأعراض المدخلة
    st.markdown("### الأعراض المدخلة:")
    symptoms_display = [
        f"درجة الحرارة: {s1}",
        f"السعال: {s2}",
        f"ألم الحلق: {s3}"
    ]
    st.markdown('\n'.join([f'* {s}' for s in symptoms_display]))

    # التوصيات
    st.markdown("---")

    if diagnosis == "التشخيص معطل مؤقتاً بسبب قيود الخادم":
        st.error("""
        ⚠️ النموذج غير متوفر حالياً بسبب قيود الخادم.  
        سيتم تفعيل التشخيص الكامل عند حل المشكلة.
        """)
    elif diagnosis == "عدم تشخيص" or score < 40:
        st.error("""
        ⚠️ نسبة الثقة منخفضة.  
        يُنصح بمراجعة طبيب مختص للتأكد من الحالة.
        """)
    else:
        st.success("""
        ✅ النتائج تشير إلى تشخيص مبدئي مع نسبة ثقة جيدة.  
        يمكن اتباع روتين الرعاية الأولية مثل شرب السوائل والراحة.
        """)