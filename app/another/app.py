import os
import pickle
import pandas as pd
import psycopg2
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()
app = Flask(__name__)
CORS(app)

# --- KONEKSI SUPABASE (POSTGRESQL) ---
def get_db_connection():
    try:
        connection_url = os.getenv("DATABASE_URL")
        conn = psycopg2.connect(connection_url)
        return conn
    except Exception as e:
        print(f"Error koneksi database: {e}")
        return None

# try:
#     with open('model_hipertensi.pkl', 'rb') as f:
#         model = pickle.load(f)
# except FileNotFoundError:
#     model = None
#     print("Peringatan: Model tidak ditemukan!")

def generate_saran(prediction, data):
    # Deskripsi Risiko sesuai Kebutuhan Pengguna [cite: 224]
    if prediction == 2:
        status = "Risiko Tinggi"
        pesan = "Peringatan! Segera lakukan pemeriksaan medis di Puskesmas terdekat."
    elif prediction == 1:
        status = "Risiko Sedang"
        pesan = "Waspada. Anda memiliki beberapa faktor risiko yang perlu diperbaiki."
    else:
        status = "Risiko Rendah"
        pesan = "Kondisi Anda baik. Tetap pertahankan pola hidup sehat ini."

    # Saran Berdasarkan Variabel Spesifik (Tabel 3.1) [cite: 231]
    tips = []
    if data.get('garam') >= 4: tips.append("Kurangi asupan garam harian.")
    if data.get('olahraga') < 3: tips.append("Tingkatkan frekuensi aktivitas fisik.")
    if data.get('rokok'): tips.append("Hentikan kebiasaan merokok segera.")
    if data.get('stress') >= 4: tips.append("Lakukan teknik relaksasi untuk mengelola stres.")
    
    return status, f"{pesan} Tips: {' '.join(tips)}"

# --- 1. REGISTRASI PENGGUNA ---
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    
    hashed_pw = generate_password_hash(password)
    
    conn = get_db_connection()
    if not conn: return jsonify({"error": "Database connection failed"}), 500
    
    cur = conn.cursor()
    try:
        # Simpan ke tabel users dan profile sesuai ERD [cite: 357, 398]
        cur.execute("INSERT INTO users (email, password) VALUES (%s, %s) RETURNING user_id", (email, hashed_pw))
        user_id = cur.fetchone()[0]
        cur.execute("INSERT INTO profile (user_id, name) VALUES (%s, %s)", (user_id, name))
        conn.commit()
        return jsonify({"message": "Registrasi berhasil"}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        cur.close()
        conn.close()

# --- 2. LOGIN PENGGUNA ---
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT user_id, password FROM users WHERE email = %s", (email,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if user and check_password_hash(user[1], password):
        # Mengembalikan user_id untuk disimpan di frontend [cite: 271, 303]
        return jsonify({"user_id": user[0], "message": "Login berhasil"}), 200
    return jsonify({"message": "Kredensial salah"}), 401

# --- 3. SKRINING & INFERENCE ENGINE AI ---
# def screening():
#     data = request.json
#     input_df = pd.DataFrame([{
#         "usia": data['usia'], "tb": data['tb'], "bb": data['bb'],
#         "garam": data['garam'], "lemak": data['lemak'], "kafein": data['kafein'],
#         "olahraga": data['olahraga'], "tidur": data['tidur'], "stress": data['stress'],
#         "rokok": 1 if data['rokok'] else 0, "keturunan": 1 if data['keturunan'] else 0
#     }])

#     # Proses Klasifikasi (Inference Engine) 
#     pred = int(model.predict(input_df)[0])
#     status, saran = generate_saran(pred, data)

#     # Simpan ke Database (Tabel Screening & Prediction) [cite: 398]
#     conn = get_db_connection()
#     cur = conn.cursor()
#     cur.execute("INSERT INTO screening (user_id, tb, bb, garam, olahraga, rokok) VALUES (%s,%s,%s,%s,%s,%s) RETURNING screening_id",
#                 (data['user_id'], data['tb'], data['bb'], data['garam'], data['olahraga'], data['rokok']))
#     sid = cur.fetchone()[0]
#     cur.execute("INSERT INTO prediction (screening_id, hasil_prediksi, saran) VALUES (%s,%s,%s)", (sid, status, saran))
#     conn.commit()
    
#     return jsonify({"status": status, "saran": saran})

# --- 4. RIWAYAT PEMERIKSAAN ---
# @app.route('/api/history/<int:user_id>', methods=['GET'])
# def get_history(user_id):
#     conn = get_db_connection()
#     cur = conn.cursor()
#     # Mengambil riwayat dengan JOIN sesuai rancangan ERD [cite: 357, 399]
#     cur.execute("""
#         SELECT s.created_at, p.hasil_prediksi, s.bb 
#         FROM screening s 
#         JOIN prediction p ON s.screening_id = p.screening_id 
#         WHERE s.user_id = %s ORDER BY s.created_at DESC
#     """, (user_id,))
#     rows = cur.fetchall()
#     cur.close()
#     conn.close()
    
#     return jsonify([{"date": r[0].strftime("%d/%m/%Y"), "result": r[1], "weight": r[2]} for r in rows])

if __name__ == '__main__':
    app.run(debug=True, port=5000)