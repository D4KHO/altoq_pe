from sqlalchemy import create_engine, text
from app.config import settings

DATABASE_URL = settings.database_url.replace("mysql+pymysql", "mysql+pymysql")
engine = create_engine(DATABASE_URL)

def update_product_rating(product_id, rating, count):
    with engine.connect() as connection:
        connection.execute(text(f"UPDATE products SET rating={rating}, rating_count={count} WHERE id={product_id}"))
        connection.commit()
        print(f"Producto {product_id} actualizado con rating {rating} y {count} opiniones.")

if __name__ == "__main__":
    # Actualizar el producto con ID 1 (asumiendo que existe)
    try:
        update_product_rating(1, 4.5, 120)
    except Exception as e:
        print(f"Error: {e}")
