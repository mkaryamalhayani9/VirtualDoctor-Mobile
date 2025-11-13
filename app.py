import sqlite3
import os 
import pickle
import numpy as np
from flask import Flask, render_template, request, redirect, url_for, session, g

# ----------------- إعدادات Flask -----------------
app = Flask(__name__)
app.secret_key = 'your_super_secret_key_here' 

# ----------------- إعداد قاعدة البيانات -----------------
DATABASE = 'users.db'

def get_db():
    # دالة لفتح اتصال بقاعدة البيانات
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    # دالة لغلق الاتصال بقاعدة البيانات عند انتهاء الطلب
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    # التأكد من وجود قاعدة البيانات وإنشاء الجداول
    with app.app_context():
        db = get_db()
        
        # 1. جدول المستخدمين (للتسجيل والدخول)
        db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            );
        ''')
        
        # 2. جدول الأطباء (للحجز)
        db.execute('''
            CREATE TABLE IF NOT EXISTS doctors (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                specialty TEXT NOT NULL,
                is_available INTEGER NOT NULL
            );
        ''')
        
        # 3. جدول الحجوزات (لتخزين المواعيد)
        db.execute('''
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                doctor_id INTEGER NOT NULL,  
                appointment_date TEXT NOT NULL,
                appointment_time TEXT NOT NULL,
                diagnosis TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (doctor_id) REFERENCES doctors (id)  
            );
        ''')

        # إضافة الأطباء الافتراضيين (إذا لم يكونوا موجودين)
        initial_doctors = [
            ("د. أحمد علي", "عام", 1), 
            ("د. فاطمة يوسف", "باطنية", 1), 
            ("د. مريم خالد", "جلدية", 1)
        ]
        
        existing_doctors = db.execute("SELECT COUNT(*) FROM doctors").fetchone()[0]
        if existing_doctors == 0:
            for name, specialty, is_available in initial_doctors:
                db.execute(
                    "INSERT INTO doctors (name, specialty, is_available) VALUES (?, ?, ?)",
                    (name, specialty, is_available)
                )
        db.commit()

init_db()

# ----------------- إعدادات الذكاء الاصطناعي -----------------
symptoms_list = [
    'حمى', 'سعال', 'آلام في الجسم', 'تعب', 'احتقان الأنف', 'سيلان الأنف',
    'التهاب الحلق', 'صداع', 'غثيان', 'قيء', 'إسهال', 'ألم في الرقبة',
    'تشنج العضلات', 'حكة في العين', 'حساسية' # (15 عَرَضًا)
]
diseases_list = [
    'الإنفلونزا الموسمية', 'نزلات البرد', 'حساسية الربيع', 'صداع التوتر'
]

# التحقق من وتحميل النموذج
model = None
try:
    with open('model.pkl', 'rb') as file:
        model = pickle.load(file)
except FileNotFoundError:
    print("FATAL ERROR: model.pkl not found. Please run train_model.py first.")
    
# ----------------- مسارات التطبيق (Routes) -----------------

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('medical_consultation'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        db = get_db()
        try:
            db.execute(
                "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                (username, email, password)
            )
            db.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            error = 'اسم المستخدم أو البريد الإلكتروني مستخدم بالفعل.'
            
    return render_template('register.html', error=error)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE username = ? AND password = ?', 
            (username, password)
        ).fetchone()
        
        if user is None:
            error = 'اسم المستخدم أو كلمة المرور غير صحيحة.'
        else:
            session['username'] = user['username']
            return redirect(url_for('medical_consultation'))
            
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/medical_consultation', methods=['GET', 'POST'])
def medical_consultation():
    if 'username' not in session:
        return redirect(url_for('login'))
        
    if request.method == 'POST' and model:
        selected_symptoms = request.form.getlist('symptom')
        
        # 1. إنشاء متجه الإدخال (يجب أن يتطابق مع الـ 15 عَرَضًا)
        input_vector = np.zeros(len(symptoms_list))
        for symptom in selected_symptoms:
            try:
                index = symptoms_list.index(symptom)
                input_vector[index] = 1
            except ValueError:
                pass
        
        # 2. التشخيص باستخدام النموذج
        input_vector_reshaped = input_vector.reshape(1, -1)
        probabilities = model.predict_proba(input_vector_reshaped)[0]
        predicted_index = np.argmax(probabilities)
        diagnosis = diseases_list[predicted_index]
        confidence_score = probabilities[predicted_index] * 100
        
        # 3. تمرير النتائج
        return redirect(url_for('results', 
                                diagnosis=diagnosis, 
                                symptoms=selected_symptoms, 
                                score=confidence_score))
        
    return render_template('consultation.html', symptoms=symptoms_list)


@app.route('/results')
def results():
    if 'username' not in session:
        return redirect(url_for('login'))
        
    diagnosis = request.args.get('diagnosis', 'عدم تشخيص')
    symptoms = request.args.getlist('symptoms')
    score = request.args.get('score', 0.0) # استقبال نسبة الثقة
    
    return render_template('results.html', 
                           diagnosis=diagnosis, 
                           symptoms=symptoms,
                           score=score) # تمرير نسبة الثقة إلى results.html


@app.route('/book_appointment', methods=['GET', 'POST'])
def book_appointment():
    if 'username' not in session:
        return redirect(url_for('login'))
        
    db = get_db()
    user = db.execute('SELECT id FROM users WHERE username = ?', (session['username'],)).fetchone()
    
    # جلب قائمة الأطباء وأرقامهم من قاعدة البيانات
    available_doctors = db.execute(
        "SELECT id, name, specialty FROM doctors WHERE is_available = 1"
    ).fetchall()
    
    if request.method == 'POST':
        doctor_id = request.form['doctor_id'] 
        date = request.form['date']
        time = request.form['time']
        
        doctor_info = db.execute("SELECT name FROM doctors WHERE id = ?", (doctor_id,)).fetchone()
        
        if not doctor_info:
            return "خطأ: رقم الطبيب غير صحيح.", 400

        db.execute(
            "INSERT INTO appointments (user_id, doctor_id, appointment_date, appointment_time) VALUES (?, ?, ?, ?)",
            (user['id'], doctor_id, date, time)
        )
        db.commit()
        
        doctor_name = doctor_info['name'] 
        return render_template('booking_success.html', doctor=doctor_name, date=date, time=time)
        
    return render_template('booking.html', doctors=available_doctors)


if __name__ == '__main__':
    app.run(debug=True)