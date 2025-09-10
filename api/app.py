from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import bcrypt
from db import fetch_one, execute

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
    # hash igual que tu app Tkinter
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
    if not row:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    if not bcrypt.checkpw(u.password.encode(), row["password_hash"].encode()):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    return {"ok": True, "role": row.get("role", "organizer")}

@app.post("/events")
def create_event(e: EventIn):
    execute("""
        INSERT INTO events (name, description, event_date, category, price, available_tickets, creator_id)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """, (e.name, e.description, e.event_date, e.category, e.price, e.available_tickets, e.creator_id))
    return {"created": True}

@app.get("/events")
def list_events():
    # ejemplo simple (sin paginación)
    # reutilizamos fetch_one/execute; añadimos fetch_all rápido aquí:
    from db import get_conn
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, event_date, category, price, available_tickets FROM events ORDER BY event_date DESC")
            cols = [d[0] for d in cur.description]
            rows = [dict(zip(cols, r)) for r in cur.fetchall()]
            return rows
