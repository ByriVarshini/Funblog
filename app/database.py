# import psycopg2
# from psycopg2.extras import RealDictCursor

# def get_db():
#     conn = psycopg2.connect(
#         host="localhost",
#         database="fastapi",
#         user="postgres",
#         password="varshu2212",
#         cursor_factory=RealDictCursor
#     )
#     try:
#         cursor = conn.cursor()
#         yield cursor 
#     finally:
#         cursor.close()
#         conn.close()

from psycopg2 import connect
from psycopg2.extras import RealDictCursor

def get_db():
    conn = connect(
        "postgresql://postgres:funblog@db.hbmjmbgbuxhygzrdkeuj.supabase.co:5432/postgres",
        cursor_factory=RealDictCursor
    )
    try:
        cursor = conn.cursor()
        yield cursor
    finally:
        cursor.close()
        conn.close()
