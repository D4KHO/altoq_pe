# Guía de Migraciones de Base de Datos - AltoQ Backend

Este proyecto utiliza **Alembic** para el manejo de migraciones, similar a las migraciones de Laravel en PHP.

## 📋 ¿Qué es una migración?

Las migraciones son archivos que controlan los cambios en la estructura de tu base de datos. Permiten:
- Crear y modificar tablas de forma versionada
- Mantener sincronización entre desarrolladores
- Revertir cambios si es necesario
- Tener un historial completo de la evolución de la BD

## 🚀 Comandos Disponibles

El script `migrate.py` es un wrapper que simplifica el uso de Alembic con comandos similares a Laravel:

### Ejecutar migraciones pendientes
```bash
python migrate.py
# o
python migrate.py up
# o
python migrate.py migrate
```
**Equivalente Laravel:** `php artisan migrate`

### Crear una nueva migración
```bash
python migrate.py create "descripcion del cambio"
```
**Equivalente Laravel:** `php artisan make:migration descripcion_del_cambio`

Esto genera automáticamente una migración basada en los cambios en los modelos SQLAlchemy.

### Revertir la última migración
```bash
python migrate.py rollback
# Revertir N migraciones
python migrate.py rollback 3
```
**Equivalente Laravel:** `php artisan migrate:rollback`

### Ver estado actual
```bash
python migrate.py status
# o
python migrate.py current
```
**Equivalente Laravel:** `php artisan migrate:status`

### Ver historial de migraciones
```bash
python migrate.py history
# o
python migrate.py log
```
**Equivalente Laravel:** `php artisan migrate:show`

### Revertir todas las migraciones
```bash
python migrate.py reset
```
**Equivalente Laravel:** `php artisan migrate:reset`

## 📝 Flujo de Trabajo Típico

### 1. Modificar un Modelo
Cuando necesites hacer un cambio en la base de datos:

```python
# app/models/user.py
class User(Base):
    # ... campos existentes ...
    phone = Column(String(20), nullable=True)  # Nuevo campo
```

### 2. Crear la Migración
```bash
python migrate.py create "agregar campo phone a users"
```

Esto creará un archivo nuevo en `alembic/versions/` con los cambios detectados automáticamente.

### 3. Revisar la Migración
Abre el archivo generado en `alembic/versions/` y verifica que los cambios sean correctos:

```python
# alembic/versions/XXXX_agregar_campo_phone_a_users.py
def upgrade() -> None:
    op.add_column('users', sa.Column('phone', sa.String(20), nullable=True))

def downgrade() -> None:
    op.drop_column('users', 'phone')
```

### 4. Ejecutar la Migración
```bash
python migrate.py
```

## 🔧 Configuración

### Archivo de Configuración
- **`.env`**: Contiene la URL de conexión a la base de datos
- **`alembic.ini`**: Configuración principal de Alembic
- **`alembic/env.py`**: Configuración del entorno y carga de modelos

### Estructura de Archivos
```
altoq_backend/
├── alembic/
│   ├── versions/          # Archivos de migración
│   │   └── 0001_initial_estado_inicial.py
│   ├── env.py            # Configuración del entorno
│   └── script.py.mako    # Template para nuevas migraciones
├── alembic.ini           # Configuración de Alembic
├── migrate.py            # Script wrapper (comandos tipo Laravel)
└── app/
    └── models/           # Modelos SQLAlchemy
```

## 💡 Ejemplos Comunes

### Agregar una columna
```bash
python migrate.py create "agregar campo telefono a users"
```

### Crear una nueva tabla
```bash
# 1. Crear el modelo en app/models/nuevo_modelo.py
# 2. Importarlo en app/models/__init__.py
# 3. Crear la migración
python migrate.py create "crear tabla nuevos_modelos"
```

### Modificar una columna
```bash
# 1. Modificar el modelo
# 2. Crear la migración
python migrate.py create "modificar tipo de campo email"
```

### Agregar un índice
```bash
# 1. Agregar index=True en el modelo
# 2. Crear la migración
python migrate.py create "agregar indice unico a email"
```

## ⚠️ Buenas Prácticas

1. **Siempre revisa la migración generada** antes de ejecutarla
2. **Usa mensajes descriptivos** para las migraciones
3. **Mantén los modelos actualizados** - las migraciones se generan comparando modelos con BD
4. **Haz commit de las migraciones** junto con los cambios en código
5. **Nunca edites directamente la base de datos** en producción
6. **Prueba las migraciones** en desarrollo antes de producción

## 🐛 Solución de Problemas

### Error: "Target database is not up to date"
```bash
python migrate.py status  # Ver qué migraciones faltan
python migrate.py         # Ejecutar migraciones pendientes
```

### Error: "No module named 'app'"
Verifica que estás en el directorio `altoq_backend/` y que el entorno virtual está activado.

### La migración no detecta cambios
1. Verifica que importaste el modelo en `app/models/__init__.py`
2. Verifica que el modelo herede de `Base`
3. Asegúrate de que los cambios estén en los modelos, no en la BD directamente

## 📚 Recursos Adicionales

- [Documentación de Alembic](https://alembic.sqlalchemy.org/)
- [Documentación de SQLAlchemy](https://docs.sqlalchemy.org/)
- [FastAPI Database Tutorial](https://fastapi.tiangolo.com/tutorial/sql-databases/)
