from ..database import db_manager
import bcrypt
from tkinter import messagebox
"""
    Crea un nuevo usuario en la base de datos de forma segura.
    Retorna True si la creación fue exitosa, False en caso contrario.
"""
def create_user(username, password):
    """
    Crea un nuevo usuario en la base de datos de forma segura.
    Retorna True si la creación fue exitosa, False en caso contrario.
    """
    # 1. Validar que el nombre de usuario no esté vacío
    if not username:
        print("Error: El nombre de usuario no puede estar vacío.")
        messagebox.showerror("Crear Cuenta", "El nombre de usuario no puede estar vacío.")
        return False

    # 2. Hashear la contraseña de forma segura
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    password_hash_str = password_hash.decode('utf-8')

    # 3. Ejecutar la consulta usando el db_manager e intentar capturar el error de unicidad
    try:
        # Intentamos insertar directamente. db_manager.insert_users_query debería devolver algo
        # (como el ID del nuevo usuario) si tiene éxito, o None/lanzar excepción si falla.
        user_id = db_manager.insert_users_query(username, password_hash_str) # Asumo que insert_users_query devuelve el ID o None

        if user_id is not None:
            print(f"Usuario '{username}' creado exitosamente con ID: {user_id}")
            messagebox.showinfo("Crear Cuenta", "¡Se ha creado su cuenta exitosamente!")
            return True
        else:
            # Esto podría pasar si insert_users_query devuelve None sin lanzar excepción
            print(f"Error desconocido al intentar crear el usuario '{username}'. db_manager devolvió None.")
            messagebox.showerror("Crear Cuenta", "Ocurrió un error desconocido al crear la cuenta.")
            return False

    except Exception as e:
        # Capturar excepciones, incluyendo la de llave duplicada
        error_message = str(e).lower()
        
        if "llave duplicada viola restricción de unicidad" in error_message or "duplicate key violates unique constraint" in error_message:
            print(f"Error: El nombre de usuario '{username}' ya está en uso.")
            messagebox.showerror("Crear Cuenta", "Este nombre de usuario ya está en uso. Por favor, elige otro.")
        else:
            # Capturar cualquier otra excepción inesperada
            print(f"Excepción inesperada al crear usuario '{username}': {e}")
            messagebox.showerror("Crear Cuenta", f"Ocurrió un error inesperado: {e}")
        
        return False