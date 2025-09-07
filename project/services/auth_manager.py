from ..database import db_manager
import bcrypt

# pip install bcrypt

"""
    Verifica las credenciales del usuario y retorna su rol si son válidas.
"""
def authenticate_user(username, password):
    
    # 1. Obtener la conexión a la base de datos
    conn = db_manager.get_connection()
    if not conn:
        return False, None
    try:

        # 2. Consultar el usuario por su nombre
        with conn.cursor() as cursor:
            query = "SELECT password_hash, role FROM users WHERE username = %s;"
            cursor.execute(query, (username,))
            user_data = cursor.fetchone()

        # 3. Verificar si el usuario existe
        if user_data:
            stored_hash = user_data[0].encode('utf-8')
            user_role = user_data[1]

            # 4. Verificar la contraseña
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                return True, user_role
    except Exception as e:
        print(f"Error en la autenticación: {e}")
        return False, None
    finally:
        # 5. Cerrar la conexión
        db_manager.close_connection(conn)
    
    return False, None