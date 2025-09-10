import tkinter as tk
from tkinter import ttk, messagebox
from ..services import event_manager

class EventDetailsWindow(tk.Toplevel):
    def __init__(self, master, event_data, user_id):
        super().__init__(master)

        self.master = master
        self.event_data = event_data
        self.user_id = user_id

        self.title("Detalles del Evento")
        self.geometry("450x300")
        self.resizable(False, False)

        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título del evento
        ttk.Label(main_frame, text=event_data.get('name', 'N/A'), font=("Arial", 16, "bold")).pack(pady=(0, 10))

        # Descripción
        ttk.Label(main_frame, text="Descripción:", font=("Arial", 10, "bold")).pack(anchor="w")
        description_text = tk.Text(main_frame, height=5, width=40, wrap="word")
        description_text.insert(tk.END, event_data.get('description', 'N/A'))
        description_text.config(state="disabled")
        description_text.pack(fill=tk.X, pady=(0, 10))

        # Contenedor para la información clave
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(5, 0))

        # Fecha
        ttk.Label(info_frame, text=f"Fecha: {event_data.get('event_date', 'N/A')}").pack(anchor="w")
        # Categoría
        ttk.Label(info_frame, text=f"Categoría: {event_data.get('category', 'N/A')}").pack(anchor="w")
        # Precio
        ttk.Label(info_frame, text=f"Precio: ${event_data.get('price', 'N/A')}").pack(anchor="w")
        # Cupos
        ttk.Label(info_frame, text=f"Cupos Disponibles: {event_data.get('available_tickets', 'N/A')}").pack(anchor="w")
        
        if self.user_id == self.event_data.get('creator_id'):
            ttk.Separator(main_frame, orient="horizontal").pack(fill="x", pady=10)
            
            delete_button = ttk.Button(main_frame, 
                                       text="Eliminar Evento", 
                                       style="Red.TButton", 
                                       command=self._delete_event)
            delete_button.pack(pady=10)
        
    def _delete_event(self):
        """Maneja la lógica para eliminar el evento de la base de datos."""
        response = messagebox.askyesno(
            "Confirmar Eliminación", 
            "¿Estás seguro de que quieres eliminar este evento? Esta acción no se puede deshacer."
        )

        if response:
            # Llama a la función de eliminación del gestor de eventos
            success = event_manager.delete_event(self.event_data['id'], self.user_id)
            if success:
                messagebox.showinfo("Éxito", "Evento eliminado exitosamente.")
                self.destroy()  # Cierra el popup
                self.master._load_my_events() # Recarga las tablas para reflejar el cambio
                self.master._load_all_events() # Recarga las tablas para reflejar el cambio
            else:
                messagebox.showerror("Error", "No se pudo eliminar el evento.")