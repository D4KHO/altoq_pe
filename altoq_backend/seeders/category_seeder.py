from sqlalchemy.orm import Session
from app.models.category import Category

CATEGORIES = [
    {"name": "Ropa y Moda", "slug": "ropa-y-moda", "description": "Prendas de vestir, calzado y accesorios", "icon": "👕"},
    {"name": "Electrónica", "slug": "electronica", "description": "Celulares, computadoras y gadgets", "icon": "📱"},
    {"name": "Hogar y Jardín", "slug": "hogar-y-jardin", "description": "Muebles, decoración y herramientas", "icon": "🏠"},
    {"name": "Salud y Belleza", "slug": "salud-y-belleza", "description": "Cuidado personal, maquillaje y perfumes", "icon": "💄"},
    {"name": "Deportes", "slug": "deportes", "description": "Ropa deportiva, bicicletas y accesorios", "icon": "⚽"},
    {"name": "Juguetes", "slug": "juguetes", "description": "Juguetes para niños y juegos de mesa", "icon": "🧸"},
    {"name": "Libros", "slug": "libros", "description": "Novelas, textos académicos y cómics", "icon": "📚"},
    {"name": "Comida", "slug": "comida", "description": "Alimentos, postres y restaurantes", "icon": "🍔"}
]

def run(db: Session):
    print("\n[1/5] Sembrando categorías...")
    for cat_data in CATEGORIES:
        cat = db.query(Category).filter(Category.slug == cat_data["slug"]).first()
        if not cat:
            cat = Category(**cat_data)
            db.add(cat)
            db.commit()
            print(f"  + Categoría creada: {cat.name}")
        else:
            cat.description = cat_data["description"]
            cat.icon = cat_data["icon"]
            db.commit()
            print(f"  ~ Categoría verificada: {cat.name}")
