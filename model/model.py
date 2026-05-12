import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.model_selection import KFold, cross_val_predict
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.preprocessing import LabelEncoder

# 1. LOAD DATA
# Pastikan file csv berada di folder yang sama dengan script ini
df = pd.read_csv('hypertension_dataset.csv')
print(f"Dataset berhasil dimuat. Total data: {df.shape[0]} baris.")

# 2. PREPROCESSING
# Mengopi data agar data asli tetap aman
df_clean = df.copy()

# Encoding data kategori (jika ada kolom teks) menjadi numerik
le = LabelEncoder()
categorical_cols = df_clean.select_dtypes(include=['object']).columns
for col in categorical_cols:
    df_clean[col] = le.fit_transform(df_clean[col])
    print(f"Kolom {col} telah di-encoding.")

# 3. PEMISAHAN FITUR (X) DAN TARGET (y)
# Target berdasarkan dataset kamu adalah 'Has_Hypertension' [cite: 398]
X = df_clean.drop(columns=['Has_Hypertension'])
y = df_clean['Has_Hypertension']

# 4. INISIALISASI MODEL DECISION TREE
# Menggunakan 'entropy' sesuai metodologi di proposal kamu [cite: 84]
# max_depth=10 untuk menjaga akurasi tetap tinggi tanpa overfitting
model = DecisionTreeClassifier(
    criterion='entropy', 
    max_depth=10, 
    class_weight='balanced', 
    random_state=42
)

# 5. K-FOLD CROSS VALIDATION (5-FOLD)
# Memenuhi tahap pengujian pada metodologi penelitian [cite: 96, 200]
kf = KFold(n_splits=5, shuffle=True, random_state=42)

# Mendapatkan prediksi hasil cross-validation
print("Sedang memproses pengujian K-Fold...")
y_pred = cross_val_predict(model, X, y, cv=kf)

# 6. EVALUASI AKURASI & METRIK
accuracy = accuracy_score(y, y_pred)
print(f"\n======================================")
print(f"AKURASI MODEL: {accuracy * 100:.2f}%")
print(f"======================================")

print("\nLAPORAN KLASIFIKASI:")
print(classification_report(y, y_pred, target_names=['Normal (0)', 'Hipertensi (1)']))

# 7. VISUALISASI CONFUSION MATRIX
# Sesuai dengan rencana pengujian di Bab IV [cite: 111]
cm = confusion_matrix(y, y_pred)
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=['Prediksi Normal', 'Prediksi Hipertensi'], 
            yticklabels=['Aktual Normal', 'Aktual Hipertensi'])
plt.title('Confusion Matrix - Skrining Risiko Hipertensi')
plt.xlabel('Prediksi Sistem')
plt.ylabel('Kenyataan (Aktual)')
plt.show()

# 8. ANALISIS VARIABEL PALING BERPENGARUH (FEATURE IMPORTANCE)
# Membantu analisis di Bab IV mengenai faktor risiko utama [cite: 109]
model.fit(X, y)
feat_importances = pd.Series(model.feature_importances_, index=X.columns)
plt.figure(figsize=(10, 6))
feat_importances.nlargest(10).plot(kind='barh', color='teal')
plt.title('10 Variabel Utama Penentu Risiko Hipertensi')
plt.xlabel('Tingkat Kepentingan (Gini/Entropy Importance)')
plt.show()