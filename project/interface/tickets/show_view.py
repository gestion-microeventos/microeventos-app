# project/interface/tickets/show_view.py
import tkinter as tk
from tkinter import ttk

def show_view(view_name: str,
              events_frame: ttk.Frame,
              tickets_frame: ttk.Frame) -> None:
    """
    Muestra una vista y oculta la otra.
    view_name: "events" | "tickets"
    """
    # Ocultar ambas
    for f in (events_frame, tickets_frame):
        try:
            f.pack_forget()
        except Exception:
            pass

    if view_name == "events":
        events_frame.pack(fill=tk.BOTH, expand=True)
    elif view_name == "tickets":
        tickets_frame.pack(fill=tk.BOTH, expand=True)
    else:
        raise ValueError(f"Vista desconocida: {view_name}")
