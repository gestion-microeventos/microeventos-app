# build_tickets_view.py (fragmento de ejemplo)
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from project.services.event_manager import get_all_events
from project.services.ticket_manager import (
    sell_ticket, refund_ticket, check_in, list_tickets_filtered, sell_tickets_bulk
)
# (Si usas el EventPickerDialog del mismo archivo, no lo importes)

def build_tickets_view(parent: ttk.Frame, controller) -> None:
    wrap = ttk.Frame(parent, padding=20)
    wrap.pack(fill=tk.BOTH, expand=True)

    ttk.Label(wrap, text="Venta de Entradas", font=("Arial", 16, "bold")).pack(anchor="w", pady=(0, 10))

    # --- Estado ---
    selected_event_id = tk.IntVar(value=0)
    selected_event_label = tk.StringVar(value="(ninguno)")
    available_var = tk.IntVar(value=0)
 
    # ---------- FORM VENTA ----------
    form = ttk.Frame(wrap); form.pack(fill=tk.X, pady=8)

    # Evento
    ttk.Label(form, text="Evento").grid(row=0, column=0, sticky="w")
    e_event_display = ttk.Entry(form, textvariable=selected_event_label, state="readonly", width=40)
    e_event_display.grid(row=0, column=1, sticky="w", padx=(6, 6))

    def pick_event():
        dlg = EventPickerDialog(parent=wrap)
        if dlg.result:
            selected_event_id.set(dlg.result["id"])
            selected_event_label.set(f'{dlg.result["id"]} — {dlg.result["name"]}')
            if not e_price.get().strip():
                e_price.delete(0, tk.END)
                e_price.insert(0, str(dlg.result.get("price") or 0))

            # 👇 set inmediato + confirmación desde servidor
            available_var.set(int(dlg.result.get("available_tickets") or 0))
            try:
                e_qty.config(to=max(1, available_var.get()))
            except Exception:
                pass
            refresh_available_from_server()

            refresh()  # recarga la tabla de tickets del evento


    ttk.Button(form, text="Seleccionar…", command=pick_event).grid(row=0, column=2, padx=(0, 6))
    ttk.Label(form, text="Cupos disponibles:").grid(row=0, column=3, sticky="e")
    lbl_available = ttk.Label(form, textvariable=available_var, width=6)
    lbl_available.grid(row=0, column=4, sticky="w", padx=(6, 0))

    # Comprador
    ttk.Label(form, text="Nombre").grid(row=1, column=0, sticky="w", pady=(8,0))
    e_name = ttk.Entry(form, width=28); e_name.grid(row=1, column=1, sticky="w", padx=(6,6), pady=(8,0))

    ttk.Label(form, text="Email").grid(row=1, column=2, sticky="w", pady=(8,0))
    e_email = ttk.Entry(form, width=28); e_email.grid(row=1, column=3, sticky="w", padx=(6,6), pady=(8,0))

    ttk.Label(form, text="Precio").grid(row=1, column=4, sticky="w", pady=(8,0))
    e_price = ttk.Entry(form, width=12); e_price.grid(row=1, column=5, sticky="w", padx=(6,0), pady=(8,0))

    # Cantidad
    ttk.Label(form, text="Cantidad").grid(row=1, column=6, sticky="w", pady=(8,0))
    qty_var = tk.IntVar(value=1)
    e_qty = ttk.Spinbox(form, from_=1, to=1, textvariable=qty_var, width=6)
    e_qty.grid(row=1, column=7, sticky="w", padx=(6,0), pady=(8,0))

    # Acciones venta/devolución/check-in
    btns = ttk.Frame(wrap); btns.pack(fill=tk.X, pady=10)
    ttk.Label(btns, text="Ticket ID:").pack(side=tk.LEFT)
    e_ticket_id = ttk.Entry(btns, width=10); e_ticket_id.pack(side=tk.LEFT, padx=(4, 12))

    def do_sell():
        ev_id = selected_event_id.get()
        if ev_id <= 0:
            from tkinter import messagebox
            messagebox.showerror("Falta evento", "Debes seleccionar un evento.")
            return

        available_now = int(available_var.get() or 0)
        q = int(qty_var.get() or 1)

        if available_now <= 0:
            from tkinter import messagebox
            messagebox.showwarning("Agotado", "Este evento no tiene cupos disponibles.")
            return

        if q > available_now:
            from tkinter import messagebox
            messagebox.showerror("Cantidad inválida",
                                f"Solicitas {q}, pero solo quedan {available_now} cupo(s).")
            return

        payload = {
            "event_id": ev_id,
            "buyer_name": e_name.get(),
            "buyer_email": e_email.get(),
            "price": e_price.get()
        }

        ok = False
        if q <= 1:
            t = sell_ticket(payload)
            ok = bool(t)
        else:
            from project.services.ticket_manager import sell_tickets_bulk, is_valid_email
            email = e_email.get().strip()
            if email and not is_valid_email(email):
                from tkinter import messagebox
                messagebox.showerror("Email inválido", "El email del comprador no es válido.")
                return
            created = sell_tickets_bulk(ev_id, e_name.get(), email, q, e_price.get())
            ok = len(created) == q  # exige venta total

        if ok:
            e_name.delete(0, tk.END)
            e_email.delete(0, tk.END)
            refresh()
            try:
                controller._load_all_events()
                controller._load_summary()
            except Exception:
                pass
            # 👇 vuelve a traer cupos reales del server y ajusta el Spinbox
            refresh_available_from_server()
        else:
            # si hubo intentos parciales/falla, igual reconsulta los cupos
            refresh_available_from_server()



    def do_refund():
        tid = e_ticket_id.get().strip()
        if tid:
            from project.services.ticket_manager import refund_ticket
            if refund_ticket(int(tid)):
                refresh()
                try:
                    controller._load_all_events()
                    controller._load_summary()
                except Exception:
                    pass
                refresh_available_from_server()  # 👈 refleja +1 en pantalla



    def do_checkin():
        tid = e_ticket_id.get().strip()
        if tid:
            if check_in(int(tid)):
                refresh()

    def refresh_available_from_server():
        ev_id = selected_event_id.get()
        if ev_id > 0:
            ev = get_event_by_id(ev_id)
            if ev:
                available_var.set(int(ev.get("available_tickets") or 0))
                # opcional: limitar el Spinbox al máximo disponible (min 1)
                try:
                    e_qty.config(to=max(1, available_var.get()))
                except Exception:
                    pass

    def pick_event():
        dlg = EventPickerDialog(parent=wrap)
        if dlg.result:
            selected_event_id.set(dlg.result["id"])
            selected_event_label.set(f'{dlg.result["id"]} — {dlg.result["name"]}')
            if not e_price.get().strip():
                e_price.delete(0, tk.END)
                e_price.insert(0, str(dlg.result.get("price") or 0))
            refresh_available_from_server()   # 👈 carga y muestra cupos
            refresh()


    ttk.Button(btns, text="Vender", command=do_sell).pack(side=tk.LEFT, padx=(0,6))
    ttk.Button(btns, text="Devolver", command=do_refund).pack(side=tk.LEFT, padx=(0,6))
    ttk.Button(btns, text="Check-in", command=do_checkin).pack(side=tk.LEFT)

    # ---------- FILTROS LISTA ----------
    filters = ttk.LabelFrame(wrap, text="Filtros"); filters.pack(fill=tk.X, pady=(8,6))

    ttk.Label(filters, text="Comprador").grid(row=0, column=0, sticky="w", padx=6, pady=6)
    f_buyer = ttk.Entry(filters, width=24); f_buyer.grid(row=0, column=1, sticky="w")

    ttk.Label(filters, text="Desde (YYYY-MM-DD)").grid(row=0, column=2, sticky="w", padx=6)
    f_from = ttk.Entry(filters, width=12); f_from.grid(row=0, column=3, sticky="w")

    ttk.Label(filters, text="Hasta (YYYY-MM-DD)").grid(row=0, column=4, sticky="w", padx=6)
    f_to = ttk.Entry(filters, width=12); f_to.grid(row=0, column=5, sticky="w")

    ttk.Label(filters, text="Check-in").grid(row=0, column=6, sticky="w", padx=6)
    f_checked = ttk.Combobox(filters, values=["Todos","Checkeados","No checkeados"], state="readonly", width=15)
    f_checked.current(0)
    f_checked.grid(row=0, column=7, sticky="w")

    def apply_filters():
        refresh()
    ttk.Button(filters, text="Aplicar", command=apply_filters).grid(row=0, column=8, padx=8)

    # ---------- TABLA ----------
    table = ttk.Treeview(wrap,
        columns=("id","event","name","email","price","sold_at","checked"),
        show="headings", height=12)
    for c, txt, w, anc in [
        ("id","ID",60,"w"),
        ("event","Evento",70,"w"),
        ("name","Comprador",180,"w"),
        ("email","Email",200,"w"),
        ("price","Precio",80,"e"),
        ("sold_at","Fecha venta",160,"w"),
        ("checked","Check-in",90,"center"),
    ]:
        table.heading(c, text=txt)
        table.column(c, width=w, anchor=anc)
    table.pack(fill=tk.BOTH, expand=True, pady=(6,0))

    def on_row_dclick(_):
        sel = table.selection()
        if not sel: return
        vals = table.item(sel[0], "values")
        e_ticket_id.delete(0, tk.END); e_ticket_id.insert(0, vals[0])
    table.bind("<Double-1>", on_row_dclick)

    # ---------- Refresh ----------
    def refresh():
        for i in table.get_children():
            table.delete(i)

        ev_id = selected_event_id.get() or None
        buyer = f_buyer.get().strip() or None
        date_from = f_from.get().strip() or None
        date_to = f_to.get().strip() or None
        checked_map = {"Todos":"all", "Checkeados":"yes", "No checkeados":"no"}
        checked = checked_map.get(f_checked.get(), "all")

        rows = list_tickets_filtered(
            event_id=ev_id,
            buyer=buyer,
            date_from=date_from,
            date_to=date_to,
            checked=checked
        )
        for t in rows:
            table.insert("", tk.END, values=(
                t.get("id"), t.get("event_id"), t.get("buyer_name"),
                t.get("buyer_email"), t.get("price"), t.get("sold_at"),
                "Sí" if t.get("checked") else "No"
            ))

    refresh()
    controller._load_all_events()
    controller._load_summary()
        
