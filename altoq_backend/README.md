# ALTOQ Backend - FastAPI

Backend del marketplace ALTOQ construido con FastAPI y MySQL.

## Requisitos Previos

- Python 3.8+
- MySQL Server 8.0+

## Configuración de Base de Datos

1. Crear la base de datos en MySQL:
```sql
CREATE DATABASE altoq_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. Crear archivo `.env` basado en `.env.example`:
```bash
cp .env.example .env
```

3. Editar `.env` con tus credenciales de MySQL:
```
DATABASE_URL=mysql+pymysql://root:tu_password@localhost:3306/altoq_db
```

## Instalación

1. Crear entorno virtual:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Crear las tablas de la base de datos (migraciones):
```bash
python migrate.py
```

4. Ejecutar servidor:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Migraciones (Base de Datos)

Este proyecto usa **Alembic** para manejar las migraciones de base de datos (similar a `php artisan migrate` en Laravel).

### Comandos disponibles

| Acción | Comando |
| :--- | :--- |
| **Ejecutar migraciones pendientes** | `python migrate.py` |
| **Crear nueva migración** (detecta cambios en tus modelos) | `python migrate.py create "descripción del cambio"` |
| **Revertir la última migración** | `python migrate.py rollback` |
| **Ver estado actual** | `python migrate.py status` |
| **Ver historial completo** | `python migrate.py history` |
| **Revertir TODO** | `python migrate.py reset` |

### Flujo de trabajo

1. Modifica o crea un modelo en `app/models/`
2. Importa el modelo en `app/models/__init__.py`
3. Ejecuta: `python migrate.py create "descripcion del cambio"`
4. Ejecuta: `python migrate.py` para aplicar los cambios a la BD

## Endpoints

### Productos
- `GET /api/products` - Lista de productos
- `GET /api/products/{id}` - Detalle de producto
- `POST /api/products` - Crear producto
- `PUT /api/products/{id}` - Actualizar producto
- `DELETE /api/products/{id}` - Eliminar producto

### Autenticación
- `POST /api/auth/register` - Registrar usuario
- `POST /api/auth/login` - Iniciar sesión

### Órdenes
- `POST /api/orders` - Crear orden
- `GET /api/orders/user` - Órdenes del usuario
- `GET /api/orders/{id}` - Detalle de orden

## Documentación API

Accede a la documentación interactiva en:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
