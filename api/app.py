# api/app.py
from fastapi import FastAPI, HTTPException, Query, Path
from pydantic import BaseModel
import bcrypt
from db import fetch_one, execute, get_conn  # <- importa get_conn
from typing import Optional

app = FastAPI(title="Microeventos API")

class UserIn(BaseModel):
    username: str
    password: str

class EventIn(BaseModel):
    name: str
    description: str | None = None
    event_date: str  # ISO 'YYYY-MM-DDTHH:MM:SS'
    category: str | None = None
    price: float = 0.0
    available_tickets: int = 0
    creator_id: int | None = None

@app.get("/health")
def health():
    row = fetch_one("SELECT 1 as ok;")
    return {"status": "ok", "db": bool(row and row["ok"] == 1)}

@app.post("/users")
def create_user(u: UserIn):
    pw_hash = bcrypt.hashpw(u.password.encode(), bcrypt.gensalt()).decode()
    try:
        execute("""
            INSERT INTO users (username, password_hash)
            VALUES (%s, %s)
            ON CONFLICT (username) DO NOTHING
        """, (u.username, pw_hash))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"created": True}

@app.post("/auth/login")
def login(u: UserIn):
    row = fetch_one("SELECT password_hash, role FROM users WHERE username=%s", (u.username,))
    if not row or not bcrypt.checkpw(u.password.encode(), row["password_hash"].encode()):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    return {"ok": True, "role": row.get("role", "organizer")}

# ---- ENDPOINTS DE EVENTOS ----

# 1) Resumen (debe ir ANTES que /events/{event_id})
@app.get("/events/summary")
def events_summary(creator_id: int | None = Query(default=None)):
    sql_all = """
        SELECT
            COUNT(*) AS total_events,
            COALESCE(SUM(available_tickets),0) AS total_available_tickets,
            COUNT(*) FILTER (WHERE available_tickets = 0) AS sold_out
        FROM events
    """
    with get_conn() as conn, conn.cursor() as cur:
        if creator_id is None:
            cur.execute(sql_all)
        else:
            cur.execute(sql_all + " WHERE creator_id = %s", (creator_id,))
        row = cur.fetchone()
        cols = [d[0] for d in cur.description]
        return dict(zip(cols, row))

# 2) Crear evento
@app.post("/events")
def create_event_api(e: EventIn):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            INSERT INTO events (name, description, event_date, category, price, available_tickets, creator_id)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (e.name, e.description, e.event_date, e.category, e.price, e.available_tickets, e.creator_id))
        conn.commit()
    return {"created": True}

# 3) Listar (con filtro opcional por creador)
@app.get("/events")
def list_events(creator_id: int | None = Query(default=None)):
    with get_conn() as conn, conn.cursor() as cur:
        if creator_id is None:
            cur.execute("""
                SELECT id, name, description, event_date, category, price, available_tickets, creator_id
                FROM events ORDER BY event_date DESC
            """)
        else:
            cur.execute("""
                SELECT id, name, description, event_date, category, price, available_tickets, creator_id
                FROM events WHERE creator_id=%s ORDER BY event_date DESC
            """, (creator_id,))
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]

# 4) Detalle (después de /events/summary)
@app.get("/events/{event_id}")
def get_event(event_id: int = Path(..., gt=0)):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT id, name, description, event_date, category, price, available_tickets, creator_id
            FROM events WHERE id=%s
        """, (event_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(404, "Not found")
        cols = [d[0] for d in cur.description]
        return dict(zip(cols, row))

# 5) Update
@app.put("/events/{event_id}")
def update_event_api(event_id: int, e: EventIn):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            UPDATE events
            SET name=%s, description=%s, event_date=%s, category=%s, price=%s, available_tickets=%s, creator_id=%s
            WHERE id=%s
        """, (e.name, e.description, e.event_date, e.category, e.price, e.available_tickets, e.creator_id, event_id))
        conn.commit()
    return {"updated": True, "id": event_id}

