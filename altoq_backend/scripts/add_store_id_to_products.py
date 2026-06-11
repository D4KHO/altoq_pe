import os
import sys
from sqlalchemy import text

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine

def add_store_id_column():
    """Agrega la columna store_id a la tabla products"""
    try:
        with engine.connect() as conn:
            # Verificar si la columna ya existe
            result = conn.execute(text("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'products' AND COLUMN_NAME = 'store_id'
            """))
            
            if result.fetchone():
                print("La columna store_id ya existe en la tabla products")
                return
            
            # Agregar la columna store_id
            conn.execute(text("""
                ALTER TABLE products 
                ADD COLUMN store_id INT NULL,
                ADD FOREIGN KEY (store_id) REFERENCES stores(id)
            """))
            
            conn.commit()
            print("Columna store_id agregada exitosamente a la tabla products")
            
    except Exception as e:
        print(f"Error al agregar columna store_id: {e}")
        raise

if __name__ == "__main__":
    add_store_id_column()
