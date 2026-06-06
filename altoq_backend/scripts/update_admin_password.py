from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
import sys
import bcrypt

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:@localhost:3306/altoq_db")
engine = create_engine(DATABASE_URL)

def create_password_hash(password: str) -> str:
    """Hash password using bcrypt directly"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def update_admin_password():
    """Update admin password with new bcrypt hash"""
    password_hash = create_password_hash("admin123")
    
    with engine.connect() as conn:
        # Update admin password
        result = conn.execute(
            text("UPDATE admins SET password_hash = :hash WHERE username = 'admin'"),
            {"hash": password_hash}
        )
        conn.commit()
        
        if result.rowcount > 0:
            print("✓ Admin password updated successfully!")
            print("\nCredentials:")
            print("Username: admin")
            print("Password: admin123")
        else:
            print("✗ Admin user not found. Creating new admin...")
            conn.execute(
                text("""
                    INSERT INTO admins (username, email, password_hash, full_name) 
                    VALUES ('admin', 'admin@altoq.com', :hash, 'Administrator')
                """),
                {"hash": password_hash}
            )
            conn.commit()
            print("✓ Admin created successfully!")

if __name__ == "__main__":
    update_admin_password()