# 6) Delete (valida opcionalmente ownership)
@app.delete("/events/{event_id}")
def delete_event_api(event_id: int, user_id: int | None = Query(default=None)):
    with get_conn() as conn, conn.cursor() as cur:
        if user_id is None:
            cur.execute("DELETE FROM events WHERE id=%s", (event_id,))
        else:
            cur.execute("DELETE FROM events WHERE id=%s AND creator_id=%s", (event_id, user_id))
        conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(404, "Not found or not owner")
    return {"deleted": True, "id": event_id}

# ---- TICKETS & ATTENDANCE ----
from typing import Optional, List
from fastapi import Body

class TicketIn(BaseModel):
    event_id: int
    buyer_name: str
    buyer_email: Optional[str] = None
    price: Optional[float] = None  # si None, tomamos price del evento

@app.get("/tickets")
def list_tickets(event_id: int | None = Query(default=None)):
    with get_conn() as conn, conn.cursor() as cur:
        if event_id is None:
            cur.execute("""
                SELECT id, event_id, buyer_name, buyer_email, price, sold_at
                FROM tickets
                ORDER BY sold_at DESC
            """)
        else:
            cur.execute("""
                SELECT id, event_id, buyer_name, buyer_email, price, sold_at
                FROM tickets
                WHERE event_id=%s
                ORDER BY sold_at DESC
            """, (event_id,))
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]

