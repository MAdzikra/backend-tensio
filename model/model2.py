import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.model_selection import KFold, cross_val_predict
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.preprocessing import LabelEncoder
import pickle

df = pd.read_csv('hypertension_dataset.csv')
print(f"Dataset berhasil dimuat. Total data: {df.shape[0]} baris.")

df_clean = df.copy()
encoders = {}

categorical_cols = df_clean.select_dtypes(include=['object']).columns

for col in categorical_cols:
    le = LabelEncoder()
    df_clean[col] = le.fit_transform(df_clean[col])
    encoders[col] = le

X = df_clean.drop(columns=['Has_Hypertension'])
y = df_clean['Has_Hypertension']

model = DecisionTreeClassifier(
    criterion='entropy', 
    max_depth=10, 
    class_weight='balanced', 
    random_state=42
)


kf = KFold(n_splits=5, shuffle=True, random_state=42)
print("Sedang memproses pengujian K-Fold...")
y_pred = cross_val_predict(model, X, y, cv=kf)

accuracy = accuracy_score(y, y_pred)
print(f"\n======================================")
print(f"AKURASI MODEL: {accuracy * 100:.2f}%")
print(f"======================================")

print("\nLAPORAN KLASIFIKASI:")
print(classification_report(y, y_pred, target_names=['Normal (0)', 'Hipertensi (1)']))

cm = confusion_matrix(y, y_pred)
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=['Prediksi Normal', 'Prediksi Hipertensi'], 
            yticklabels=['Aktual Normal', 'Aktual Hipertensi'])
plt.title('Confusion Matrix - Skrining Risiko Hipertensi')
plt.xlabel('Prediksi Sistem')
plt.ylabel('Kenyataan (Aktual)')
plt.show()

model.fit(X, y)
feat_importances = pd.Series(model.feature_importances_, index=X.columns)
plt.figure(figsize=(10, 6))
feat_importances.nlargest(10).plot(kind='barh', color='teal')
plt.title('10 Variabel Utama Penentu Risiko Hipertensi')
plt.xlabel('Tingkat Kepentingan (Gini/Entropy Importance)')
plt.show()

filename = 'model_hipertensi.pkl'
with open(filename, 'wb') as file:
    pickle.dump(model, file)

with open('encoders.pkl', 'wb') as f:
    pickle.dump(encoders, f)

print(f"\nModel berhasil disimpan dengan nama: {filename}")