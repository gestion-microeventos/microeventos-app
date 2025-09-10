import tkinter as tk
from tkinter import ttk, messagebox
from .new_event import NewEventWindow
from ..services import event_manager
from .event_details import EventDetailsWindow

class MainWindow(tk.Toplevel):
    """
    Clase que representa la ventana principal de la aplicación.
    Hereda de tk.Toplevel para ser una ventana secundaria.
    """
    def __init__(self, master=None, user_id=None,):
        super().__init__(master)

        self.user_id = user_id
        self.title("Gestión de Eventos")
        self.state('zoomed') # Maximiza la ventana

        # Configurar estilos personalizados
        self._configure_styles()

        self._create_widgets()


    """
        Configura los estilos de los widgets ttk.
    """
    def _configure_styles(self):
        
        style = ttk.Style(self)
        
        # Estilo para los encabezados de Treeview
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
        style.configure("Treeview", rowheight=25)
        
        # Estilo para el botón "Crear Evento" (fondo y texto del mismo color)
        style.configure("Blue.TButton", 
                        background="#007bff",  # Color de fondo azul
                        foreground="#007bff",     # Color de la letra azul
                        font=("Arial", 12, "bold"))
        style.map("Blue.TButton",
                  background=[("active", "#007bff")],
                  foreground=[("active", "#007bff")])
        
        # Estilo para el botón "Cerrar Sesión" (fondo y texto del mismo color)
        style.configure("Red.TButton",
                        background="#dc3545",  # Color de fondo rojo
                        foreground="#dc3545",     # Color de la letra rojo
                        font=("Arial", 12, "bold"))
        style.map("Red.TButton",
                  background=[("active", "#dc3545")],
                  foreground=[("active", "#dc3545")])



    """
        Crea y organiza los widgets de la ventana principal.
    """  
    def _create_widgets(self):
        
        main_pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        my_events_frame = ttk.Frame(main_pane, padding=10)
        main_pane.add(my_events_frame, weight=1)
        ttk.Label(my_events_frame, text="Mis Eventos", font=("Arial", 14, "bold")).pack(pady=5)
        # 📌 Agrega los widgets de filtro para "Mis Eventos"
        my_events_filter_frame = ttk.Frame(my_events_frame)
        my_events_filter_frame.pack(fill="x", pady=(0, 10))
        ttk.Label(my_events_filter_frame, text="Buscar:").pack(side="left", padx=(0, 5))
        self.my_events_search_entry = ttk.Entry(my_events_filter_frame, width=30)
        self.my_events_search_entry.pack(side="left", padx=5)
        ttk.Button(my_events_filter_frame, text="Filtrar", command=self._apply_my_events_filter).pack(side="left", padx=5)
        ttk.Button(my_events_filter_frame, text="Restablecer", command=self._reset_my_events_filter).pack(side="left", padx=5)
        #Mostrar los datos de Mis Eventos
        self.my_events_tree = ttk.Treeview(my_events_frame, columns=("Nombre", "Fecha", "Categoría", "Precio", "Cupos"), show="headings")
        self.my_events_tree.heading("Nombre", text="Nombre")
        self.my_events_tree.heading("Fecha", text="Fecha")
        self.my_events_tree.heading("Categoría", text="Categoría")
        self.my_events_tree.heading("Precio", text="Precio")
        self.my_events_tree.heading("Cupos", text="Cupos")
        self.my_events_tree.column("Nombre", width=120)
        self.my_events_tree.column("Fecha", width=120)
        self.my_events_tree.column("Categoría", width=90)
        self.my_events_tree.column("Precio", width=70, anchor=tk.CENTER)
        self.my_events_tree.column("Cupos", width=70, anchor=tk.CENTER)
        self.my_events_tree.bind("<<TreeviewSelect>>", self._on_event_select)

        self.my_events_tree.pack(fill=tk.BOTH, expand=True)
        # 📌 Llama a la función para cargar MIS eventos
        self._load_my_events()

        all_events_frame = ttk.Frame(main_pane, padding=10)
        main_pane.add(all_events_frame, weight=1)
        ttk.Label(all_events_frame, text="Todos los Eventos", font=("Arial", 14, "bold")).pack(pady=5)
        # 📌 Agrega los widgets de filtro para "Todos los Eventos"
        all_events_filter_frame = ttk.Frame(all_events_frame)
        all_events_filter_frame.pack(fill="x", pady=(0, 10))
        ttk.Label(all_events_filter_frame, text="Buscar:").pack(side="left", padx=(0, 5))
        self.all_events_search_entry = ttk.Entry(all_events_filter_frame, width=30)
        self.all_events_search_entry.pack(side="left", padx=5)
        ttk.Button(all_events_filter_frame, text="Filtrar", command=self._apply_all_events_filter).pack(side="left", padx=5)
        ttk.Button(all_events_filter_frame, text="Restablecer", command=self._reset_all_events_filter).pack(side="left", padx=5)
        #Mostrar datos de Todos los Eventps
        self.all_events_tree = ttk.Treeview(all_events_frame, columns=("Nombre", "Fecha", "Categoría", "Precio", "Cupos"), show="headings")
        self.all_events_tree.heading("Nombre", text="Nombre")
        self.all_events_tree.heading("Fecha", text="Fecha")
        self.all_events_tree.heading("Categoría", text="Categoría")
        self.all_events_tree.heading("Precio", text="Precio")
        self.all_events_tree.heading("Cupos", text="Cupos")
        self.all_events_tree.column("Nombre", width=120)
        self.all_events_tree.column("Fecha", width=120)
        self.all_events_tree.column("Categoría", width=90)
        self.all_events_tree.column("Precio", width=70, anchor=tk.CENTER)
        self.all_events_tree.column("Cupos", width=70, anchor=tk.CENTER)
        self.all_events_tree.bind("<<TreeviewSelect>>", self._on_event_select)

        self.all_events_tree.pack(fill=tk.BOTH, expand=True)
        # 📌 Llama a la función para cargar los eventos al iniciar
        self._load_all_events()
        
        # Contenedor para los botones inferiores (centrados)
        button_frame = ttk.Frame(self)
        button_frame.pack(side=tk.BOTTOM, pady=10)

        # Botón para crear un evento con el estilo "Blue.TButton"
        self.create_event_button = ttk.Button(button_frame, 
                                            text="Crear Evento", 
                                            style="Blue.TButton",
                                            command=self._create_event)
        self.create_event_button.pack(side=tk.LEFT, padx=5)

        # Botón de cerrar sesión con el estilo "Red.TButton"
        self.logout_button = ttk.Button(button_frame, 
                                        text="Cerrar Sesión", 
                                        style="Red.TButton",
                                        command=self.close_window)
        self.logout_button.pack(side=tk.LEFT, padx=5)
    
    """
        Abre la ventana del formulario de creación de evento como un popup.
    """
    def _create_event(self):
        
        # Desactiva la ventana principal para que el usuario no pueda interactuar con ella
        self.attributes('-disabled', True) 
        
        # Crea la ventana del formulario
        new_event_window = NewEventWindow(self, self.user_id)
        
        # Espera a que la ventana del formulario se cierre
        self.wait_window(new_event_window)
        
        # Vuelve a habilitar la ventana principal
        self.attributes('-disabled', False)
        # 📌 Recarga ambas tablas al cerrar el popup
        self._load_my_events(search_term="")
        self._load_all_events()
    
    """
        Carga todos los eventos desde la base de datos y los muestra en el Treeview.
    """
    def _load_all_events(self, search_term=""):
        
        # Limpia el Treeview para evitar duplicados cada vez que se carga
        for item in self.all_events_tree.get_children():
            self.all_events_tree.delete(item)

        # Obtiene todos los eventos desde el gestor de eventos
        events = event_manager.get_all_events(search_term)

        if events:
            for event in events:
                # Inserta cada evento como una nueva fila en el Treeview
                self.all_events_tree.insert("", "end", tags=(event['id'],), 
                                       values=(event['name'], event['event_date'], event['category'], event['price'], event['available_tickets']))
        else:    
            messagebox.showinfo("Información", "No se encontraron eventos en la base de datos.")
    
    """
        Carga los eventos creados por el usuario actual y los muestra en el Treeview.
    """
    def _load_my_events(self, search_term=""):
        
        for item in self.my_events_tree.get_children():
            self.my_events_tree.delete(item)

        # 📌 Llama a una nueva función en event_manager que filtre por user_id
        my_events = event_manager.get_events_by_creator(self.user_id, search_term)

        if my_events:
            for event in my_events:
                self.my_events_tree.insert("", "end", tags=(event['id'],), 
                                       values=(event['name'], event['event_date'], event['category'], event['price'], event['available_tickets']))
        else:
            print("No tienes eventos creados.")
        
    def close_window(self):
        """Cierra la ventana actual y muestra la ventana principal (root)."""
        self.destroy()
        if self.master:
            self.master.deiconify()
            self.master.state('zoomed')

    """
        Maneja la lógica para abrir el popup de detalles al seleccionar un evento.
    """
    def _on_event_select(self, event):
        
        # 📌 Obtiene el widget que disparó el evento (all_events_tree o my_events_tree)
        tree_widget = event.widget
        selected_items = tree_widget.selection()

        # 📌 Verifica si hay elementos seleccionados.
        if not selected_items:
            return

        # 📌 Asigna un valor a 'item_id' solo si hay una selección
        item_id = selected_items[0]
        
        # Obtiene el 'tag' (nuestro ID de la base de datos) de la fila seleccionada
        tags = tree_widget.item(item_id, 'tags')
        if not tags:
            print("Error: No se pudo encontrar el ID del evento.")
            return
        
        
        event_id = tags[0] # El ID de la base de datos es el primer elemento de la tupla de tags

        event_data = event_manager.get_event_by_id(event_id)
        if not event_data:
            messagebox.showerror("Error", "No se pudieron obtener los detalles del evento.")
            return

        self.attributes('-disabled', True)
        details_window = EventDetailsWindow(self, event_data, self.user_id)
        self.wait_window(details_window)
        self.attributes('-disabled', False)
    
    def _apply_my_events_filter(self):
        search_term = self.my_events_search_entry.get()
        self._load_my_events(search_term)
    
    def _reset_my_events_filter(self):
        self.my_events_search_entry.delete(0, tk.END)
        self._load_my_events()
    
    def _apply_all_events_filter(self):
        search_term = self.all_events_search_entry.get()
        self._load_all_events(search_term)

    def _reset_all_events_filter(self):
        self.all_events_search_entry.delete(0, tk.END)
        self._load_all_events()
    

