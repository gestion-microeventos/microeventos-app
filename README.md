# Gestión de Entradas para Micro-Eventos

## Descripción
Este proyecto proporciona una aplicación web para gestionar entradas de micro-eventos, como charlas, talleres o actividades de corta duración. 
Permite a los organizadores:

- Registrar y gestionar entradas.
- Validar la asistencia de los participantes.
- Generar reportes de ventas y asistencia.

## Tecnologías 

### Frontend (Tkinter)
El frontend se construirá usando la librería estándar Tkinter de Python. Se encargará de la interfaz de usuario, permitiendo a los administradores interactuar con el sistema de manera visual.

### Backend (Python)
El backend, desarrollado en Python. Contiene la lógica de negocio y gestiona toda la comunicación con la base de datos. 

### Base de Datos (PostgreSQL)
PostgreSQL almacenará todos los datos de la aplicación. Se diseñará un esquema relacional simple y robusto para garantizar la integridad de los datos.

## Dependencias

Instala las dependencias con:

```bash
pip install psycopg2-binary python-dotenv tkcalendar bcrypt
```
* psycopg2-binary: Conector para interactuar con bases de datos PostgreSQL desde Python.
* python-dotenv: Permite gestionar variables de entorno desde un archivo .env (útil para credenciales y configuraciones).
* tkcalendar: Widget de calendario para interfaces gráficas en Tkinter.
* bcrypt: Librería para encriptar y verificar contraseñas de manera segura.

## Configuración de la Base de Datos y Credenciales

El proyecto utiliza la librería python-dotenv para leer las variables del archivo .env.

### Pasos para la Configuración de Variable de Entorno

1. Crear el archivo .env: En la raíz de tu proyecto, crea un nuevo archivo llamado .env.
2. Añadir las variables: Copia y pega el siguiente código en el archivo, reemplazando los valores de ejemplo con tus propias credenciales de PostgreSQL.

```bash
DB_HOST=localhost
DB_NAME=nombre_de_tu_base_de_datos
DB_USER=usuario_de_tu_base_de_datos
DB_PASSWORD=contraseña_de_tu_base_de_datos
```

### Crear Base de Datos y Tablas
1. Crear la base de datos: Abre tu terminal o una herramienta como PgAdmin y crea una base de datos con el nombre microeventos.
2. Crear tablas: Haz click derecho en tu base de datos y selecciona "Query Tool", pega el siguiente código y luego ejecuta.

```SQL
-- Tabla para almacenar la información de los usuarios
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(60) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user',
);

-- Tabla para almacenar los eventos
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    event_date TIMESTAMP WITH TIME ZONE NOT NULL,
    category VARCHAR(50),
    price NUMERIC(10, 2) NOT NULL,
    available_tickets INTEGER NOT NULL,
    creator_id INTEGER NOT NULL,
    
    -- Restricción de clave externa para vincular con el creador del evento
    FOREIGN KEY (creator_id) REFERENCES users(id) ON DELETE CASCADE
);
```
## Cómo Ejecutar la Aplicación

Asegúrate de tener instalados Python 3.x y PostgreSQL, tener la base de datos configurada (con sus respectivas tablas) y la variable de entorno creada.
* Abre tu terminal.
* Navega hasta el directorio raíz de tu proyecto.
* Ejecuta el archivo principal con el siguiente comando

````bash
python main.py
````


## Estructura del repositorio

```bash
├──project/
│ ├─ interface/
│ │ ├─ event_details.py
│ │ ├─ login_screen.py
│ │ ├─ main_window.py
│ │ └─ new_event.py
│ ├─ services/
│ │ ├─ auth_manager.py
│ │ ├─ event_manager.py
│ │ └─ user_manager.py
│ └─ database/
│   └─ db_manager.py
├── tests/
│ ├─ test_services.py
│ └─ ...
├── main.py
├── .gitignore
├── .env
└── README.md
```

## Funcionalidades principales
- Registro de entradas por evento.
- Validación de asistencia.
- Gestión de eventos y usuarios organizadores.

## Contribución
Para colaborar, usar la branch `dev` para desarrollo y enviar Pull Requests a `main` cuando los cambios estén listos.
