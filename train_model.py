import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
import pickle
import numpy as np

# ----------------- 1. إعداد البيانات -----------------
# قائمة الأعراض والقائمة الرئيسية كما في ملف app.py
symptoms_list = [
    'حمى', 'سعال', 'آلام في الجسم', 'تعب', 'احتقان الأنف', 'سيلان الأنف',
    'التهاب الحلق', 'صداع', 'غثيان', 'قيء', 'إسهال', 'ألم في الرقبة',
    'تشنج العضلات', 'حكة في العين', 'حساسية'
]

# قائمة الأمراض (النتائج)
diseases_list = [
    'الإنفلونزا الموسمية', 'نزلات البرد', 'حساسية الربيع', 'صداع التوتر'
]

# إنشاء بيانات تجريبية (Synthetic Data) للتدريب
data = []
# الإنفلونزا: حمى، سعال، آلام في الجسم، تعب
data.extend([[1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]] * 50)
# نزلات البرد: سعال، احتقان أنف، سيلان أنف، التهاب الحلق
data.extend([[0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]] * 50)
# حساسية الربيع: حكة في العين، سيلان أنف، حساسية
data.extend([[0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1]] * 50)
# صداع التوتر: صداع، ألم في الرقبة، تشنج العضلات
data.extend([[0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0]] * 50)

# إنشاء قائمة الأهداف (Diseases)
targets = (
    [diseases_list[0]] * 50 + 
    [diseases_list[1]] * 50 + 
    [diseases_list[2]] * 50 + 
    [diseases_list[3]] * 50
)

# تحويل البيانات إلى إطار بيانات (DataFrame)
X = pd.DataFrame(data, columns=symptoms_list)
y = pd.Series(targets)

# ----------------- 2. التدريب والحفظ -----------------
# تقسيم البيانات
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# إنشاء وتدريب النموذج (Decision Tree هو أبسط نموذج)
model = DecisionTreeClassifier()
model.fit(X_train, y_train)

# حفظ النموذج باستخدام pickle
with open('model.pkl', 'wb') as file:
    pickle.dump(model, file)

print("---")
print("✅ Model trained successfully and saved as model.pkl.")
print(f"Model accuracy on test set: {model.score(X_test, y_test) * 100:.2f}%")
print("---")
print("Now run: python app.py")