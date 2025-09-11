# project/services/event_manager.py
import os
import requests
from tkinter import messagebox
from datetime import datetime
from decimal import Decimal
from dotenv import load_dotenv

load_dotenv()
API_BASE = os.getenv("API_BASE", "http://localhost:8000").rstrip("/")


# ----------------- Helpers -----------------
def _to_iso_datetime(datestr: str) -> str | None:
    """
    Convierte una fecha de entrada ('YYYY-MM-DD', 'YYYY/MM/DD' o 'DD/MM/YYYY')
    a ISO 'YYYY-MM-DDTHH:MM:SS' (hora fija 09:00 para evitar tz).
    """
    if not datestr:
        return None

    # Formatos que pueden venir desde la UI
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y"):
        try:
            dt = datetime.strptime(datestr, fmt)
            return dt.strftime("%Y-%m-%dT09:00:00")
        except ValueError:
            pass
    return None


def _validate_event_data(data: dict) -> bool:
    required = ['name', 'description', 'date', 'category', 'price', 'tickets', 'creator_id']
    for f in required:
        if data.get(f) in (None, "", []):
            messagebox.showerror("Error", f"El campo '{f}' es requerido.")
            return False
    return True


def _filter_client_side(events: list[dict], search_term: str) -> list[dict]:
    """
    Filtro de búsqueda local (cliente) si la API no soporta búsqueda.
    Busca en: name, description, event_date, category, price, available_tickets.
    """
    if not search_term:
        return events

    st = str(search_term).strip().lower()
    if not st:
        return events

    out = []
    for e in events:
        # Construye un blob de texto simple con campos clave
        blob = " ".join([
            str(e.get("name", "")),
            str(e.get("description", "")),
            str(e.get("event_date", "")),
            str(e.get("category", "")),
            str(e.get("price", "")),
            str(e.get("available_tickets", "")),
        ]).lower()

        if st in blob:
            out.append(e)
    return out


# ----------------- API Calls -----------------
def create_event(event_data: dict) -> bool:
    """
    Crea un evento vía API (POST /events).
    """
    if not _validate_event_data(event_data):
        return False

    # Validaciones / conversiones de tipos
    try:
        price = Decimal(event_data['price'])
        tickets = int(event_data['tickets'])
    except Exception:
        messagebox.showerror("Error", "Los datos de precio o cupos no tienen el formato correcto.")
        return False

    iso = _to_iso_datetime(event_data.get("date", ""))
    if not iso:
        messagebox.showerror("Error", f"Formato de fecha no reconocido: {event_data.get('date')}")
        return False

    payload = {
        "name": (event_data.get("name") or "").strip(),
        "description": (event_data.get("description") or "").strip() or None,
        "event_date": iso,
        "category": (event_data.get("category") or "").strip() or None,
        "price": float(price),
        "available_tickets": tickets,
        "creator_id": int(event_data.get("creator_id")),
    }

    try:
        r = requests.post(f"{API_BASE}/events", json=payload, timeout=10)
        if r.ok:
            messagebox.showinfo("Éxito", "Evento guardado exitosamente.")
            return True
        messagebox.showerror("Error API", f"{r.status_code}: {r.text}")
        return False
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo crear el evento:\n{e}")
        return False


def get_all_events(search_term: str = "") -> list[dict]:
    """
    Obtiene todos los eventos (GET /events) y aplica búsqueda local si se indica.
    """
    try:
        r = requests.get(f"{API_BASE}/events", timeout=10)
        if r.ok:
            data = r.json() or []
            return _filter_client_side(data, search_term)
        messagebox.showerror("Error API", f"{r.status_code}: {r.text}")
        return []
    except Exception as e:
        print(f"Error al obtener eventos: {e}")
        return []


