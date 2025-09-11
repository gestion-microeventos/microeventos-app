import tkinter as tk
from tkinter import ttk, messagebox

# project/interface/tickets -> project/services
from ...services import event_manager

# project/interface/tickets -> project/interface
from ..event_details import EventDetailsWindow
from ..new_event import NewEventWindow


def build_events_view(parent: ttk.Frame, controller) -> None:
    # ----- Paned principal -----
    main_pane = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
    main_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # ================== MIS EVENTOS ==================
    my_events_frame = ttk.Frame(main_pane, padding=10)
    main_pane.add(my_events_frame, weight=1)

    ttk.Label(my_events_frame, text="Mis Eventos", font=("Arial", 14, "bold")).pack(pady=5)

    # Filtros (Mis eventos)
    my_events_filter_frame = ttk.Frame(my_events_frame)
    my_events_filter_frame.pack(fill="x", pady=(0, 10))

    ttk.Label(my_events_filter_frame, text="Buscar:").pack(side="left", padx=(0, 5))
    controller.my_events_search_entry = ttk.Entry(my_events_filter_frame, width=30)
    controller.my_events_search_entry.pack(side="left", padx=5)
    ttk.Button(
        my_events_filter_frame, text="Filtrar",
        command=controller._apply_my_events_filter
    ).pack(side="left", padx=5)
    ttk.Button(
        my_events_filter_frame, text="Restablecer",
        command=controller._reset_my_events_filter
    ).pack(side="left", padx=5)

    # Tree Mis eventos
    controller.my_events_tree = ttk.Treeview(
        my_events_frame,
        columns=("Nombre", "Fecha", "Categoría", "Precio", "Cupos"),
        show="headings"
    )
    for col, w, anchor in [
        ("Nombre", 120, tk.W),
        ("Fecha", 120, tk.W),
        ("Categoría", 90, tk.W),
        ("Precio", 70, tk.CENTER),
        ("Cupos", 70, tk.CENTER),
    ]:
        controller.my_events_tree.heading(col, text=col)
        controller.my_events_tree.column(col, width=w, anchor=anchor)

    controller.my_events_tree.bind("<<TreeviewSelect>>", controller._on_event_select)
    controller.my_events_tree.pack(fill=tk.BOTH, expand=True)

    # ================== TODOS LOS EVENTOS ==================
    all_events_frame = ttk.Frame(main_pane, padding=10)
    main_pane.add(all_events_frame, weight=1)

    ttk.Label(all_events_frame, text="Todos los Eventos", font=("Arial", 14, "bold")).pack(pady=5)

    # Filtros (Todos)
    all_events_filter_frame = ttk.Frame(all_events_frame)
    all_events_filter_frame.pack(fill="x", pady=(0, 10))

    ttk.Label(all_events_filter_frame, text="Buscar:").pack(side="left", padx=(0, 5))
    controller.all_events_search_entry = ttk.Entry(all_events_filter_frame, width=30)
    controller.all_events_search_entry.pack(side="left", padx=5)
    ttk.Button(
        all_events_filter_frame, text="Filtrar",
        command=controller._apply_all_events_filter
    ).pack(side="left", padx=5)
    ttk.Button(
        all_events_filter_frame, text="Restablecer",
        command=controller._reset_all_events_filter
    ).pack(side="left", padx=5)

    # Tree Todos
    controller.all_events_tree = ttk.Treeview(
        all_events_frame,
        columns=("Nombre", "Fecha", "Categoría", "Precio", "Cupos"),
        show="headings"
    )
    for col, w, anchor in [
        ("Nombre", 120, tk.W),
        ("Fecha", 120, tk.W),
        ("Categoría", 90, tk.W),
        ("Precio", 70, tk.CENTER),
        ("Cupos", 70, tk.CENTER),
    ]:
        controller.all_events_tree.heading(col, text=col)
        controller.all_events_tree.column(col, width=w, anchor=anchor)

    controller.all_events_tree.bind("<<TreeviewSelect>>", controller._on_event_select)
    controller.all_events_tree.pack(fill=tk.BOTH, expand=True)

    # ================== Botonera inferior ==================
    button_frame = ttk.Frame(parent)
    button_frame.pack(side=tk.BOTTOM, pady=10)

    controller.create_event_button = ttk.Button(
        button_frame, text="Crear Evento",
        style="Blue.TButton", command=controller._create_event
    )
    controller.create_event_button.pack(side=tk.LEFT, padx=5)

    controller.logout_button = ttk.Button(
        button_frame, text="Cerrar Sesión",
        style="Red.TButton", command=controller.close_window
    )
    controller.logout_button.pack(side=tk.LEFT, padx=5)

    # ================== Cargas iniciales ==================
    controller._load_my_events()
    controller._load_all_events()
