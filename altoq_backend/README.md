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

### Comandos disponibles (Estilo Laravel)

| Acción | Comando Laravel | Comando AltoQ |
| :--- | :--- | :--- |
| **Ejecutar migraciones pendientes** | `php artisan migrate` | `python migrate.py` |
| **Crear nueva migración** | `php artisan make:migration` | `python migrate.py create "descripción"` |
| **Revertir última migración** | `php artisan migrate:rollback` | `python migrate.py rollback` |
| **Ver estado actual** | `php artisan migrate:status` | `python migrate.py status` |
| **Ver historial completo** | `php artisan migrate:show` | `python migrate.py history` |
| **Revertir TODO** | `php artisan migrate:reset` | `python migrate.py reset` |
| **Recrear BD desde cero** | `php artisan migrate:fresh` | `python migrate.py fresh` |

### Flujo de trabajo típico

1. Modifica o crea un modelo en `app/models/`
2. Importa el modelo en `app/models/__init__.py`
3. Ejecuta: `python migrate.py create "descripcion del cambio"`
4. Revisa el archivo generado en `alembic/versions/`
5. Ejecuta: `python migrate.py` para aplicar los cambios a la BD

### Documentación adicional

- **[QUICKSTART_MIGRATIONS.md](QUICKSTART_MIGRATIONS.md)** - Guía rápida de inicio
- **[MIGRATIONS_GUIDE.md](MIGRATIONS_GUIDE.md)** - Documentación completa del sistema

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
