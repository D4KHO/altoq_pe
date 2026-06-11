import sys
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Agregar el directorio raíz del proyecto al path de Python
# para que pueda importar los módulos de la app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Alembic Config object
config = context.config

# Configurar logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ---- CONFIGURACIÓN DE LA BASE DE DATOS ----
# Leer la URL de la base de datos desde el archivo .env
# (usando la misma configuración que FastAPI)
from app.config import settings
config.set_main_option("sqlalchemy.url", settings.database_url)

# ---- IMPORTAR BASE Y TODOS LOS MODELOS ----
# Importamos Base (DeclarativeBase) y todos los modelos para que Alembic
# pueda detectar las tablas y generar migraciones automáticamente.
# El orden de importación es importante para resolver las FK correctamente.
from app.database import Base  # noqa: F401
from app.models import (  # noqa: F401
    Admin,
    User,
    Category,
    Store,
    Address,
    Product,
    Order,
    Chat,
    Message,
    DeliveryCode,
    ProductTemplate,
    TemplateField,
    StoreMetric,
)

# target_metadata es lo que Alembic usa para comparar modelos con la BD
# y generar migraciones automáticas con --autogenerate
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    Configura el contexto solo con la URL, sin crear un Engine real.
    Útil para generar SQL sin conectarse a la BD.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    Crea un Engine real y asocia la conexión con el contexto.
    Es el modo estándar para ejecutar migraciones.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
