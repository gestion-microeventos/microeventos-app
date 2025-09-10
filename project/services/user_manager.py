from ..database import db_manager
import bcrypt
from tkinter import messagebox
"""
    Crea un nuevo usuario en la base de datos de forma segura.
    Retorna True si la creación fue exitosa, False en caso contrario.
"""
def create_user(username, password):
    
    # 1. Validar que el nombre de usuario no esté vacío
    if not username:
        print("Error: El nombre de usuario no puede estar vacío.")
        return False

    # 2. Hashear la contraseña de forma segura
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    # Convierte el hash a string para guardarlo en la BD
    password_hash_str = password_hash.decode('utf-8')

    # 3. Ejecutar la consulta usando el db_manager
    try:
        if db_manager.insert_users_query(username, password_hash_str) is not None:
            print(f"Usuario '{username}' creado exitosamente.")
            messagebox.showinfo("Crear Cuenta", "¡Se ha creado su cuenta exitosamente!")
            return True
        else:
            print(f"Error al intentar crear el usuario '{username}'.")
            return False
    except Exception as e:
        # Capturar cualquier excepción inesperada durante la ejecución de la consulta
        print(f"Excepción inesperada al crear usuario '{username}': {e}")
        return False