def get_events_by_creator(creator_id: int, search_term: str = "") -> list[dict]:
    """
    Obtiene eventos por creador (GET /events?creator_id=...) y aplica búsqueda local.
    """
    try:
        r = requests.get(f"{API_BASE}/events", params={"creator_id": creator_id}, timeout=10)
        # Si la API no soporta el parámetro (422), traemos todos y filtramos client-side
        if r.status_code == 422:
            all_ev = get_all_events(search_term="")
            subset = [e for e in all_ev if str(e.get("creator_id")) == str(creator_id)]
            return _filter_client_side(subset, search_term)

        if r.ok:
            data = r.json() or []
            return _filter_client_side(data, search_term)

        messagebox.showerror("Error API", f"{r.status_code}: {r.text}")
        return []
    except Exception as e:
        print(f"Error al obtener eventos del creador: {e}")
        return []


def get_event_by_id(event_id: int) -> dict | None:
    """
    Detalle de un evento (GET /events/{id})
    """
    try:
        r = requests.get(f"{API_BASE}/events/{int(event_id)}", timeout=10)
        if r.ok:
            return r.json()
        if r.status_code == 404:
            return None
        messagebox.showerror("Error API", f"{r.status_code}: {r.text}")
        return None
    except Exception as e:
        print(f"Error al obtener el evento {event_id}: {e}")
        return None


def delete_event(event_id: int, user_id: int) -> bool:
    """
    Elimina un evento (DELETE /events/{id}?user_id=...).
    """
    try:
        r = requests.delete(f"{API_BASE}/events/{int(event_id)}", params={"user_id": int(user_id)}, timeout=10)
        if r.ok:
            return True
        if r.status_code == 404:
            messagebox.showwarning("Aviso", "El evento no existe o no eres el propietario.")
            return False
        messagebox.showerror("Error API", f"{r.status_code}: {r.text}")
        return False
    except Exception as e:
        print(f"Error al eliminar el evento {event_id}: {e}")
        return False


def update_event(event_data: dict) -> bool:
    """
    Actualiza un evento (PUT /events/{id}).
    Requiere: id, name, date, price, tickets, creator_id.
    """
    if not event_data.get("id"):
        messagebox.showerror("Error", "Falta el ID del evento a actualizar.")
        return False

    # Validaciones / conversiones
    try:
        price = Decimal(event_data['price'])
        tickets = int(event_data['tickets'])
    except Exception:
        messagebox.showerror("Error de Formato", "Precio y cupos deben ser números válidos.")
        return False

    iso = _to_iso_datetime(event_data.get("date", ""))
    if not iso:
        messagebox.showerror("Error", f"Formato de fecha no reconocido: {event_data.get('date')}")
        return False

    payload = {
        "name": (event_data.get("name") or "").strip(),
        "description": (event_data.get("description") or "").strip() or None,
        "event_date": iso,
        "category": (event_data.get("category") or "").strip() or None,
        "price": float(price),
        "available_tickets": tickets,
        "creator_id": int(event_data.get("creator_id")),
    }

    try:
        r = requests.put(f"{API_BASE}/events/{int(event_data['id'])}", json=payload, timeout=10)
        if r.ok:
            messagebox.showinfo("Éxito", "Evento actualizado exitosamente.")
            return True
        messagebox.showerror("Error API", f"{r.status_code}: {r.text}")
        return False
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo actualizar el evento:\n{e}")
        return False


def get_summary(creator_id: int | None = None) -> dict:
    """
    Resumen de eventos (GET /events/summary o /events/summary?creator_id=...).
    Retorna dict con: total_events, total_available_tickets, sold_out
    """
    try:
        params = {"creator_id": creator_id} if creator_id is not None else None
        r = requests.get(f"{API_BASE}/events/summary", params=params, timeout=10)
        if r.ok:
            return r.json() or {}
        # Si choca con /events/{id} (orden de rutas), cambia el path en API a /events-summary o reordena rutas.
        messagebox.showerror("Error API", f"{r.status_code}: {r.text}")
        return {"total_events": 0, "total_available_tickets": 0, "sold_out": 0}
    except Exception as e:
        print("Error get_summary:", e)
        return {"total_events": 0, "total_available_tickets": 0, "sold_out": 0}
