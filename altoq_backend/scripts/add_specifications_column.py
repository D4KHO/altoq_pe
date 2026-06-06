from sqlalchemy import create_engine, Column, JSON, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root@localhost/altoq_db")

engine = create_engine(DATABASE_URL)
Base = declarative_base()

def add_specifications_column():
    """Add specifications column to products table"""
    try:
        print("Adding specifications column to products table...")
        
        with engine.connect() as conn:
            # Add the specifications column as JSON - use text() for SQLAlchemy 2.0
            conn.execute(text("ALTER TABLE products ADD COLUMN specifications JSON NULL"))
            conn.commit()
            
        print("✓ Successfully added specifications column")
        
    except Exception as e:
        if "Duplicate column name" in str(e):
            print("ℹ Column 'specifications' already exists")
        else:
            print(f"✗ Error: {e}")
            raise

if __name__ == "__main__":
    add_specifications_column()
