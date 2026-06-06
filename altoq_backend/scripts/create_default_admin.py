from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
import sys

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.admin import Admin
from app.utils.security import get_password_hash

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:@localhost:3306/altoq_db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def create_default_admin():
    """Create default admin user for first time setup"""
    db = SessionLocal()
    
    try:
        # Check if admin already exists
        existing_admin = db.query(Admin).filter(Admin.username == "admin").first()
        
        if existing_admin:
            print("ℹ Default admin user already exists")
            return
        
        # Create default admin
        admin = Admin(
            username="admin",
            email="admin@altoq.com",
            password_hash=get_password_hash("admin123"),
            full_name="Administrator"
        )
        
        db.add(admin)
        db.commit()
        
        print("✓ Default admin created successfully!")
        print("\n" + "="*50)
        print("Default Admin Credentials:")
        print("Username: admin")
        print("Password: admin123")
        print("="*50)
        print("\n⚠️  IMPORTANT: Change the password after first login!")
        
    except Exception as e:
        print(f"✗ Error creating default admin: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_default_admin()
