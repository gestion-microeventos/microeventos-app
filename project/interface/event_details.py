import tkinter as tk
from tkinter import ttk, messagebox
from ..services import event_manager
from .new_event import NewEventWindow

class EventDetailsWindow(tk.Toplevel):
    def __init__(self, master, event_data, user_id):
        super().__init__(master)

        self.master = master
        self.event_data = event_data
        self.user_id = user_id

        self.title("Detalles del Evento")
        self.geometry("450x450")
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
        ttk.Label(info_frame, text=f"Fecha (yyyy-mm-dd): {event_data.get('event_date', 'N/A')}").pack(anchor="w")
        # Categoría
        ttk.Label(info_frame, text=f"Categoría: {event_data.get('category', 'N/A')}").pack(anchor="w")
        # Precio
        ttk.Label(info_frame, text=f"Precio: ${event_data.get('price', 'N/A')}").pack(anchor="w")
        # Cupos
        ttk.Label(info_frame, text=f"Cupos Disponibles: {event_data.get('available_tickets', 'N/A')}").pack(anchor="w")
        
        ttk.Separator(main_frame, orient="horizontal").pack(fill="x", pady=10)
        button_frame = ttk.Frame(self)
        button_frame.pack(side="bottom", fill="x", padx=20, pady=10)
        try:
            event_creator_id = int(self.event_data.get('creator_id'))
        except (ValueError, TypeError):
            event_creator_id = None # Si no se puede convertir, no es válido
            print("Advertencia: creator_id del evento no es un número válido.")

        try:
            current_user_id = int(self.user_id)
        except (ValueError, TypeError):
            current_user_id = None
            print("Advertencia: user_id del usuario no es un número válido.")


        #Boton editar
        edit_button = ttk.Button(button_frame, 
                                     text="Editar Evento", 
                                     style="Edit.TButton", # Asumiendo que tienes un estilo 'Edit.TButton'
                                     command=self._edit_event)
        edit_button.pack(side="left", padx=5)
        #Boton eliminar
        if event_creator_id is not None and current_user_id is not None and event_creator_id == current_user_id:
            ttk.Separator(main_frame, orient="horizontal").pack(fill="x", pady=10)

            delete_button = ttk.Button(button_frame,
                           text="Eliminar Evento",
                           style="Red.TButton",
                           command=self._delete_event)
            
            delete_button.pack(side="left", padx=5)
        #Boton cancelar
        close_button = ttk.Button(button_frame, 
                             text="Cerrar",
                             style="Blue.TButton",
                             command=self.destroy)
        close_button.pack(side="right", padx=5)

        
    def _edit_event(self):
        """Abre la ventana de edición con los datos del evento actual."""
        # Asegúrate de que event_data tiene el ID del evento para que NewEventWindow sepa que está editando
        if 'id' not in self.event_data:
            messagebox.showerror("Error", "No se pudo obtener el ID del evento para editar.")
            return
        # La forma correcta de llamar sería:
        edit_window = NewEventWindow(self, event_data=self.event_data, user_id=self.user_id)
        
        # Si necesitas recargar las tablas después de editar, puedes hacerla modal y luego recargar
        self.wait_window(edit_window) # Espera a que la ventana de edición se cierre
        
        # Recargar las tablas después de cerrar la ventana de edición
        self.master._load_my_events()
        self.master._load_all_events()
        self.destroy() # Cierra la ventana de detalles después de editar y recargar

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