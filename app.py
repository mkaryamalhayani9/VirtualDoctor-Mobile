import sqlite3
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, session
import pickle
import numpy as np
import os # <--- تم إضافته

# تحديد مسار المجلد الحالي للمشروع
PROJECT_ROOT = os.path.dirname(os.path.abspath(_file_))

# تحديد مسار قاعدة البيانات باستخدام المسار المطلق
DB_NAME = os.path.join(PROJECT_ROOT, 'virtual_doctor.db')

# تحميل نموذج التعلم الآلي باستخدام المسار المطلق
with open(os.path.join(PROJECT_ROOT, 'model.pkl'), 'rb') as file:
    model = pickle.load(file)

# تحديد مسار مجلد الـ templates للمساعدة في تحديد الموقع على الخادم
TEMPLATES_FOLDER = os.path.join(PROJECT_ROOT, 'templates')

# تعريف تطبيق Flask مع تحديد مسار الـ templates الجديد
app = Flask(_name_, template_folder=TEMPLATES_FOLDER) # <--- سطر معدل
app.secret_key = 'your_secret_key_here' # يجب تغيير هذا المفتاح إلى مفتاح سري حقيقي

# --- دوال قاعدة البيانات ---

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    # جدول المستخدمين
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL
        );
    ''')
    # جدول المواعيد
    conn.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            phone TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    ''')
    conn.commit()
    conn.close()

# تهيئة قاعدة البيانات عند تشغيل التطبيق (للتأكد)
init_db()

# --- مسارات التطبيق (Routes) ---

@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('home.html')

# مسار تسجيل الدخول
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user['id']
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')

# مسار التسجيل
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        try:
            conn = get_db_connection()
            conn.execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)', (username, password, email))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return render_template('register.html', error='Username or Email already exists.')
    return render_template('register.html')

# مسار تسجيل الخروج
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

# مسار التشخيص
@app.route('/consultation', methods=['GET', 'POST'])
def consultation():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        try:
            # جمع المدخلات من النموذج
            inputs = [
                float(request.form.get('input1', 0)),
                float(request.form.get('input2', 0)),
                float(request.form.get('input3', 0)),
                float(request.form.get('input4', 0)),
                float(request.form.get('input5', 0)),
                float(request.form.get('input6', 0)),
                float(request.form.get('input7', 0)),
                float(request.form.get('input8', 0))
            ]
            
            # تحويل المدخلات إلى مصفوفة NumPy
            features = np.array([inputs])
            
            # إجراء التنبؤ
            prediction = model.predict(features)[0]
            
            # تحويل النتيجة إلى نص
            result_text = "مرتفع" if prediction == 1 else "منخفض"
            
            return render_template('results.html', result=result_text, prediction_value=prediction)
            
        except Exception as e:
            # في حالة حدوث أي خطأ
            return render_template('consultation.html', error=f"An error occurred: {e}")
            
    return render_template('consultation.html')

# مسار حجز موعد
@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        user_id = session['user_id']
        name = request.form['name']
        age = request.form['age']
        date = request.form['date']
        time = request.form['time']
        phone = request.form['phone']

        try:
            conn = get_db_connection()
            conn.execute('INSERT INTO appointments (user_id, name, age, date, time, phone) VALUES (?, ?, ?, ?, ?, ?)', 
                         (user_id, name, age, date, time, phone))
            conn.commit()
            conn.close()
            return redirect(url_for('booking_success'))
        except Exception as e:
            return render_template('booking.html', error=f"An error occurred: {e}")
            
    return render_template('booking.html')

# مسار نجاح الحجز
@app.route('/booking_success')
def booking_success():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('booking_success.html')