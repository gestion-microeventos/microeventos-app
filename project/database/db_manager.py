import os
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

# Cargar las variables de entorno del archivo .env
load_dotenv()

# pip install psycopg2-binary
# pip install dotenv

"""
    Establece y devuelve una conexión a la base de datos PostgreSQL.
    Retorna el objeto de conexión si es exitoso, None en caso de error.
"""
def get_connection():
    conn = None
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        print("Conexión exitosa a la base de datos.")
        return conn
    
    except psycopg2.OperationalError as e:
        print(f"Error de conexión a la base de datos: {e}")
        return None

"""
    Cierra la conexión a la base de datos.
"""
def close_connection(conn):
    if conn:
        conn.close()
        print("Conexión a la base de datos cerrada.")

"""
    Ejecuta una consulta SQL con la conexión a la base de datos.
    Retorna los resultados de la consulta si hay, o None.
"""
def execute_query(query, params=None):
    conn = get_connection()
    if conn is None:
        return None
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            conn.commit()
            return cursor.fetchall()
    except psycopg2.DatabaseError as e:
        print(f"Error al ejecutar la consulta: {e}")
        conn.rollback()
        return None
    finally:
        close_connection(conn)

def insert_events_query(name, description, event_date, category, price, available_tickets, creator_id):
    query = """
        INSERT INTO events (name, description, event_date, category, price, available_tickets.creator_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    params = (name, description, event_date, category, price, available_tickets, creator_id,)
    result = execute_query(query, params)
    if result:
        return result
    return None

def insert_users_query(username, password_hash):
    query = """
        INSERT INTO users (username, password_hash)
        VALUES (%s, %s)
    """
    params = (username, password_hash,)
    result = execute_query(query, params)
    if result:
        return result
    return None
