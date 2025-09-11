# project/services/ticket_manager.py
import os
import re
import requests
from tkinter import messagebox
from datetime import datetime
from decimal import Decimal, InvalidOperation
from dotenv import load_dotenv

# Intentamos reutilizar el event_manager para validar stock / precio por defecto
try:
    from .event_manager import get_event_by_id
except Exception:
    get_event_by_id = None

load_dotenv()
API_BASE = os.getenv("API_BASE", "http://localhost:8000").rstrip("/")

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


# ----------------- Helpers -----------------
def _validate_sale_data(data: dict) -> bool:
    """
    Requisitos mínimos para vender un ticket.
    Campos esperados: event_id, buyer_name, buyer_email (opcional), price (opcional)
    """
    if not data.get("event_id"):
        messagebox.showerror("Error", "Falta event_id.")
        return False
    if not (data.get("buyer_name") and str(data["buyer_name"]).strip()):
        messagebox.showerror("Error", "El nombre del comprador es requerido.")
        return False
    email = (data.get("buyer_email") or "").strip()
    if email and not EMAIL_RE.match(email):
        messagebox.showerror("Error", "El email del comprador no es válido.")
        return False
    # price es opcional; si viene, debe ser numérico positivo
    if data.get("price") not in (None, ""):
        try:
            p = Decimal(str(data["price"]))
            if p < 0:
                messagebox.showerror("Error", "El precio no puede ser negativo.")
                return False
        except InvalidOperation:
            messagebox.showerror("Error", "Formato de precio no válido.")
            return False
    return True


def _filter_client_side(tickets: list[dict], search_term: str) -> list[dict]:
    """
    Búsqueda local simple en buyer_name, buyer_email, price, sold_at, event_id, id.
    """
    if not search_term:
        return tickets

    st = str(search_term).strip().lower()
    if not st:
        return tickets

    out = []
    for t in tickets:
        blob = " ".join([
            str(t.get("id", "")),
            str(t.get("event_id", "")),
            str(t.get("buyer_name", "")),
            str(t.get("buyer_email", "")),
            str(t.get("price", "")),
            str(t.get("sold_at", "")),
        ]).lower()
        if st in blob:
            out.append(t)
    return out


def _coerce_price_or_default(event_id: int, price) -> float:
    """
    Si price viene vacío/None, intenta usar el precio del evento como default.
    """
    if price not in (None, ""):
        return float(Decimal(str(price)))
    if get_event_by_id:
        try:
            ev = get_event_by_id(int(event_id))
            if ev and ev.get("price") is not None:
                return float(Decimal(str(ev["price"])))
        except Exception:
            pass
    # Default a 0 si no hay info
    return 0.0


# ----------------- API Calls: Tickets -----------------
def sell_ticket(ticket_data: dict) -> dict | None:
    """
    Vende un ticket (POST /tickets).
    ticket_data requiere: event_id, buyer_name
    opcionales: buyer_email, price
    Devuelve el ticket creado o None.
    """
    if not _validate_sale_data(ticket_data):
        return None

    payload = {
        "event_id": int(ticket_data["event_id"]),
        "buyer_name": str(ticket_data["buyer_name"]).strip(),
        "buyer_email": (ticket_data.get("buyer_email") or "").strip() or None,
        "price": _coerce_price_or_default(ticket_data["event_id"], ticket_data.get("price")),
    }

    # Validación amistosa de stock en cliente (la API igual debe validar)
    if get_event_by_id:
        ev = get_event_by_id(payload["event_id"])
        if ev and isinstance(ev.get("available_tickets"), int) and ev["available_tickets"] <= 0:
            messagebox.showerror("Sin cupos", "El evento no tiene cupos disponibles.")
            return None

    try:
        r = requests.post(f"{API_BASE}/tickets", json=payload, timeout=10)
        if r.ok:
            return r.json()
        # Constrain UNIQUE(event_id, buyer_email, buyer_name)
        if r.status_code == 409:
            messagebox.showerror("Duplicado", "Ya existe un ticket para este comprador en este evento.")
            return None
        messagebox.showerror("Error API", f"{r.status_code}: {r.text}")
        return None
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo vender el ticket:\n{e}")
        return None