class EventPickerDialog(tk.Toplevel):
    """
    Diálogo modal para seleccionar un evento.
    Retorna el dict del evento seleccionado en self.result (o None si cancel).
    """
    def __init__(self, parent, title="Seleccionar evento"):
        super().__init__(parent)
        self.title(title)
        self.transient(parent)
        self.resizable(True, True)
        self.result = None

        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        # --- Búsqueda ---
        bar = ttk.Frame(self, padding=(12, 10))
        bar.grid(row=0, column=0, sticky="ew")
        bar.columnconfigure(1, weight=1)

        ttk.Label(bar, text="Buscar:").grid(row=0, column=0, sticky="w")
        self.e_search = ttk.Entry(bar)
        self.e_search.grid(row=0, column=1, sticky="ew", padx=(6, 6))
        ttk.Button(bar, text="Buscar", command=self._reload).grid(row=0, column=2)

        # --- Tabla ---
        self.table = ttk.Treeview(self, columns=("id","name","event_date","category","price","available"), show="headings")
        for c, txt, w, anchor in [
            ("id", "ID", 60, "w"),
            ("name", "Nombre", 220, "w"),
            ("event_date", "Fecha", 160, "w"),
            ("category", "Categoría", 120, "w"),
            ("price", "Precio", 80, "e"),
            ("available", "Cupos", 70, "e"),
        ]:
            self.table.heading(c, text=txt)
            self.table.column(c, width=w, anchor=anchor)
        self.table.grid(row=2, column=0, sticky="nsew", padx=12, pady=(0, 8))

        # Scroll
        vs = ttk.Scrollbar(self, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=vs.set)
        vs.grid(row=2, column=1, sticky="ns", pady=(0, 8))

        # --- Botones ---
        btns = ttk.Frame(self, padding=(12, 0, 12, 12))
        btns.grid(row=3, column=0, columnspan=2, sticky="ew")
        btns.columnconfigure(0, weight=1)
        ttk.Button(btns, text="Cancelar", command=self._cancel).pack(side=tk.RIGHT, padx=(6, 0))
        ttk.Button(btns, text="Seleccionar", command=self._select).pack(side=tk.RIGHT)

        # Eventos
        self.table.bind("<Double-1>", lambda e: self._select())
        self.e_search.bind("<Return>", lambda e: self._reload())

        # Cargar
        self._reload()

        # Modal
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._cancel)
        self.e_search.focus_set()
        self.wait_window(self)

    def _reload(self):
        term = self.e_search.get().strip()
        # Usa la búsqueda local del manager (ya implementada)
        events = get_all_events(search_term=term)

        # Limpiar
        for i in self.table.get_children():
            self.table.delete(i)

        # Insertar
        for ev in events:
            date_txt = self._fmt_date(ev.get("event_date"))
            available = int(ev.get("available_tickets") or 0)
            row_tags = ("soldout",) if available <= 0 else ()
            self.table.insert(
                "", tk.END,
                values=(
                    ev.get("id"),
                    ev.get("name"),
                    date_txt,
                    ev.get("category"),
                    ev.get("price"),
                    available,
                ),
                tags=row_tags  # 👈 aplica el tag
            )


    def _select(self):
        sel = self.table.selection()
        if not sel:
            return
        vals = self.table.item(sel[0], "values")
        available = int(vals[5]) if vals[5] not in (None, "",) else 0

        self.result = {
            "id": int(vals[0]),
            "name": vals[1],
            "event_date": vals[2],
            "category": vals[3],
            "price": float(vals[4]) if vals[4] not in (None, "",) else 0.0,
            "available_tickets": available,
        }
        self.destroy()


    def _cancel(self):
        self.result = None
        self.destroy()

    def refresh_available_from_server():
        ev_id = selected_event_id.get()
        if ev_id > 0:
            ev = get_event_by_id(ev_id)  # GET /events/{id}
            if ev:
                available = int(ev.get("available_tickets") or 0)
                available_var.set(available)
                try:
                    # limita el Spinbox a lo que hay (mínimo 1 para evitar to=0)
                    e_qty.config(to=max(1, available))
                except Exception:
                    pass


    @staticmethod
    def _fmt_date(iso_str: str | None) -> str:
        if not iso_str:
            return ""
        # Admite 'YYYY-MM-DDTHH:MM:SS' o 'YYYY-MM-DD HH:MM:SS'
        s = iso_str.replace("T", " ")
        try:
            dt = datetime.strptime(s[:19], "%Y-%m-%d %H:%M:%S")
            return dt.strftime("%Y-%m-%d %H:%M")
        except Exception:
            return iso_str