# Gestión de Entradas para Micro-Eventos

## Descripción
Este proyecto proporciona una aplicación web para gestionar entradas de micro-eventos, como charlas, talleres o actividades de corta duración. 
Permite a los organizadores:

- Registrar y gestionar entradas.
- Validar la asistencia de los participantes.
- Generar reportes de ventas y asistencia.

## Tecnologías (Tkinter)

### Frontend
El frontend se construirá usando la librería estándar Tkinter de Python. Se encargará de la interfaz de usuario, permitiendo a los administradores interactuar con el sistema de manera visual.

### Backend (Python)
El backend, desarrollado en Python. Contiene la lógica de negocio y gestiona toda la comunicación con la base de datos. 

### Base de Datos (PostgreSQL)
PostgreSQL almacenará todos los datos de la aplicación. Se diseñará un esquema relacional simple y robusto para garantizar la integridad de los datos.

## Estructura del repositorio

```bash
├──project/
│ ├─ interface/
│ │ ├─ main_window.py
│ │ └─ ...
│ ├─ services/
│ │ ├─ report:generator.py
│ │ └─ ...
│ ├─ database/
│ │ ├─ db_config.py
│ │ └─ ...
│ └─ main.py
├──tests/
│ ├─ test_services.py
│ └─ ...
└─ README.md
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
