# project/interface/main_banner.py
import tkinter as tk
from tkinter import ttk

BANNER_BLUE = "#0d6efd"    # azul del banner
BLUE_DARK   = "#0b5ed7"    # azul activo/hover
WHITE       = "#ffffff"

class MainBanner(ttk.Frame):
    """
    Banner superior azul con botón 'Cerrar Sesión' en contraste (blanco con texto azul).
    on_logout: callback a ejecutar al hacer clic (ej. MainWindow.close_window).
    """
    def __init__(self, master=None, on_logout=None, **kwargs):
        super().__init__(master, **kwargs)

        self.on_logout = on_logout

        # ---- Estilos ----
        style = ttk.Style(self)

        # Frame del banner: fondo azul
        style.configure("BlueBanner.TFrame", background=BANNER_BLUE)
        self.configure(style="BlueBanner.TFrame")

        style.configure(
            "BannerTitle.TLabel",
            background=BANNER_BLUE,
            foreground=WHITE,
            font=("Arial", 16, "bold")
        )

        style.configure(
            "Logout.TButton",
            background=BANNER_BLUE,
            foreground=BANNER_BLUE,
            font=("Arial", 11, "bold"),
            borderwidth=2,
            relief="solid",
            padding=(10, 6)
        )
        style.map(
            "Logout.TButton",
            background=[("active", BANNER_BLUE)],
            foreground=[("active", BLUE_DARK)]
        )

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=0)

        # Título
        ttk.Label(self, text="Gestión de Eventos", style="BannerTitle.TLabel") \
            .grid(row=0, column=0, padx=(12, 6), pady=8, sticky="w")

        # Spacer
        ttk.Frame(self, style="BlueBanner.TFrame") \
            .grid(row=0, column=1, sticky="nsew")

        # Botón de cerrar sesión (contraste)
        logout_btn = ttk.Button(
            self,
            text="Cerrar Sesión",
            style="Logout.TButton",
            command=self._handle_logout
        )
        logout_btn.grid(row=0, column=2, padx=(6, 12), pady=8, sticky="e")

    def _handle_logout(self):
        if callable(self.on_logout):
            self.on_logout()
