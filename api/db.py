import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from contextlib import contextmanager

load_dotenv()

@contextmanager
def get_conn():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=int(os.getenv("DB_PORT", 5432)),
    )
    try:
        yield conn
    finally:
        conn.close()

def fetch_one(query, params=None):
    with get_conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(query, params)
        return cur.fetchone()

def execute(query, params=None):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(query, params)
        conn.commit()
