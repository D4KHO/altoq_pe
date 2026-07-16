from sqlalchemy.orm import Session
from app.models.admin import Admin
from app.utils.security import get_password_hash

def run(db: Session):
    print("\nSembrando usuario administrador...")
    
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
