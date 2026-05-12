import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    # Mengambil URL dari file .env
    connection_url = os.getenv("DATABASE_URL")
    try:
        conn = psycopg2.connect(connection_url)
        return conn
    except Exception as e:
        print(f"Gagal terhubung ke Supabase: {e}")
        return None