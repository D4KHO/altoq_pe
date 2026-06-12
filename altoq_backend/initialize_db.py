"""
Script de inicialización de Base de Datos para AltoQ Backend.
Crea todas las tablas desde los modelos de SQLAlchemy y las marca como sincronizadas en Alembic.
"""

import sys
import os
from sqlalchemy import create_engine

# Agregar el directorio actual al path para poder importar app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import Base, engine
# Importar todos los modelos para registrarlos en Base.metadata
import app.models  # noqa: F401

def create_database_if_not_exists():
    from app.config import settings
    from sqlalchemy import create_engine, text
    
    database_url = settings.database_url
    if "sqlite" in database_url:
        return
        
    rfind_slash = database_url.rfind("/")
    if rfind_slash != -1:
        server_url = database_url[:rfind_slash]
        db_name = database_url[rfind_slash+1:]
        if "?" in db_name:
            db_name = db_name.split("?")[0]
            
        try:
            temp_engine = create_engine(server_url)
            with temp_engine.connect() as conn:
                conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
            temp_engine.dispose()
            print(f"✅ Base de datos '{db_name}' asegurada.")
        except Exception as e:
            print(f"⚠️ Advertencia al auto-crear base de datos: {e}")


def main():
    print("=" * 60)
    print("  INICIALIZADOR DE BASE DE DATOS - ALTOQ")
    print("=" * 60)
    
    try:
        # Asegurar la base de datos
        create_database_if_not_exists()
        
        # 1. Crear todas las tablas definidas en los modelos
        print("\n[1/2] Creando tablas en la base de datos...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tablas creadas exitosamente.")
        
        # 2. Registrar en Alembic que ya estamos en la última revisión (head)
        print("\n[2/2] Sincronizando historial de Alembic (stamp head)...")
        from alembic.config import Config
        from alembic import command
        
        alembic_cfg = Config("alembic.ini")
        command.stamp(alembic_cfg, "head")
        print("✅ Base de datos sincronizada con Alembic en la versión más reciente.")
        
        print("\n🎉 ¡Inicialización completada con éxito! Ya puedes usar 'python migrate.py'.")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error durante la inicialización: {e}")
        print("\nPor favor, asegúrate de que:")
        print("1. Tu servidor MySQL esté encendido.")
        print("2. Hayas creado la base de datos vacía 'altoq_db'.")
        print("3. Las credenciales en el archivo .env sean correctas.")
        sys.exit(1)

if __name__ == "__main__":
    main()
