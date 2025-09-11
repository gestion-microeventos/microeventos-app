# api/app.py
from fastapi import FastAPI, HTTPException, Query, Path
from pydantic import BaseModel
import bcrypt
from db import fetch_one, execute, get_conn  # <- importa get_conn

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
