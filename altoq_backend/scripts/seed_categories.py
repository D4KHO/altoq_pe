from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:@localhost:3306/altoq_db")
engine = create_engine(DATABASE_URL)

def seed_categories():
    """Add sample categories to the database"""
    print("Seeding categories...")
    
    categories = [
        {
            "name": "Electrónica",
            "slug": "electronica",
            "description": "Productos electrónicos y tecnología",
            "icon": "⚡"
        },
        {
            "name": "Ropa y Moda",
            "slug": "ropa-moda",
            "description": "Ropa, calzado y accesorios",
            "icon": "👕"
        },
        {
            "name": "Hogar y Jardín",
            "slug": "hogar-jardin",
            "description": "Artículos para el hogar y jardín",
            "icon": "🏠"
        },
        {
            "name": "Deportes",
            "slug": "deportes",
            "description": "Artículos deportivos y fitness",
            "icon": "⚽"
        },
        {
            "name": "Juguetes y Niños",
            "slug": "juguetes-ninos",
            "description": "Juguetes y productos para niños",
            "icon": "🧸"
        },
        {
            "name": "Libros",
            "slug": "libros",
            "description": "Libros físicos y digitales",
            "icon": "📚"
        },
        {
            "name": "Belleza y Cuidado Personal",
            "slug": "belleza-cuidado",
            "description": "Productos de belleza y cuidado personal",
            "icon": "💄"
        },
        {
            "name": "Alimentos y Bebidas",
            "slug": "alimentos-bebidas",
            "description": "Comida y bebidas",
            "icon": "🍔"
        }
    ]
    
    with engine.connect() as conn:
        for cat in categories:
            # Check if category already exists
            result = conn.execute(
                text("SELECT id FROM categories WHERE slug = :slug"),
                {"slug": cat["slug"]}
            ).fetchone()
            
            if not result:
                conn.execute(
                    text("""
                        INSERT INTO categories (name, slug, description, icon)
                        VALUES (:name, :slug, :description, :icon)
                    """),
                    cat
                )
                print(f"✓ Added category: {cat['name']}")
            else:
                print(f"ℹ Category already exists: {cat['name']}")
        
        conn.commit()
        print("\n✓ Categories seeded successfully!")

if __name__ == "__main__":
    seed_categories()
