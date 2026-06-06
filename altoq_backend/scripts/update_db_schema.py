import pymysql
from app.config import settings
from sqlalchemy import create_engine, text

# Conexión directa para ejecutar DDL
DATABASE_URL = settings.database_url.replace("mysql+pymysql", "mysql+pymysql")

engine = create_engine(DATABASE_URL)

def add_column_if_not_exists(table, column, definition):
    with engine.connect() as connection:
        # Verificar si la columna existe
        result = connection.execute(text(f"SHOW COLUMNS FROM {table} LIKE '{column}'"))
        if result.fetchone():
            print(f"Columna '{column}' ya existe en '{table}'.")
        else:
            print(f"Agregando columna '{column}' a '{table}'...")
            connection.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {definition}"))
            connection.commit()
            print(f"Columna '{column}' agregada exitosamente.")

if __name__ == "__main__":
    print("Iniciando actualización de esquema...")
    try:
        add_column_if_not_exists("products", "rating", "FLOAT DEFAULT 0.0")
        add_column_if_not_exists("products", "rating_count", "INT DEFAULT 0")
        print("Actualización completada.")
    except Exception as e:
        print(f"Error durante la actualización: {e}")
