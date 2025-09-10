import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from ..services import event_manager

"pip install tkcalendar"
class NewEventWindow(tk.Toplevel):
    """
    Clase que representa la ventana del formulario para crear un nuevo evento.
    """
    def __init__(self, master=None, user_id=None,):
        super().__init__(master)

        self.user_id = user_id
        self.title("Crear Nuevo Evento")
        self.geometry("600x650")
        self.resizable(False, False)
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Crea y organiza los widgets del formulario."""
        
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título del formulario
        ttk.Label(main_frame, text="Crear Nuevo Evento", font=("Arial", 16, "bold")).pack(pady=10)

        # Nombre del Evento
        ttk.Label(main_frame, text="Nombre del Evento:").pack(anchor="w", pady=(10, 0))
        self.name_entry = ttk.Entry(main_frame, width=50)
        self.name_entry.pack(fill=tk.X)

        # Descripción
        ttk.Label(main_frame, text="Descripción:").pack(anchor="w", pady=(10, 0))
        self.description_text = tk.Text(main_frame, height=5, width=50)
        self.description_text.pack(fill=tk.X)

        # Fecha del Evento
        ttk.Label(main_frame, text="Fecha:").pack(anchor="w", pady=(10, 0))
        self.date_entry = DateEntry(main_frame, width=12, background='darkblue', foreground='white', borderwidth=2)
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

    def _save_event(self):
        """
        Método para manejar el guardado del evento.
        Recoge, valida y envía los datos al gestor de eventos.
        """
        name = self.name_entry.get()
        description = self.description_text.get("1.0", tk.END).strip()
        event_date = self.date_entry.get()
        category = self.category_entry.get()
        price = self.price_entry.get()
        tickets = self.tickets_entry.get()

        # Usar un diccionario para pasar los datos al gestor
        event_data = {
            'name': name,
            'description': description,
            'date': event_date,
            'category': category,
            'price': price,
            'tickets': tickets,
            'creator_id': self.user_id
        }

        # Llama al gestor de eventos para crear el evento
        success = event_manager.create_event(event_data)

        if success:
            self.destroy() # Cierra la ventana solo si el evento se creó exitosamente

        # El gestor de eventos ya maneja los popups, por lo que no es necesario aquí.
        # Si `create_event` devuelve `False`, el popup de error ya se mostró.