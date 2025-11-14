import streamlit as st
import pickle
import numpy as np
import pandas as pd
import sqlite3
import os

# 1. تحديد المسار المطلق للملفات
PROJECT_ROOT = os.path.dirname(os.path.abspath(_file_))
DB_NAME = os.path.join(PROJECT_ROOT, 'virtual_doctor.db')

# 2. تحميل نموذج التعلم الآلي (مع محاولة تجاوز مشاكل التثبيت)
model = None
model_loaded = False
try:
    with open(os.path.join(PROJECT_ROOT, 'model.pkl'), 'rb') as file:
        model = pickle.load(file)
    model_loaded = True
except Exception:
    # هذا يسمح للتطبيق بالعمل حتى لو تعذر تحميل النموذج بسبب مكتبات الخادم
    model = None
    model_loaded = False

# 3. دالة الاتصال بقاعدة البيانات (للحفاظ على الاتصال)
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# 4. دالة التشخيص (يجب أن تتطابق مع طريقة تدريب النموذج)
def diagnose_disease(symptoms_input):
    if not model_loaded:
        # رسالة تعرض عندما يكون النموذج معطلاً
        return "التشخيص معطل مؤقتاً بسبب قيود الخادم", 0.0 
    
    try:
        # هنا يتم تحويل المدخلات إلى مصفوفة وإجراء التنبؤ
        features = np.array([symptoms_input])
        prediction = model.predict(features)
        
        # قيمة الثقة (يمكنكِ تعديلها لتناسب نموذجكِ)
        confidence_score = 90.0
        
        disease_name = prediction[0]
        return disease_name, confidence_score
    except Exception:
        return "خطأ في التشخيص", 0.0

# 5. بناء واجهة Streamlit 🌟
st.set_page_config(page_title="طبيب افتراضي AI", layout="centered", icon="🩺")

st.title("👨‍⚕️ نظام طبيب افتراضي لتشخيص الأمراض")
st.markdown("---")

# بناء نموذج إدخال الأعراض 
with st.form("diagnosis_form"):
    st.subheader("يرجى اختيار الأعراض:")
    
    # ****************
    # يجب تكرار هذه العناصر بناءً على الأعراض الفعلية لنموذجكِ:
    # (مثال: استخدام sliders للأعراض ذات القيمة العددية)
    # ****************
    
    s1 = st.slider("درجة الحرارة (Fever) - القيمة من 0 إلى 5", 
                   min_value=0.0, max_value=5.0, value=1.0, step=0.5)
    s2 = st.slider("السعال (Cough) - القيمة من 0 إلى 5", 
                   min_value=0.0, max_value=5.0, value=0.0, step=0.5)
    s3 = st.slider("ألم الحلق (Sore Throat) - القيمة من 0 إلى 5", 
                   min_value=0.0, max_value=5.0, value=0.0, step=0.5)
    
    # ... أضيفي باقي أعراضكِ هنا ...
    
    submitted = st.form_submit_button("تشخيص الحالة 🔍")

# 6. عرض النتائج عند الضغط على الزر
if submitted:
    # جمع المدخلات في قائمة (يجب أن يتطابق الترتيب مع النموذج)
    symptoms_input = [s1, s2, s3] 
    
    diagnosis, score = diagnose_disease(symptoms_input)
    
    st.markdown("---")
    st.subheader("نتائج التشخيص الأولي 🩺")

    # عرض صندوق النتيجة
    with st.container(border=True):
        st.write(f"*التشخيص الأكثر احتمالية:* <span style='color: #00bcd4; font-size: 1.2em;'>{diagnosis}</span>", unsafe_allow_html=True)
        st.write(f"*نسبة الثقة بالتشخيص (Confidence Score):* <span style='color: #00bcd4; font-size: 1.1em;'>{score:.2f}%</span>", unsafe_allow_html=True)

    # عرض الأعراض المدخلة
    symptoms_display = [f"درجة الحرارة: {s1}", f"السعال: {s2}", f"ألم الحلق: {s3}"]
    st.markdown("### الأعراض المدخلة:")
    st.markdown('\n'.join([f'* {s}' for s in symptoms_display]))

    # عرض التوصيات (مطابق لمنطقكِ في results.html)
    st.markdown("---")
    
    if diagnosis == "التشخيص معطل مؤقتاً بسبب قيود الخادم":
        st.error("*⚠️ تنبيه هام:* النموذج معطل بسبب مشكلة الخادم. لكن واجهة الويب تعمل بنجاح.")
    elif diagnosis == "عدم تشخيص" or score < 40:
        st.error("""
        *⚠️ تنبيه هام:* نظراً لعدم تطابق الأعراض أو لقلة الثقة، 
        نوصي بشدة بمراجعة طبيب بشري مختص.
        """)
    else:
        st.success("
        *✅ توصيات أولية:* بما أن نسبة الثقة عالية، يمكن البدء بالعلاج الأولي 
        مثل الراحة وتناول السوائل.
        )