def sell_tickets_bulk(event_id: int, buyer_name: str, buyer_email: str | None, quantity: int, price=None) -> list[dict]:
    # ✅ valida email una vez
    email = (buyer_email or "").strip()
    if email and not is_valid_email(email):
        from tkinter import messagebox
        messagebox.showerror("Email inválido", "El email del comprador no es válido.")
        return []

    try:
        qty = int(quantity)
        if qty <= 0:
            from tkinter import messagebox
            messagebox.showerror("Error", "La cantidad debe ser mayor a 0.")
            return []
    except Exception:
        from tkinter import messagebox
        messagebox.showerror("Error", "Cantidad inválida.")
        return []

    created = []
    for i in range(qty):
        data = {
            "event_id": event_id,
            "buyer_name": buyer_name if qty == 1 else f"{buyer_name} #{i+1}",
            "buyer_email": email or None,
            "price": price,
        }
        t = sell_ticket(data)
        if t:
            created.append(t)
        else:
            # si falla un insert (sin cupos/duplicado), detenemos el loop para no spamear
            break
    return created


def list_tickets(event_id: int | None = None, search_term: str = "") -> list[dict]:
    """
    Lista tickets. Si event_id está presente: GET /tickets?event_id=...
    Si no: GET /tickets. Aplica búsqueda local si search_term viene.
    """
    try:
        if event_id is not None:
            r = requests.get(f"{API_BASE}/tickets", params={"event_id": int(event_id)}, timeout=10)
        else:
            r = requests.get(f"{API_BASE}/tickets", timeout=10)

        if r.ok:
            data = r.json() or []
            return _filter_client_side(data, search_term)
        messagebox.showerror("Error API", f"{r.status_code}: {r.text}")
        return []
    except Exception as e:
        print(f"Error al listar tickets: {e}")
        return []
    
# --- nuevo: listar con filtros ---
def list_tickets_filtered(
    event_id: int | None = None,
    buyer: str | None = None,
    date_from: str | None = None,  # "YYYY-MM-DD"
    date_to: str | None = None,    # "YYYY-MM-DD"
    checked: str = "all"           # "yes" | "no" | "all"
) -> list[dict]:
    try:
        params = {}
        if event_id is not None: params["event_id"] = int(event_id)
        if buyer: params["buyer"] = buyer
        if date_from: params["date_from"] = date_from
        if date_to: params["date_to"] = date_to
        if checked in ("yes","no","all"): params["checked"] = checked

        r = requests.get(f"{API_BASE}/tickets", params=params, timeout=10)
        if r.ok:
            return r.json() or []
        messagebox.showerror("Error API", f"{r.status_code}: {r.text}")
        return []
    except Exception as e:
        print("list_tickets_filtered:", e)
        return []



def get_ticket(ticket_id: int) -> dict | None:
    """
    Detalle de ticket por id (GET /tickets/{id}).
    """
    try:
        r = requests.get(f"{API_BASE}/tickets/{int(ticket_id)}", timeout=10)
        if r.ok:
            return r.json()
        if r.status_code == 404:
            return None
        messagebox.showerror("Error API", f"{r.status_code}: {r.text}")
        return None
    except Exception as e:
        print(f"Error al obtener ticket {ticket_id}: {e}")
        return None


def refund_ticket(ticket_id: int, actor_user_id: int | None = None) -> bool:
    """
    Devolución (refund). Opciones comunes de backend:
    - POST /tickets/{id}/refund
    - DELETE /tickets/{id}?refund=1
    - POST /refunds con ticket_id
    Aquí intentamos primero la convención REST 'POST /tickets/{id}/refund',
    y si da 404/405, probamos DELETE con query param.
    """
    # Opción 1: POST /tickets/{id}/refund
    try:
        payload = {"actor_user_id": actor_user_id} if actor_user_id is not None else None
        r = requests.post(f"{API_BASE}/tickets/{int(ticket_id)}/refund", json=payload, timeout=10)
        if r.ok:
            messagebox.showinfo("Éxito", "Devolución realizada.")
            return True
        if r.status_code not in (404, 405):
            messagebox.showerror("Error API", f"{r.status_code}: {r.text}")
            return False
    except Exception:
        # seguimos a fallback
        pass

    # Opción 2 (fallback): DELETE /tickets/{id}?refund=1
    try:
        params = {"refund": 1}
        if actor_user_id is not None:
            params["actor_user_id"] = int(actor_user_id)
        r = requests.delete(f"{API_BASE}/tickets/{int(ticket_id)}", params=params, timeout=10)
        if r.ok:
            messagebox.showinfo("Éxito", "Devolución realizada.")
            return True
        if r.status_code == 404:
            messagebox.showwarning("Aviso", "El ticket no existe.")
            return False
        messagebox.showerror("Error API", f"{r.status_code}: {r.text}")
        return False
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo procesar la devolución:\n{e}")
        return False


