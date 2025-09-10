import tkinter as tk
from tkinter import ttk, messagebox
from ..services import auth_manager, user_manager
from .main_window import MainWindow

"""
    Clase que representa la ventana de inicio de sesión.
    Hereda de tk.Tk para ser la ventana principal.
"""
class LoginScreen(tk.Tk):
    
    def __init__(self):
        super().__init__()

        self.title("Gestión de Eventos - Iniciar Sesión")
        
        # Configurar pantalla completa
        self.state('zoomed') 

        self._configure_styles()
        self._create_widgets()

    """
        Configura los estilos de los botones.
    """
    def _configure_styles(self):
        style = ttk.Style(self)
        login_button = 'Login.TButton'
        create_button = 'Create.TButton'
        
        # Estilo para el botón de Iniciar Sesión (verde con borde y letra verde oscuro)
        style.configure(login_button, 
                        background='#A5D6A7',  # Verde claro para el fondo
                        foreground='#388E3C',  # Verde oscuro para la letra
                        font=('Arial', 10, 'bold'),
                        borderwidth=2,
                        relief="solid")
        style.map(login_button, 
                  background=[('active', '#C8E6C9')], # Verde muy claro al pasar el mouse
                  foreground=[('active', '#1B5E20')]) # Verde oscuro al pasar el mouse

        # Estilo para el botón de Crear Cuenta (azul con borde y letra azul oscuro)
        style.configure(create_button, 
                        background='#BBDEFB',  # Azul claro para el fondo
                        foreground='#1976D2',  # Azul oscuro para la letra
                        font=('Arial', 10, 'bold'),
                        borderwidth=2,
                        relief="solid")
        style.map(create_button,
                  background=[('active', '#E3F2FD')], # Azul muy claro al pasar el mouse
                  foreground=[('active', '#0D47A1')]) # Azul oscuro al pasar el mouse
                  
        # Eliminar el borde feo en Windows
        style.configure("TButton", borderwidth=0)

    """
        Crea y posiciona los widgets de la interfaz.
    """
    def _create_widgets(self):
        # Usamos un Frame principal que ocupa toda la ventana y lo centramos
        main_frame = ttk.Frame(self, padding="30")
        main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Labels y campos de entrada
        ttk.Label(main_frame, text="Usuario:", font=('Arial', 12)).grid(row=0, column=0, sticky="w", pady=10, padx=5)
        self.username_entry = ttk.Entry(main_frame, font=('Arial', 12), width=30)
        self.username_entry.grid(row=0, column=1, sticky="ew", pady=10, padx=5)

        ttk.Label(main_frame, text="Contraseña:", font=('Arial', 12)).grid(row=1, column=0, sticky="w", pady=10, padx=5)
        self.password_entry = ttk.Entry(main_frame, show="*", font=('Arial', 12), width=30)
        self.password_entry.grid(row=1, column=1, sticky="ew", pady=10, padx=5)

        # Botón de inicio de sesión (verde)
        login_button = ttk.Button(main_frame, text="Iniciar Sesión", command=self.attempt_login, style='Login.TButton')
        login_button.grid(row=2, column=0, columnspan=2, pady=15, padx=5, sticky="ew")
        
        # Botón de crear cuenta (azul)
        create_account_button = ttk.Button(main_frame, text="Crear Cuenta", command=self.create_account, style='Create.TButton')
        create_account_button.grid(row=3, column=0, columnspan=2, pady=5, padx=5, sticky="ew")
        
        # Configurar expansión de columna para que los widgets se expandan
        main_frame.grid_columnconfigure(1, weight=1)

    """
        Simula la autenticación. Aquí iría la lógica del backend.
    """
    def attempt_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        user_id = auth_manager.authenticate_user(username, password)
        if user_id:
            self.withdraw()
            # 📌 Pasa el user_id a la MainWindow
            main_window = MainWindow(self, user_id) 
            self.wait_window(main_window)
            self.deiconify()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos.")

    def create_account(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if not username or not password:
            messagebox.showwarning("Crear Cuenta", "Por favor, ingrese un nombre de usuario y contraseña.")
            return
        user_manager.create_user(username, password)
        