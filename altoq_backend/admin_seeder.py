import sys
import os

# Agregar el directorio actual al path para importar correctamente
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.admin import Admin
from app.utils.security import get_password_hash

def seed_admin():
    print("=" * 60)
    print("      SEMILLERO DEL ADMINISTRADOR (ADMIN SEEDER) - ALTOQ")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        # Verificar si el administrador ya existe
        existing_admin = db.query(Admin).filter(Admin.username == "admin").first()
        if not existing_admin:
            admin = Admin(
                username="admin",
                email="admin@altoq.com",
                password_hash=get_password_hash("admin123"),
                full_name="Administrator"
            )
            db.add(admin)
            db.commit()
            print("  + Usuario administrador ('admin' / 'admin123') creado exitosamente.")
        else:
            print("  ~ El usuario administrador 'admin' ya existe.")
            
        print("\n" + "=" * 60)
        print("  [OK] ¡Base de datos sembrada con el usuario administrador!")
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
    seed_admin()
