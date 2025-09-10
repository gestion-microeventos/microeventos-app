from ..database import db_manager
import bcrypt

# pip install bcrypt

def authenticate_user(username, password):
    """
    Verifica las credenciales del usuario y retorna su ID si son válidas.
    """
    conn = db_manager.get_connection()
    if not conn:
        return None  # Retorna None si no se puede conectar

    try:
        # 1. Consultar el usuario por su nombre, obteniendo el ID y el hash
        with conn.cursor() as cursor:
            query = "SELECT id, password_hash FROM users WHERE username = %s;"
            cursor.execute(query, (username,))
            user_data = cursor.fetchone()

        # 2. Verificar si el usuario existe
        if user_data:
            user_id = user_data[0]
            stored_hash = user_data[1].encode('utf-8')

            # 3. Verificar la contraseña
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                return user_id  # Retorna el ID del usuario
    except Exception as e:
        print(f"Error en la autenticación: {e}")
    finally:
        # 4. Cerrar la conexión
        db_manager.close_connection(conn)
    
    return None  # Retorna None si la autenticación falla por cualquier motivo