@app.get("/tickets/{ticket_id}")
def get_ticket(ticket_id: int = Path(..., gt=0)):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT id, event_id, buyer_name, buyer_email, price, sold_at
            FROM tickets WHERE id=%s
        """, (ticket_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(404, "Not found")
        cols = [d[0] for d in cur.description]
        return dict(zip(cols, row))

@app.post("/tickets")
def sell_ticket_api(t: TicketIn):
    # (opcional si aplicaste el punto 2) valida email si viene
    # import re arriba del archivo y define EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    # if t.buyer_email and not EMAIL_RE.match(t.buyer_email):
    #     raise HTTPException(status_code=400, detail="Email inválido")

    with get_conn() as conn, conn.cursor() as cur:
        # 0) precio por defecto del evento si no viene
        price = t.price
        if price is None:
            cur.execute("SELECT price FROM events WHERE id=%s", (t.event_id,))
            row = cur.fetchone()
            if not row:
                raise HTTPException(404, "Evento no existe")
            price = float(row[0] or 0.0)

        # 1) DESCONTAR UN CUPO SOLO SI HAY (atómico) y guardar el RESTANTE
        cur.execute("""
            UPDATE events
               SET available_tickets = available_tickets - 1
             WHERE id = %s
               AND available_tickets > 0
            RETURNING available_tickets
        """, (t.event_id,))
        dec = cur.fetchone()
        if not dec:
            raise HTTPException(status_code=409, detail="Evento sin cupos disponibles")
        remaining = dec[0]  # 👈 cupos restantes después de descontar

        # 2) CREAR TICKET
        try:
            cur.execute("""
                INSERT INTO tickets (event_id, buyer_name, buyer_email, price)
                VALUES (%s, %s, %s, %s)
                RETURNING id, event_id, buyer_name, buyer_email, price, sold_at
            """, (t.event_id, t.buyer_name.strip(), (t.buyer_email or None), price))
            row = cur.fetchone()
            cols = [d[0] for d in cur.description]
            ticket = dict(zip(cols, row))
            ticket["remaining_available"] = remaining  # 👈 añadimos el remanente a la respuesta
            conn.commit()
            return ticket
        except Exception as e:
            # Si falla (p.ej. UNIQUE), se repone el cupo y se informa
            conn.rollback()
            with get_conn() as conn2, conn2.cursor() as cur2:
                cur2.execute("UPDATE events SET available_tickets = available_tickets + 1 WHERE id=%s", (t.event_id,))
                conn2.commit()
            raise HTTPException(status_code=409, detail=f"No se pudo crear el ticket: {e}")


@app.delete("/tickets/{ticket_id}")
def delete_or_refund_ticket(ticket_id: int, refund: int | None = Query(default=None)):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT event_id FROM tickets WHERE id=%s", (ticket_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(404, "Ticket no existe")
        event_id = row[0]

        cur.execute("DELETE FROM attendance WHERE ticket_id=%s", (ticket_id,))
        cur.execute("DELETE FROM tickets WHERE id=%s", (ticket_id,))
        if cur.rowcount == 0:
            conn.rollback()
            raise HTTPException(404, "Ticket no existe (concurrencia)")

        remaining = None
        if refund:
            cur.execute("""
                UPDATE events
                   SET available_tickets = available_tickets + 1
                 WHERE id=%s
                RETURNING available_tickets
            """, (event_id,))
            r = cur.fetchone()
            remaining = r[0] if r else None

        conn.commit()
    return {"deleted": True, "refunded": bool(refund), "remaining_available": remaining}


# ---- Attendance (check-in) ----

class AttendanceIn(BaseModel):
    ticket_id: int

@app.post("/attendance")
def create_attendance(a: AttendanceIn):
    with get_conn() as conn, conn.cursor() as cur:
        # validar ticket existe
        cur.execute("SELECT 1 FROM tickets WHERE id=%s", (a.ticket_id,))
        if not cur.fetchone():
            raise HTTPException(404, "Ticket no existe")
        # insertar (UNIQUE en ticket_id)
        try:
            cur.execute("""
                INSERT INTO attendance (ticket_id) VALUES (%s)
                RETURNING id, ticket_id, checked_in_at
            """, (a.ticket_id,))
        except Exception as e:
            conn.rollback()
            # probablemente UNIQUE violation
            raise HTTPException(status_code=409, detail="Este ticket ya tiene check-in")
        row = cur.fetchone()
        conn.commit()
        cols = [d[0] for d in cur.description]
        return dict(zip(cols, row))

@app.get("/attendance/{ticket_id}")
def get_attendance(ticket_id: int):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT id, ticket_id, checked_in_at
            FROM attendance WHERE ticket_id=%s
        """, (ticket_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(404, "No hay check-in para este ticket")
        cols = [d[0] for d in cur.description]
        return dict(zip(cols, row))

@app.delete("/attendance/{ticket_id}")
def delete_attendance(ticket_id: int):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM attendance WHERE ticket_id=%s", (ticket_id,))
        if cur.rowcount == 0:
            conn.rollback()
            raise HTTPException(404, "No había check-in para ese ticket")
        conn.commit()
        return {"deleted": True}

@app.get("/tickets")
def list_tickets(
    event_id: int | None = Query(default=None),
    buyer: str | None = Query(default=None, description="Nombre o email (ILIKE)"),
    date_from: str | None = Query(default=None, description="YYYY-MM-DD"),
    date_to: str | None = Query(default=None, description="YYYY-MM-DD (inclusive)"),
    checked: str = Query(default="all", description="yes|no|all")
):
    """
    Devuelve tickets con columna 'checked' (bool).
    Filtros opcionales: event_id, buyer (nombre o email, ILIKE),
    rango de fechas (sold_at) y estado de check-in.
    """
    with get_conn() as conn, conn.cursor() as cur:
        where = []
        params: list = []

        if event_id is not None:
            where.append("t.event_id = %s")
            params.append(int(event_id))

        if buyer:
            where.append("(t.buyer_name ILIKE %s OR t.buyer_email ILIKE %s)")
            like = f"%{buyer.strip()}%"
            params.extend([like, like])

        if date_from:
            where.append("t.sold_at >= %s::date")
            params.append(date_from)

        if date_to:
            # inclusivo: < date_to + 1 día
            where.append("t.sold_at < (%s::date + INTERVAL '1 day')")
            params.append(date_to)

        if checked in ("yes", "no"):
            where.append(("a.id IS NOT NULL") if checked == "yes" else "a.id IS NULL")

        sql = """
            SELECT
                t.id, t.event_id, t.buyer_name, t.buyer_email, t.price, t.sold_at,
                (a.id IS NOT NULL) AS checked
            FROM tickets t
            LEFT JOIN attendance a ON a.ticket_id = t.id
        """
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY t.sold_at DESC"

        cur.execute(sql, params)
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]