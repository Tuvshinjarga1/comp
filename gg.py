import os
import psycopg2
from psycopg2.extras import DictCursor

# 1) Хамгийн энгийн — өгөгдлийг кодонд шууд бичих (анхаар: нууц үг кодонд хадгалах нь аюултай)
HOST = "13.214.153.0"
PORT = 5432
DBNAME = "postgres"
USER = "postgres"
PASSWORD = "PasswordDotaafdb"

def get_connection():
    return psycopg2.connect(
        host=HOST,
        port=PORT,
        dbname=DBNAME,
        user=USER,
        password=PASSWORD
    )

def test_query():
    conn = None
    try:
        conn = get_connection()
        with conn.cursor(cursor_factory=DictCursor) as cur:
            # Жишээ: сэрвэр дээр байгаа схем/таблуудыг харах
            cur.execute("""
                SELECT table_schema, table_name
                FROM information_schema.tables
                WHERE table_type = 'BASE TABLE'
                  AND table_schema NOT IN ('pg_catalog','information_schema')
                ORDER BY table_schema, table_name
                LIMIT 50;
            """)
            rows = cur.fetchall()
            for r in rows:
                print(r["table_schema"], r["table_name"])
    except Exception as e:
        print("Connection/query error:", e)
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    test_query()
