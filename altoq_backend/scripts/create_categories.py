from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:@localhost:3306/altoq_db")
engine = create_engine(DATABASE_URL)

def create_categories_table():
    """Create categories table and add category_id to products"""
    print("Creating categories system...")
    
    with engine.connect() as conn:
        # Create categories table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS categories (
                id INT PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(100) NOT NULL,
                slug VARCHAR(100) UNIQUE NOT NULL,
                description TEXT,
                icon VARCHAR(100),
                parent_id INT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_slug (slug),
                INDEX idx_parent (parent_id),
                FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE SET NULL
            )
        """))
        print("✓ Created categories table")
        
        # Add category_id to products if not exists
        try:
            conn.execute(text("""
                ALTER TABLE products ADD COLUMN category_id INT NULL
            """))
            print("✓ Added category_id column to products")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("ℹ category_id column already exists in products")
            else:
                raise
        
        # Add foreign key constraint
        try:
            conn.execute(text("""
                ALTER TABLE products 
                ADD CONSTRAINT fk_product_category 
                FOREIGN KEY (category_id) REFERENCES categories(id) 
                ON DELETE SET NULL
            """))
            print("✓ Added foreign key constraint")
        except Exception as e:
            if "Duplicate foreign key" in str(e) or "already exists" in str(e):
                print("ℹ Foreign key constraint already exists")
            else:
                print(f"⚠ Could not add foreign key: {e}")
        
        conn.commit()
        print("\n✓ Categories system created successfully!")

if __name__ == "__main__":
    create_categories_table()
