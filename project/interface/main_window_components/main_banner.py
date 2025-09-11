import tkinter as tk
from tkinter import ttk

BANNER_BLUE = "#0d6efd"   # fondo del banner
BLUE_DARK   = "#0b5ed7"   # hover
WHITE       = "#ffffff"
BLACK       = "#000000"

class MainBanner(ttk.Frame):
    def __init__(self, master=None, on_switch=None, on_logout=None, **kwargs):
        super().__init__(master, **kwargs)
        self.on_switch = on_switch
        self.on_logout = on_logout
        self.current_view = "events"

        # ---- Estilos ----
        style = ttk.Style(self)
        style.configure("BlueBanner.TFrame", background=BANNER_BLUE)
        self.configure(style="BlueBanner.TFrame")

        style.configure("BannerTitle.TLabel",
                        background=BANNER_BLUE, foreground=WHITE,
                        font=("Arial", 16, "bold"))

        # Botones de navegación (píldora blanca, texto azul)
        style.configure("Nav.TButton",
                        background=WHITE, foreground=BANNER_BLUE,
                        font=("Arial", 11, "bold"),
                        padding=(12, 6), borderwidth=0)
        style.map("Nav.TButton",
                  background=[("active", WHITE)],
                  foreground=[("active", BLUE_DARK)])

        # Estado “seleccionado” (texto blanco sobre azul oscuro)
        style.configure("NavSelected.TButton",
                        background=BLUE_DARK, foreground=WHITE,
                        font=("Arial", 11, "bold"),
                        padding=(12, 6), borderwidth=0)
        style.map("NavSelected.TButton",
                  background=[("active", BLUE_DARK)],
                  foreground=[("active", WHITE)])

        # Botón cerrar sesión (blanco bordeado, texto azul)
        style.configure("Logout.TButton",
                        background=WHITE, foreground=BANNER_BLUE,
                        font=("Arial", 11, "bold"),
                        padding=(12, 6), borderwidth=2, relief="solid")
        style.map("Logout.TButton",
                  background=[("active", WHITE)],
                  foreground=[("active", BLUE_DARK)])

        # Layout
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=0)
        self.columnconfigure(3, weight=0)
        self._build()

    def _build(self):
        ttk.Label(self, text="Gestión de Eventos", style="BannerTitle.TLabel") \
            .grid(row=0, column=0, padx=(12, 8), pady=8, sticky="w")

        # Nav
        nav_frame = ttk.Frame(self, style="BlueBanner.TFrame")
        nav_frame.grid(row=0, column=1, padx=8, pady=8, sticky="w")

        self.btn_events = ttk.Button(
            nav_frame, text="Eventos",
            style="NavSelected.TButton",
            command=lambda: self._switch("events"))
        self.btn_events.pack(side=tk.LEFT, padx=(0, 6))

        self.btn_tickets = ttk.Button(
            nav_frame, text="Venta de Entradas",
            style="Nav.TButton",
            command=lambda: self._switch("tickets"))
        self.btn_tickets.pack(side=tk.LEFT, padx=(6, 0))

        # Spacer
        ttk.Frame(self, style="BlueBanner.TFrame") \
            .grid(row=0, column=2, sticky="nsew")

        # Logout
        logout_btn = ttk.Button(
            self, text="Cerrar Sesión",
            style="Logout.TButton",
            command=self._handle_logout
        )
        logout_btn.grid(row=0, column=3, padx=(6, 12), pady=8, sticky="e")

    def _handle_logout(self):
        if callable(self.on_logout):
            self.on_logout()

    def _switch(self, view: str):
        if view == self.current_view:
            return
        self.current_view = view
        # Actualiza estilos seleccionados
        if view == "events":
            self.btn_events.configure(style="NavSelected.TButton")
            self.btn_tickets.configure(style="Nav.TButton")
        else:
            self.btn_events.configure(style="Nav.TButton")
            self.btn_tickets.configure(style="NavSelected.TButton")

        if callable(self.on_switch):
            self.on_switch(view)
