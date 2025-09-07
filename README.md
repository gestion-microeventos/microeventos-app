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
