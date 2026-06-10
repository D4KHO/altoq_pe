# 🚀 Inicio Rápido - Sistema de Migraciones

## Configuración Inicial

### 1. Crear archivo .env
Si no tienes un archivo `.env`, el script `migrate.py` lo creará automáticamente desde `.env.example` la primera vez que lo ejecutes.

```bash
# El script creará .env automáticamente desde .env.example
python migrate.py status
```

Luego edita `.env` con tus credenciales de base de datos:
```env
DATABASE_URL=mysql+pymysql://root:tu_password@localhost:3306/altoq_db
SECRET_KEY=tu_clave_secreta_super_segura_cambiala_en_produccion
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 2. Verificar estado de migraciones
```bash
python migrate.py status
```

### 3. Ejecutar migraciones pendientes
```bash
python migrate.py
```

## Comandos Básicos (Estilo Laravel)

| Comando Laravel | Comando AltoQ | Descripción |
|----------------|---------------|-------------|
| `php artisan migrate` | `python migrate.py` | Ejecutar migraciones pendientes |
| `php artisan migrate:rollback` | `python migrate.py rollback` | Revertir última migración |
| `php artisan migrate:reset` | `python migrate.py reset` | Revertir todas las migraciones |
| `php artisan migrate:fresh` | `python migrate.py fresh` | Eliminar BD y recrear desde cero |
| `php artisan migrate:status` | `python migrate.py status` | Ver estado actual |
| `php artisan make:migration` | `python migrate.py create "mensaje"` | Crear nueva migración |

## Ejemplo de Flujo de Trabajo

### Escenario: Agregar un nuevo campo a la tabla users

**Paso 1: Modificar el modelo**
```python
# app/models/user.py
class User(Base):
    # ... campos existentes ...
    phone = Column(String(20), nullable=True)  # Nuevo campo
```

**Paso 2: Crear la migración**
```bash
python migrate.py create "agregar campo phone a users"
```

Esto generará un archivo como: `alembic/versions/XXXX_agregar_campo_phone_a_users.py`

**Paso 3: Revisar la migración generada**
```python
# alembic/versions/XXXX_agregar_campo_phone_a_users.py
def upgrade() -> None:
    op.add_column('users', sa.Column('phone', sa.String(20), nullable=True))

def downgrade() -> None:
    op.drop_column('users', 'phone')
```

**Paso 4: Ejecutar la migración**
```bash
python migrate.py
```

**Paso 5: Si necesitas revertir**
```bash
python migrate.py rollback
```

## Solución de Problemas Comunes

### Error: "No module named 'app'"
**Solución:** Asegúrate de estar en el directorio `altoq_backend/` cuando ejecutes el comando.

### Error: "Access denied for user"
**Solución:** Verifica que las credenciales en `.env` sean correctas.

### La migración no detecta cambios
**Solución:** 
1. Verifica que importaste el modelo en `app/models/__init__.py`
2. Verifica que el modelo herede de `Base`
3. Asegúrate de que los cambios estén en el modelo, no directamente en la BD

## Documentación Completa

Para más detalles, consulta: [MIGRATIONS_GUIDE.md](MIGRATIONS_GUIDE.md)
