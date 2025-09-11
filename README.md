# Gestión de Entradas para Micro-Eventos

Equipo: [Benjamín Daza] · [Carlos Mundaca]

## Índice

- [Gestión de Entradas para Micro-Eventos](#gestión-de-entradas-para-micro-eventos)
  - [Descripción](#descripción)
  - [Tecnologías (Tkinter)](#tecnologías-tkinter)
    - [Instalación y ejecución](#instalación-y-ejecución)
    - [Frontend](#frontend)
    - [Backend (Python)](#backend-python)
    - [Base de Datos (PostgreSQL)](#base-de-datos-postgresql)
    - [API (FastAPI)](#api-fastapi)
      - [Autenticación](#autenticación)
      - [Eventos](#eventos)
      - [Lógica (transacción)](#lógica-transacción)
      - [Attendance (check-in)](#attendance-check-in)
  - [Estructura del repositorio](#estructura-del-repositorio)
  - [Funcionalidades principales](#funcionalidades-principales)
  - [Contribución](#contribución)
  - [Respuestas a las preguntas propuestas](#respuestas-a-las-preguntas-propuestas)
    - [¿Cómo especificamos mejor el requerimiento?](#cómo-especificamos-mejor-el-requerimiento)
      - [Se define un alcance y objetivo general](#se-define-un-alcance-y-objetivo-general)
      - [Historias de suario y criterios de aceptación](#historias-de-suario-y-criterios-de-aceptación)
        - [HU1 - CRUD de eventos](#hu1---crud-de-eventos)
        - [HU2 - Venta de entradas](#hu2---venta-de-entradas)
        - [HU3 - Devolución de entradas](#hu3---devolución-de-entradas)
        - [HU4 - Reporte de estado](#hu4---reporte-de-estado)
        - [HU5 - Autenticación y permisos](#hu5---autenticación-y-permisos)
        - [HU6 - Filtrado y búsqueda](#hu6---filtrado-y-búsqueda)
  - [Pruebas](#pruebas)
    - [Estrategia](#estrategia)
    - [Ejemplos de pruebas](#ejemplos-de-pruebas)
  - [Problemas encontrados y soluciones](#problemas-encontrados-y-soluciones)


## Descripción
Este proyecto proporciona una aplicación web para gestionar entradas de micro-eventos, como charlas, talleres o actividades de corta duración. 
Permite a los organizadores:

- Registrar y gestionar entradas.
- Validar la asistencia de los participantes.
- Generar reportes de ventas y asistencia.

## Tecnologías (Tkinter)

### Instalación y ejecución

- Python 3.11+
- PostgreSQL 14+
- pip install -r requirements.txt

### Frontend
El frontend se construirá usando la librería estándar Tkinter de Python. Se encargará de la interfaz de usuario, permitiendo a los administradores interactuar con el sistema de manera visual.

### Backend (Python)
El backend, desarrollado en Python. Contiene la lógica de negocio y gestiona toda la comunicación con la base de datos. 

### Base de Datos (PostgreSQL)
PostgreSQL almacenará todos los datos de la aplicación. Se diseñará un esquema relacional simple y robusto para garantizar la integridad de los datos.

```bash
-- 001_schema.sql (resumen esencial)
CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  username TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  role TEXT DEFAULT 'organizer'
);

CREATE TABLE IF NOT EXISTS events (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT,
  event_date TIMESTAMP NOT NULL,
  category TEXT,
  price NUMERIC(12,2) DEFAULT 0,
  available_tickets INT DEFAULT 0,
  creator_id INT,
  CONSTRAINT events_stock_nonnegative CHECK (available_tickets >= 0)
);

CREATE TABLE IF NOT EXISTS tickets (
  id SERIAL PRIMARY KEY,
  event_id INT NOT NULL REFERENCES events(id) ON DELETE CASCADE,
  buyer_name TEXT NOT NULL,
  buyer_email TEXT,
  price NUMERIC(12,2) NOT NULL,
  sold_at TIMESTAMP NOT NULL DEFAULT NOW(),
  UNIQUE (event_id, buyer_email, buyer_name)
);

CREATE TABLE IF NOT EXISTS attendance (
  id SERIAL PRIMARY KEY,
  ticket_id INT NOT NULL UNIQUE REFERENCES tickets(id) ON DELETE CASCADE,
  checked_in_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tickets_event ON tickets(event_id);
CREATE INDEX IF NOT EXISTS idx_tickets_sold_at ON tickets(sold_at);
```

### API (FastAPI)
#### Autenticación
- POST /users — crear usuario (hash con bcrypt).
- POST /auth/login — login (valida hash); retorno {ok, role}.

#### Eventos
- GET /events/summary — {total_events, total_available_tickets, sold_out}
- POST /events — crear
- GET /events?creator_id= — listar (+ filtro)
- GET /events/{id} — detalle
- PUT /events/{id} — actualizar
- DELETE /events/{id}?user_id= — eliminar (opcional ownership)
- Tickets (venta/consulta/refund) — anti sobre-venta atómico
- POST /tickets — vende 1 ticket

#### Lógica (transacción):
- UPDATE events SET available_tickets = available_tickets - 1 WHERE id=%s AND available_tickets > 0 RETURNING available_tickets
- INSERT INTO tickets ...
- Si 2) falla → rollback y reponer cupo.
- Respuesta incluye remaining_available.
- GET /tickets — filtros: event_id, buyer, date_from, date_to, checked=(yes|no|all); incluye columna checked.
- GET /tickets/{id} — detalle
- DELETE /tickets/{id}?refund=1 — refund (borra attendance si existe, borra ticket, suma 1 cupo y retorna remaining_available)
#### Attendance (check-in)
- POST /attendance — marca asistencia (único por ticket; 409 si repetido)
- GET /attendance/{ticket_id} — consulta
- DELETE /attendance/{ticket_id} — desmarca

## Estructura del repositorio

```bash
.
├─ api/
│  └─ app.py                 # FastAPI (endpoints auth, events, tickets, attendance)
├─ db/
│  ├─ db.py                  # conexión psycopg2 (context manager)
│  └─ init/001_schema.sql    # DDL
├─ project/
│  ├─ services/
│  │  ├─ event_manager.py    # cliente HTTP para eventos
│  │  └─ ticket_manager.py   # cliente HTTP para tickets/attendance
│  └─ interface/
│     ├─ login_screen.py
│     ├─ main_window.py
│     ├─ tickets/
│     │  ├─ build_tickets_view.py  # selector de evento, venta/refund/check-in, filtros
│     │  ├─ build_events_view.py   # listado/CRUD eventos
│     │  └─ show_view.py
│     └─ main_window_components/
│        └─ main_banner.py
├─ main.py                   # entrypoint de UI
├─ requirements.txt
├─ .env.example
├─ README.md                 # este documento
└─ docs/screenshots/         # capturas
```

## Funcionalidades principales
- Registro de entradas por evento.
- Validación de asistencia.
- Reportes de participantes y ventas.
- Gestión de eventos y usuarios organizadores.

## Contribución
Para colaborar, usar la branch `dev` para desarrollo y enviar Pull Requests a `main` cuando los cambios estén listos.

# Respuestas a las preguntas propuestas

## ¿Cómo especificamos mejor el requerimiento?

### Se define un alcance y objetivo general:

Construír una aplicación sencilla para una productora local que permita gestionar eventos, vender y devolver entradas, filtrar/buscar eventos y mostrar reportes con resumen, total de eventos regstrados y eventos agotados que esté protegido por métodos de autenticación.

### Historias de suario y criterios de aceptación

#### HU1 - CRUD de eventos
| ID  | Título          | Como                      | Quiero                                  | Para                              | Prioridad |
| --- | --------------- | ------------------------- | --------------------------------------- | --------------------------------- | --------- |
| HU1 | CRUD de eventos | Administrador autenticado | Crear/editar/eliminar/consultar eventos | Mantener la cartelera actualizada | Alta      |

| Criterios de Aceptación |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| CA1: Un evento requiere **nombre**, **descripción**, **fecha** en formato ISO 8601 según la norma internacional, **categoría** ∈ {Charla, Taller, Show}, **precio** (entero ≥ 0), **cuposDisponibles** (entero ≥ 0).
<br>CA2: No se permite guardar eventos que ya fueron realizados se puede mostrar un bloque o advertencia.
<br>CA3: Si el evento no se puede vender, es decir, no hay más cupos se debe eliminar o quedar inactivo.
<br>CA4: Listado **paginado** y **ordenable por fecha**; filtros por **categoría**, **texto** y **estado** (Agotado/Con cupos). |

#### HU2 - Venta de entradas
| ID  | Título           | Como                 | Quiero                       | Para                           | Prioridad |
| --- | ---------------- | -------------------- | ---------------------------- | ------------------------------ | --------- |
| HU2 | Registrar ventas | Operador autenticado | Registrar ventas de entradas | Controlar cupos en tiempo real | Alta      |

| Criterios de Aceptación                                                                                                                                                                                                                                                                                           |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CA1: No se puede vender si `cuposDisponibles − cantidad < 0` (No puede haber sobreventa de entradas).
<br>CA2: Cada venta debe generar una **transacción** con timestamp, evento, cantidad y usuario que realizó la compra.
<br>CA3: `cuposDisponibles` **disminuye** en la cantidad vendida por venta y cantidad de entradas.
<br>CA4: Debe quedar registrada la transacción en un log de información: “Venta registrada: evento=X, qty=Y, por=usuario”. |

#### HU3 - Devolución de entradas
| ID  | Título                 | Como                 | Quiero                             | Para                         | Prioridad |
| --- | ---------------------- | -------------------- | ---------------------------------- | ---------------------------- | --------- |
| HU3 | Registrar devoluciones | Operador autenticado | Registrar devoluciones de entradas | Liberar cupos cuando procede | Media     |

| Criterios de Aceptación                                                                                                                                                                                                                                                         |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CA1: La devolución **no puede superar** las ventas acumuladas del evento y/o compradas por el usuario que requiere la devolución (no puede existir una sobre devolución).
<br>CA2: Genera transacción tipo **REFUND**; `cuposDisponibles` **aumenta** en la cantidad devuelta.
<br>CA3: Debe quedar registrada la transacción en un log de información: “Devolución registrada: evento=X, qty=Y, por=usuario”. |

#### HU4 - Reporte de estado
| ID  | Título      | Como                      | Quiero                     | Para                    | Prioridad |
| --- | ----------- | ------------------------- | -------------------------- | ----------------------- | --------- |
| HU4 | Ver resumen | Administrador autenticado | Ver un resumen con totales | Decidir acciones rápido | Media     |

| Criterios de Aceptación                                                                                                                                                                                   |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CA1: Pantalla/endpoint “**Resumen**” muestra: **totalEventos**, **cuposTotales** (suma de cupos disponibles) y **agotados** (eventos con 0 cupos).
<br>CA2: El cálculo debe considerar solo eventos activos. |

#### HU5 - Autenticación y permisos
| ID  | Título               | Como                    | Quiero                            | Para                           | Prioridad |
| --- | -------------------- | ----------------------- | --------------------------------- | ------------------------------ | --------- |
| HU5 | Autenticación básica | Equipo de la productora | Ingresar con usuario y contraseña | Restringir acciones de gestión | Alta      |

| Criterios de Aceptación                                                                                                                                                                                                                                                                                                        |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| CA1: Sin autenticación solo se ve la pantalla de login.
<br>CA2: Tras login exitoso se habilitan **CRUD**, **ventas** y **devoluciones** según los permisos del usuario.
<br>CA3: Contraseñas se guardan **cifradas** (bcrypt/argon2); nunca en texto plano. 
<br>CA4: Los usuarios pueden tener diferentes tipos de rol, tales como Administrados, Usuario (cliente)|

#### HU6 - Filtrado y búsqueda
| ID  | Título                   | Como                               | Quiero                                          | Para                       | Prioridad |
| --- | ------------------------ | ---------------------------------- | ----------------------------------------------- | -------------------------- | --------- |
| HU6 | Filtrar y buscar eventos | Operador/Administrador autenticado | Filtrar por categoría/estado y buscar por texto | Encontrar rápido un evento | Media     |

| Criterios de Aceptación                                                                                                                                                                                                           |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CA1: Filtros por **categoría** (Charla/Taller/Show) y **estado** (Agotado/Con cupos).
<br>CA2: **Búsqueda por texto** por nombre/descripción.
<br>CA3: Combinación de filtros + búsqueda. |

## Pruebas

### Estrategia

#### Unitarias (backend y cliente):
- Validaciones puras (email, fechas, payloads).
- Helpers que no requieren DB.
#### API (integración):
- Ventas atómicas (sin sobre-venta).
- Refund suma cupo y borra attendance.
- Check-in único.
- Filtros (buyer, date_from/to, checked).
- Autenticación (login correcto/incorrecto).
#### End-to-End (E2E):
- Flujo real con servidor FastAPI levantado + UI Tkinter:
- Crear evento → vender N → validar cupos en UI → refund → revalidar cupos.
- Agregar, quitar eventos disponibles y cantidad.
#### Pruebas cruzadas de UI (manuales en equipo):
- Ciclo 1: individuales.
- Ciclo 2: consolidado.
- Ciclo 3 (opcional): regresión sobre bugs.

### Ejemplos de pruebas:

| Id\_Test | Entrada                                         | Resultado Esperado                | Resultado Obtenido | Éxito | Comentario           |
| -------- | ----------------------------------------------- | --------------------------------- | ------------------ | ----- | -------------------- |
| API-001  | `POST /tickets` con `available_tickets=1`       | 201 + `remaining_available=0`     |                    |       | Atómico              |
| API-002  | 2 ventas concurrentes con `available_tickets=1` | 1 éxito, 1 `409`                  |                    |       | Evita sobre-venta    |
| API-003  | `DELETE /tickets/{id}?refund=1`                 | `remaining_available = prev+1`    |                    |       | Sube cupo            |
| API-004  | `POST /attendance` repetido                     | `409`                             |                    |       | Único                |
| API-005  | `POST /tickets` con email inválido              | `400`                             |                    |       | Validación           |
| UI-001   | Seleccionar evento agotado                      | Selecciona OK, venta bloqueada    |                    |       | Refund permitido     |
| UI-002   | Cantidad > cupos                                | Error bloqueante                  |                    |       | Spinbox y validación |
| UI-003   | Filtro buyer + rango fechas                     | Lista tickets correctos           |                    |       |                      |
| UI-004   | Post-venta                                      | Cupos bajan en etiqueta y resumen |                    |       |                      |
| UI-005   | Post-refund                                     | Cupos suben en etiqueta y resumen |                    |       |                      |


## Problemas encontrados y soluciones

Import relativo roto (ModuleNotFoundError: project.project)
➜ Usar from project.services.event_manager import get_all_events o from ..services... y asegurar __init__.py.

Sobre-venta de tickets
➜ Venta atómica: UPDATE ... available_tickets > 0 RETURNING. Reposición de cupo si falla INSERT.

Cupos no actualizaban en la UI
➜ Tras vender/refund: refrescar tabla de tickets, _load_all_events(), _load_summary() y reconsultar get_event_by_id.

Email inválido disparaba múltiples popups
➜ Validar antes del loop en venta múltiple (una sola advertencia).

Seleccionar evento agotado
➜ Permitido (para refunds). Solo se bloquea vender si cupos=0.
