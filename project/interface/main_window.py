import tkinter as tk
from tkinter import ttk

class MainWindow(tk.Toplevel):
    """
    Clase que representa la ventana principal de la aplicación.
    Hereda de tk.Toplevel para ser una ventana secundaria.
    """
    def __init__(self, master=None):
        super().__init__(master)

        self.title("Gestión de Eventos")
        self.state('zoomed') # Maximiza la ventana

        # Configurar estilos personalizados
        self._configure_styles()

        self._create_widgets()

    def _configure_styles(self):
        """Configura los estilos de los widgets ttk."""
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
        
    def _create_widgets(self):
        """Crea y organiza los widgets de la ventana principal."""
        
        main_pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        my_events_frame = ttk.Frame(main_pane, padding=10)
        main_pane.add(my_events_frame, weight=1)

        ttk.Label(my_events_frame, text="Mis Eventos", font=("Arial", 14, "bold")).pack(pady=5)
        
        self.my_events_tree = ttk.Treeview(my_events_frame, columns=("Nombre", "Fecha", "Cupos"), show="headings")
        self.my_events_tree.heading("Nombre", text="Nombre")
        self.my_events_tree.heading("Fecha", text="Fecha")
        self.my_events_tree.heading("Cupos", text="Cupos")
        self.my_events_tree.column("Nombre", width=150)
        self.my_events_tree.column("Fecha", width=100)
        self.my_events_tree.column("Cupos", width=70, anchor=tk.CENTER)
        self.my_events_tree.pack(fill=tk.BOTH, expand=True)

        all_events_frame = ttk.Frame(main_pane, padding=10)
        main_pane.add(all_events_frame, weight=1)

        ttk.Label(all_events_frame, text="Todos los Eventos", font=("Arial", 14, "bold")).pack(pady=5)
        
        self.all_events_tree = ttk.Treeview(all_events_frame, columns=("Nombre", "Categoría", "Precio"), show="headings")
        self.all_events_tree.heading("Nombre", text="Nombre")
        self.all_events_tree.heading("Categoría", text="Categoría")
        self.all_events_tree.heading("Precio", text="Precio")
        self.all_events_tree.column("Nombre", width=150)
        self.all_events_tree.column("Categoría", width=100)
        self.all_events_tree.column("Precio", width=70, anchor=tk.CENTER)
        self.all_events_tree.pack(fill=tk.BOTH, expand=True)
        
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
        
    def _create_event(self):
        """
        Método placeholder para manejar la acción de crear un evento.
        """
        print("Botón 'Crear Evento' presionado. Aquí se abriría el formulario.")
        
    def close_window(self):
        """Cierra la ventana actual y muestra la ventana principal (root)."""
        self.destroy()
        if self.master:
            self.master.deiconify()
            self.master.state('zoomed')