# ----------------- API Calls: Attendance (Check-in) -----------------
def check_in(ticket_id: int) -> bool:
    """
    Registra asistencia (POST /attendance) con ticket_id.
    El esquema define attendance.ticket_id UNIQUE, por lo que segunda pasada debe fallar con 409.
    """
    try:
        r = requests.post(f"{API_BASE}/attendance", json={"ticket_id": int(ticket_id)}, timeout=10)
        if r.ok:
            messagebox.showinfo("Éxito", "Check-in registrado.")
            return True
        if r.status_code == 409:
            messagebox.showwarning("Aviso", "Este ticket ya fue usado para check-in.")
            return False
        if r.status_code == 404:
            messagebox.showwarning("Aviso", "Ticket no encontrado.")
            return False
        messagebox.showerror("Error API", f"{r.status_code}: {r.text}")
        return False
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo registrar el check-in:\n{e}")
        return False


def undo_check_in(ticket_id: int) -> bool:
    """
    Revierte asistencia. Opciones comunes:
    - DELETE /attendance/{ticket_id}
    - DELETE /attendance?ticket_id=...
    """
    # Opción 1: path param
    try:
        r = requests.delete(f"{API_BASE}/attendance/{int(ticket_id)}", timeout=10)
        if r.ok:
            messagebox.showinfo("Éxito", "Check-in revertido.")
            return True
        if r.status_code not in (404, 405):
            messagebox.showerror("Error API", f"{r.status_code}: {r.text}")
            return False
    except Exception:
        pass

    # Opción 2: query param
    try:
        r = requests.delete(f"{API_BASE}/attendance", params={"ticket_id": int(ticket_id)}, timeout=10)
        if r.ok:
            messagebox.showinfo("Éxito", "Check-in revertido.")
            return True
        if r.status_code == 404:
            messagebox.showwarning("Aviso", "No había check-in para ese ticket.")
            return False
        messagebox.showerror("Error API", f"{r.status_code}: {r.text}")
        return False
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo revertir el check-in:\n{e}")
        return False


def get_attendance(ticket_id: int) -> dict | None:
    """
    Obtiene el registro de asistencia para un ticket.
    Rutas típicas: GET /attendance/{ticket_id} o GET /attendance?ticket_id=...
    """
    # Opción 1
    try:
        r = requests.get(f"{API_BASE}/attendance/{int(ticket_id)}", timeout=10)
        if r.ok:
            return r.json()
        if r.status_code not in (404, 405):
            messagebox.showerror("Error API", f"{r.status_code}: {r.text}")
            return None
    except Exception:
        pass

    # Opción 2
    try:
        r = requests.get(f"{API_BASE}/attendance", params={"ticket_id": int(ticket_id)}, timeout=10)
        if r.ok:
            data = r.json()
            # puede devolver [] o {} si no hay registro
            if not data:
                return None
            # normalizamos a dict
            if isinstance(data, list):
                return data[0] if data else None
            return data
        if r.status_code == 404:
            return None
        messagebox.showerror("Error API", f"{r.status_code}: {r.text}")
        return None
    except Exception as e:
        print(f"Error get_attendance ticket {ticket_id}:", e)
        return None


# ----------------- Resúmenes / Métricas -----------------
def get_sales_summary(event_id: int | None = None) -> dict:
    """
    Retorna agregados como:
      - total_tickets
      - total_amount
      - total_checked_in
      - available_tickets (del evento si event_id)
    Convenciones de rutas posibles:
      - GET /tickets/summary
      - GET /tickets/summary?event_id=...
    """
    try:
        params = {"event_id": int(event_id)} if event_id is not None else None
        r = requests.get(f"{API_BASE}/tickets/summary", params=params, timeout=10)
        if r.ok:
            return r.json() or {}
        # fallback si no existe la ruta
        if r.status_code in (404, 405):
            # Componemos un resumen básico client-side como último recurso
            tickets = list_tickets(event_id=event_id, search_term="")
            total_amount = sum(float(t.get("price") or 0) for t in tickets)
            # intentamos contar check-ins (si la API lo permite rápido evitaríamos N requests)
            checked = 0
            for t in tickets:
                att = get_attendance(t.get("id"))
                if att:
                    checked += 1
            summary = {
                "total_tickets": len(tickets),
                "total_amount": total_amount,
                "total_checked_in": checked,
            }
            if event_id is not None and get_event_by_id:
                ev = get_event_by_id(event_id)
                if ev:
                    summary["available_tickets"] = ev.get("available_tickets")
            return summary

        messagebox.showerror("Error API", f"{r.status_code}: {r.text}")
        return {}
    except Exception as e:
        print("Error get_sales_summary:", e)
        return {}

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def is_valid_email(value: str) -> bool:
    return bool(EMAIL_RE.match(value))