from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root@localhost/altoq_db")
engine = create_engine(DATABASE_URL)

inspector = inspect(engine)

# Get columns from products table
columns = inspector.get_columns('products')

print("Columnas en la tabla 'products':")
print("-" * 50)
for col in columns:
    print(f"- {col['name']}: {col['type']}")
