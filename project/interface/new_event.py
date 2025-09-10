import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from ..services import event_manager
from ..database import db_manager
from datetime import datetime

class NewEventWindow(tk.Toplevel):
    """
    Clase que representa la ventana del formulario para crear o editar un evento.
    """
    def __init__(self, master=None, event_data=None, user_id=None):
        super().__init__(master)

        self.master = master
        self.event_data = event_data
        self.user_id = user_id
        
        # 📌 Cambia el título si estamos en modo de edición
        if self.event_data:
            self.title("Editar Evento")
        else:
            self.title("Crear Nuevo Evento")
            
        self.geometry("600x650")
        self.resizable(False, False)
        
        self._create_widgets()

        # 📌 Carga los datos solo si estamos editando
        if self.event_data:
            self._load_event_data_for_editing()

    def _create_widgets(self):
        """Crea y organiza los widgets del formulario."""
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 📌 Actualiza el título dinámicamente
        if self.event_data:
            title_text = "Editar Evento"
        else:
            title_text = "Crear Nuevo Evento"
        ttk.Label(main_frame, text=title_text, font=("Arial", 16, "bold")).pack(pady=10)

        # Nombre del Evento
        ttk.Label(main_frame, text="Nombre del Evento:").pack(anchor="w", pady=(10, 0))
        self.name_entry = ttk.Entry(main_frame, width=50)
        self.name_entry.pack(fill=tk.X)

        # Descripción
        ttk.Label(main_frame, text="Descripción:").pack(anchor="w", pady=(10, 0))
        self.description_text = tk.Text(main_frame, height=5, width=50)
        self.description_text.pack(fill=tk.X)

        # Fecha del Evento
        ttk.Label(main_frame, text="Fecha (yyyy-mm-dd):").pack(anchor="w", pady=(10, 0))
        self.date_entry = DateEntry(main_frame, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.date_entry.pack(anchor="w")

        # Categoría
        ttk.Label(main_frame, text="Categoría:").pack(anchor="w", pady=(10, 0))
        self.category_entry = ttk.Entry(main_frame, width=50)
        self.category_entry.pack(fill=tk.X)

        # Precio
        ttk.Label(main_frame, text="Precio:").pack(anchor="w", pady=(10, 0))
        self.price_entry = ttk.Entry(main_frame, width=50)
        self.price_entry.pack(fill=tk.X)

        # Cupos Disponibles
        ttk.Label(main_frame, text="Cupos Disponibles:").pack(anchor="w", pady=(10, 0))
        self.tickets_entry = ttk.Entry(main_frame, width=50)
        self.tickets_entry.pack(fill=tk.X)

        # Contenedor para los botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        # Botones de Acción
        self.save_button = ttk.Button(button_frame, text="Guardar Evento", command=self._save_event)
        self.save_button.pack(side=tk.LEFT, padx=5)

        self.cancel_button = ttk.Button(button_frame, text="Cancelar", command=self.destroy)
        self.cancel_button.pack(side=tk.LEFT, padx=5)

    def _load_event_data_for_editing(self):
        """
        Carga los datos de un evento existente en el formulario para su edición.
        Este método se llama solo si `self.event_data` no es None.
        """
        self.name_entry.insert(0, self.event_data.get('name', ''))
        self.description_text.insert("1.0", self.event_data.get('description', ''))
        
        # Formatear la fecha para el widget DateEntry
        event_date_str = str(self.event_data.get('event_date', ''))
        if event_date_str:
            try:
                event_date = datetime.strptime(event_date_str, '%y-%m-%d').date()
                self.date_entry.set_date(event_date)
            except ValueError:
                # Si el formato no es el esperado, ignora la fecha
                pass
        
        self.category_entry.insert(0, self.event_data.get('category', ''))
        self.price_entry.insert(0, self.event_data.get('price', ''))
        self.tickets_entry.insert(0, self.event_data.get('available_tickets', ''))
        
        self.save_button.config(text="Actualizar Evento")
    
    def _save_event(self):
        """
        Método para manejar el guardado o la actualización del evento.
        """
        # ... (el resto del código es casi el mismo, excepto por la llamada a event_manager) ...

        # Usa un diccionario para pasar los datos
        event_data = {
            'name': self.name_entry.get(),
            'description': self.description_text.get("1.0", tk.END).strip(),
            'date': self.date_entry.get(),
            'category': self.category_entry.get(),
            'price': self.price_entry.get(),
            'tickets': self.tickets_entry.get(),
            'creator_id': self.user_id,
            'id': self.event_data.get('id') if self.event_data else None
        }

        if self.event_data:
            # 📌 Llama a la función de actualización si estamos editando
            success = event_manager.update_event(event_data)
        else:
            # Llama a la función de creación si no hay 'event_data'
            success = event_manager.create_event(event_data)
        
        if success:
            self.destroy()
            if self.master:
                self.master._load_my_events() # Asegura que la tabla de eventos del usuario se actualice
                self.master._load_all_events() # Asegura que la tabla de todos los eventos se actualice