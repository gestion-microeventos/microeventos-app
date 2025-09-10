from ..database import db_manager
from datetime import datetime
from decimal import Decimal
from tkinter import messagebox

"""
    Recibe los datos de un evento, los valida y los inserta en la base de datos.
    
    Args:
        event_data (dict): Un diccionario con los datos del evento.
    
    Returns:
        bool: True si el evento se creó exitosamente, False en caso contrario.
"""
def create_event(event_data):
    if not _validate_event_data(event_data):
        return False
    
    try:
        price = Decimal(event_data['price']) 
        tickets = int(event_data['tickets'])
        event_date = datetime.strptime(event_data['date'], '%Y/%m/%d')
        
    except (ValueError, KeyError) as e:
        messagebox.showerror("Error", "Los datos de precio, tickets o fecha no tienen el formato correcto.")
        print(f"Error de conversión de datos: {e}")
        return False
    
    # Prepara la consulta SQL
    query = """
    INSERT INTO events (name, description, event_date, category, price, available_tickets, creator_id)
    VALUES (%s, %s, %s, %s, %s, %s, %s);
    """
    params = (
        event_data['name'],
        event_data['description'],
        event_date,
        event_data['category'],
        price,
        tickets,
        event_data['creator_id']
    )
    
    # Ejecuta la consulta directamente desde db_manager
    try:
        success = db_manager.execute_query(query, params)
        if success:
            messagebox.showinfo("Éxito", "Evento guardado exitosamente.")
            return True
        else:
            messagebox.showerror("Error", "Hubo un problema al guardar el evento en la base de datos.")
            return False
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error inesperado: {e}")
        print(f"Error al ejecutar la consulta: {e}")
        return False
    
    
"""
    Función auxiliar para validar que todos los campos requeridos existen.
"""
def _validate_event_data(data):
    required_fields = ['name', 'description', 'date', 'category', 'price', 'tickets', 'creator_id']
    for field in required_fields:
        if not data.get(field):
            messagebox.showerror("Error", f"El campo '{field}' es requerido.")
            return False
    return True


"""
    Obtiene todos los eventos de la tabla 'events'.
    
    Returns:
        list of dict: Una lista de diccionarios, cada uno representando un evento.
                      Retorna una lista vacía si no hay eventos.
"""
def get_all_events(search_term=""):
    
    query = "SELECT id, name, event_date, category, price, available_tickets FROM events"
    params = [] 
    if search_term:
        query += " WHERE (name ILIKE %s OR TO_CHAR(event_date, 'YYYY-MM-DD') ILIKE %s OR description ILIKE %s OR category ILIKE %s OR TO_CHAR(price, '999999.99') ILIKE %s OR TO_CHAR(available_tickets, '999999') ILIKE %s)"
        search_param = f"%{search_term}%"
        params.extend([search_param, search_param, search_param, search_param, search_param, search_param]) # Ahora esto funciona porque params es una lista

    try:
        events = db_manager.fetch_all_query(query, tuple(params))
        return events
    except Exception as e:
        print(f"Error al obtener todos los eventos: {e}")
        return []

"""
    Obtiene todos los eventos creados por un usuario específico.
"""
def get_events_by_creator(creator_id, search_term=""):
    
    query = "SELECT id, name, event_date, category, price, available_tickets FROM events WHERE creator_id = %s"
    params = [creator_id]

    if search_term:
        # Aquí es donde se aplica el filtro de búsqueda en la consulta SQL
        query += " AND (name ILIKE %s OR TO_CHAR(event_date, 'YYYY-MM-DD') ILIKE %s OR description ILIKE %s OR category ILIKE %s OR TO_CHAR(price, '999999.99') ILIKE %s) OR TO_CHAR(available_tickets, '999999') ILIKE %s"
        search_param = f"%{search_term}%" # El '%' es para buscar coincidencias parciales (como un LIKE en SQL)
        params.extend([search_param, search_param, search_param, search_param, search_param, search_param])

    try:
        events = db_manager.fetch_all_query(query, tuple(params)) 
        return events
    except Exception as e:
        print(f"Error al obtener los eventos del creador: {e}")
        return []
    

"""
    Obtiene todos los detalles de un evento por su ID.
    
    Returns:
        dict: Un diccionario con los detalles del evento, o None si no se encuentra.
"""
def get_event_by_id(event_id):
    
    query = "SELECT id, name, description, event_date, category, price, available_tickets, creator_id FROM events WHERE id = %s;"
    params = (event_id,)

    try:
        event = db_manager.fetch_one_query(query, params)
        return event
    except Exception as e:
        print(f"Error al obtener los detalles del evento: {e}")
        return None

def delete_event(event_id, user_id):
    """
    Elimina un evento de la base de datos si el usuario es el creador.
    """
    query = "DELETE FROM events WHERE id = %s AND creator_id = %s;"
    params = (event_id, user_id)

    try:
        success = db_manager.execute_query(query, params)
        if success:
            print(f"Evento {event_id} eliminado por el usuario {user_id}.")
            return True
        else:
            print("No se pudo eliminar el evento. El usuario no es el creador o no existe.")
            return False
    except Exception as e:
        print(f"Error al eliminar el evento: {e}")
        return False
    

    
def update_event(event_data):
    """
    Actualiza un evento existente en la base de datos con los nuevos datos.
    
    Args:
        event_data (dict): Un diccionario con los datos del evento a actualizar.
    
    Returns:
        bool: True si la actualización fue exitosa, False en caso contrario.
    """
    try:
        # 1. Validar los datos
        name = event_data.get('name')
        description = event_data.get('description')
        event_date_str = event_data.get('date')
        category = event_data.get('category')
        price_str = event_data.get('price')
        tickets_str = event_data.get('tickets')
        event_id = event_data.get('id')
        creator_id = event_data.get('creator_id')

        if not all([name, event_date_str, price_str, tickets_str, event_id, creator_id]):
            messagebox.showerror("Error de Validación", "Todos los campos obligatorios deben estar llenos.")
            return False

        # 2. Convertir tipos de datos
        try:
            event_date = datetime.strptime(event_date_str, '%Y-%m-%d')
        except ValueError:
            event_date = datetime.strptime(event_date_str, '%Y/%m/%d')
            
        price = float(price_str)
        tickets = int(tickets_str)
        
        # 3. Preparar la consulta SQL
        query = """
            UPDATE events
            SET
                name = %s,
                description = %s,
                event_date = %s,
                category = %s,
                price = %s,
                available_tickets = %s
            WHERE id = %s AND creator_id = %s;
        """
        params = (name, description, event_date, category, price, tickets, event_id, creator_id)
        
        # 4. Ejecutar la consulta
        success = db_manager.execute_query(query, params)
        
        if success:
            messagebox.showinfo("Éxito", "Evento actualizado exitosamente.")
        else:
            messagebox.showerror("Error", "No se pudo actualizar el evento. Es posible que no tengas permisos para editarlo.")
            
        return success
    
    except ValueError as ve:
        messagebox.showerror("Error de Formato", f"Por favor, asegúrate de que el precio y los cupos sean números válidos. Error: {ve}")
        return False
    except Exception as e:
        messagebox.showerror("Error de Actualización", f"Ocurrió un error al actualizar el evento: {e}")
        return False