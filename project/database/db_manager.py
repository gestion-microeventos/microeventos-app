import os
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

# Cargar las variables de entorno del archivo .env
load_dotenv()

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
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT", "5432")
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
        # No hay conexión, falló la operación
        return False

    try:
        with conn.cursor() as cursor:
            # Ejecuta la consulta. Para INSERT/UPDATE/DELETE, no hay "resultados para fetch".
            cursor.execute(query, params)
        conn.commit() # Confirma la transacción
        return True # La operación fue exitosa
    except Exception as e:
        conn.rollback() # Deshace la transacción si hubo un error
        print(f"Error al ejecutar la consulta: {e}")
        return False # La operación falló
    finally:
        close_connection(conn) # Asegura que la conexión se cierre

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

"""
    Ejecuta una consulta SQL y retorna todos los resultados como una lista de diccionarios.
"""
def fetch_all_query(query, params=None):
    
    conn = get_connection()
    if conn is None:
        return []
    
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            
            # Obtiene los nombres de las columnas
            columns = [col[0] for col in cursor.description]
            
            # Obtiene todas las filas y las convierte a una lista de diccionarios
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            return results
            
    except Exception as e:
        print(f"Error al ejecutar la consulta de obtención de datos: {e}")
        return []
    finally:
        close_connection(conn)

def fetch_one_query(query, params=None):
    """
    Ejecuta una consulta SQL y retorna la primera fila de resultados como un diccionario.
    Retorna None si no hay resultados o si ocurre un error.
    """
    conn = get_connection()
    if conn is None:
        return None

    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            
            # Obtiene los nombres de las columnas
            columns = [desc[0] for desc in cursor.description]
            
            # Obtiene la primera fila
            row = cursor.fetchone()
            
            # Si se encontró una fila, la convierte en un diccionario
            if row:
                return dict(zip(columns, row))
            else:
                return None
            
    except Exception as e:
        print(f"Error al ejecutar la consulta de obtención de datos: {e}")
        return None
    finally:
        close_connection(conn)