from sqlalchemy import create_engine, text
from app.config import settings

DATABASE_URL = settings.database_url.replace("mysql+pymysql", "mysql+pymysql")
engine = create_engine(DATABASE_URL)

def add_store_name_column():
    with engine.connect() as connection:
        try:
            # Verificar si la columna ya existe
            result = connection.execute(text("SHOW COLUMNS FROM products LIKE 'store_name'"))
            if result.fetchone():
                print("La columna 'store_name' ya existe.")
                return

            print("Agregando columna 'store_name'...")
            connection.execute(text("ALTER TABLE products ADD COLUMN store_name VARCHAR(100) NULL AFTER category"))
            connection.commit()
            print("Columna agregada exitosamente.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    add_store_name_column()
