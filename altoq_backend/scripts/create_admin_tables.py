from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:@localhost:3306/altoq_db")
engine = create_engine(DATABASE_URL)

def create_admin_tables():
    """Create tables for admin panel system"""
    print("Creating admin panel tables...")
    
    with engine.connect() as conn:
        # Create admins table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS admins (
                id INT PRIMARY KEY AUTO_INCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                full_name VARCHAR(100),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_login DATETIME,
                INDEX idx_username (username),
                INDEX idx_email (email)
            )
        """))
        print("✓ Created admins table")
        
        # Update users table if needed (add password_hash if using 'password' column)
        # Note: The existing user table uses 'password', we'll keep it as-is for now
        
        # Create stores table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS stores (
                id INT PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                owner_name VARCHAR(100),
                phone VARCHAR(20),
                description VARCHAR(500),
                logo VARCHAR(255),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                status ENUM('active', 'pending', 'suspended') DEFAULT 'pending',
                INDEX idx_email (email),
                INDEX idx_status (status)
            )
        """))
        print("✓ Created stores table")
        
        conn.commit()
        print("\n✓ All admin panel tables created successfully!")

if __name__ == "__main__":
    create_admin_tables()
