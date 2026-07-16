import sys
import os

# Agregar el directorio actual al path para importar correctamente
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from seeders import admin_seeder

def main():
    print("=" * 60)
    print("      ORQUESTRADOR DE SEMBRADO (DATABASE SEEDER) - ALTOQ")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        # Ejecutar únicamente el seeder de administración
        admin_seeder.run(db)
        
        print("\n" + "=" * 60)
        print("  [OK] ¡Base de datos sembrada únicamente con el usuario administrador!")
        print("=" * 60)
        
    except Exception as e:
        db.rollback()
        print(f"\n[ERROR] Ocurrió un error al sembrar la base de datos: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()
