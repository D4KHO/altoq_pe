import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.product import Product
from app.models.store import Store
from app.models.category import Category

PRODUCTS_DATA = [
    # Panadería El Trigal
    {"store_email": "trigal@example.com", "category_slug": "comida", "name": "Torta de Tres Leches", "price": 45.00, "description": "Torta húmeda tradicional de tres leches decorada con merengue", "image": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=600"},
    {"store_email": "trigal@example.com", "category_slug": "comida", "name": "Croissant de Mantequilla", "price": 4.50, "description": "Crujiente croissant de pura mantequilla recién horneado", "image": "https://images.unsplash.com/photo-1555507036-ab1f4038808a?w=600"},
    {"store_email": "trigal@example.com", "category_slug": "comida", "name": "Pan Ciabatta rústico (x6)", "price": 6.00, "description": "Paquete de 6 panes ciabatta crujientes ideales para sandwiches", "image": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=600"},
    {"store_email": "trigal@example.com", "category_slug": "comida", "name": "Empanada de Carne", "price": 7.50, "description": "Empanada rellena de carne picada sazonada al horno", "image": "https://images.unsplash.com/photo-1554995207-c18c203602cb?w=600"},

    # TechZone Perú
    {"store_email": "techzone@example.com", "category_slug": "electronica", "name": "Audífonos Inalámbricos Bluetooth", "price": 129.90, "description": "Audífonos in-ear con cancelación de ruido y 24h de batería", "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600"},
    {"store_email": "techzone@example.com", "category_slug": "electronica", "name": "Cargador Rápido GaN 65W", "price": 89.00, "description": "Cargador ultra compacto de pared con puertos USB-C y USB-A", "image": "https://images.unsplash.com/photo-1583863788434-e58a36330cf0?w=600"},
    {"store_email": "techzone@example.com", "category_slug": "electronica", "name": "Mouse Gamer Ergonómico RGB", "price": 75.00, "description": "Mouse óptico con hasta 7200 DPI y retroiluminación personalizable", "image": "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=600"},

    # Boutique Bella & Co
    {"store_email": "bellaco@example.com", "category_slug": "ropa-y-moda", "name": "Casaca Denim Oversized", "price": 120.00, "description": "Casaca jean clásica estilo oversized para toda temporada", "image": "https://images.unsplash.com/photo-1576995853123-5a10305d93c0?w=600"},
    {"store_email": "bellaco@example.com", "category_slug": "ropa-y-moda", "name": "Zapatillas Urbanas Blancas", "price": 149.90, "description": "Zapatillas minimalistas de cuero sintético, cómodas y ligeras", "image": "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=600"},
    {"store_email": "bellaco@example.com", "category_slug": "ropa-y-moda", "name": "Lentes de Sol Polarizados", "price": 65.00, "description": "Lentes unisex con protección UV400 y montura de policarbonato", "image": "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=600"},

    # EcoHogar
    {"store_email": "ecohogar@example.com", "category_slug": "hogar-y-jardin", "name": "Set de 3 Macetas de Cerámica", "price": 55.00, "description": "Macetas minimalistas con base de madera de bambú", "image": "https://images.unsplash.com/photo-1485955900006-10f4d324d411?w=600"},
    {"store_email": "ecohogar@example.com", "category_slug": "hogar-y-jardin", "name": "Lámpara de Escritorio Nórdica", "price": 95.00, "description": "Lámpara de madera y metal blanco con cabezal articulado", "image": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=600"},
    {"store_email": "ecohogar@example.com", "category_slug": "hogar-y-jardin", "name": "Cojines Decorativos Algodón (x2)", "price": 40.00, "description": "Par de fundas de cojín con textura geométrica moderna", "image": "https://images.unsplash.com/photo-1584100936595-c0654b55a2e2?w=600"},

    # Glossy Skincare
    {"store_email": "glossy@example.com", "category_slug": "salud-y-belleza", "name": "Sérum Facial de Ácido Hialurónico", "price": 69.90, "description": "Hidratación profunda para todo tipo de piel, frasco de 30ml", "image": "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=600"},
    {"store_email": "glossy@example.com", "category_slug": "salud-y-belleza", "name": "Protector Solar Gel FPS 50+", "price": 59.00, "description": "Efecto toque seco, protección alta contra rayos UVA/UVB", "image": "https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?w=600"},
    {"store_email": "glossy@example.com", "category_slug": "salud-y-belleza", "name": "Bálsamo Labial Hidratante", "price": 15.00, "description": "Nutrición con aroma a frutos rojos y manteca de karité", "image": "https://images.unsplash.com/photo-1512496015851-a90fb38ba796?w=600"},

    # Alto Deporte
    {"store_email": "altodeporte@example.com", "category_slug": "deportes", "name": "Mat de Yoga Antideslizante", "price": 49.00, "description": "Mat de TPE ecológico de 6mm con líneas de alineación", "image": "https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=600"},
    {"store_email": "altodeporte@example.com", "category_slug": "deportes", "name": "Par de Mancuernas de Neopreno 3kg", "price": 39.90, "description": "Mancuernas hexagonales antideslizantes para tonificación", "image": "https://images.unsplash.com/photo-1583454110551-21f2fa2afe61?w=600"},
    {"store_email": "altodeporte@example.com", "category_slug": "deportes", "name": "Tomatodo Deportivo Motivacional 1L", "price": 25.00, "description": "Tomatodo de Tritan libre de BPA con sorbete y marcas de agua", "image": "https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=600"},

    # Juguetería Pekes
    {"store_email": "pekes@example.com", "category_slug": "juguetes", "name": "Bloques de Construcción de Madera", "price": 55.00, "description": "Set de 50 bloques de madera de colores con bolsa de almacenamiento", "image": "https://images.unsplash.com/photo-1515488042361-404e9250afef?w=600"},
    {"store_email": "pekes@example.com", "category_slug": "juguetes", "name": "Puzle Infantil Mapamundi", "price": 38.00, "description": "Rompecabezas de cartón grueso de 60 piezas sobre geografía", "image": "https://images.unsplash.com/photo-1587654780291-39c9404d746b?w=600"},
    {"store_email": "pekes@example.com", "category_slug": "juguetes", "name": "Juego de Mesa 'Torre de Madera'", "price": 25.00, "description": "Juego de equilibrio clásico de 54 bloques estilo Jenga", "image": "https://images.unsplash.com/photo-1610890716171-6b1bb98ffd09?w=600"},

    # Librería Estudiante
    {"store_email": "estudiante@example.com", "category_slug": "libros", "name": "Set de Cuadernos Bullet Journal", "price": 35.00, "description": "Pack de 2 cuadernos de hojas punteadas de 100g para planner", "image": "https://images.unsplash.com/photo-1531346878377-a5be20888e57?w=600"},
    {"store_email": "estudiante@example.com", "category_slug": "libros", "name": "Novela Best Seller del Año", "price": 59.90, "description": "Edición tapa blanda de la novela de drama y misterio más leída", "image": "https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=600"},
    {"store_email": "estudiante@example.com", "category_slug": "libros", "name": "Lapiceros Gel de Colores (x12)", "price": 22.00, "description": "Estuche con 12 bolígrafos gel de punta fina colores vibrantes", "image": "https://images.unsplash.com/photo-1513542789411-b6a5d4f31634?w=600"},

    # Pizzería Nápoles
    {"store_email": "napoles@example.com", "category_slug": "comida", "name": "Pizza Margarita Familiar", "price": 39.00, "description": "Masa delgada, pomodoro, queso mozzarella fresca y albahaca", "image": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=600"},
    {"store_email": "napoles@example.com", "category_slug": "comida", "name": "Pizza Pepperoni Especial", "price": 44.00, "description": "Con abundante pepperoni, queso mozzarella y orégano", "image": "https://images.unsplash.com/photo-1628840042765-356cda07504e?w=600"},
    {"store_email": "napoles@example.com", "category_slug": "comida", "name": "Pan al Ajo Simple (4 unidades)", "price": 12.00, "description": "Baguette tostada con mantequilla de ajo y finas hierbas", "image": "https://images.unsplash.com/photo-1573140247632-f8fd74997d5c?w=600"},

    # La Casa del Postre
    {"store_email": "casapostre@example.com", "category_slug": "comida", "name": "Cheesecake de Fresa", "price": 48.00, "description": "Clásico cheesecake frío con salsa de fresas naturales", "image": "https://images.unsplash.com/photo-1524351199679-46cddf530c04?w=600"},
    {"store_email": "casapostre@example.com", "category_slug": "comida", "name": "Caja de Muffins Surtidos (x6)", "price": 24.00, "description": "Contiene 2 muffins de chocolate, 2 de arándanos y 2 de plátano", "image": "https://images.unsplash.com/photo-1587314168485-3236d6710814?w=600"},
    {"store_email": "casapostre@example.com", "category_slug": "comida", "name": "Suspiro a la Limeña (Pote)", "price": 9.50, "description": "Postre limeño dulce tradicional cubierto de merengue al oporto", "image": "https://images.unsplash.com/photo-1551024506-0bccd828d307?w=600"}
]

def run(db: Session):
    print("\n[4/5] Sembrando productos...")
    for p_data in PRODUCTS_DATA:
        # Buscar tienda asociada
        store = db.query(Store).filter(Store.email == p_data["store_email"]).first()
        if not store:
            print(f"  [ERROR] No se pudo crear el producto '{p_data['name']}' porque la tienda '{p_data['store_email']}' no existe.")
            continue
            
        # Buscar categoría asociada
        cat = db.query(Category).filter(Category.slug == p_data["category_slug"]).first()
        cat_id = cat.id if cat else None
        
        prod = db.query(Product).filter(Product.name == p_data["name"], Product.store_id == store.id).first()
        if not prod:
            prod = Product(
                name=p_data["name"],
                price=p_data["price"],
                description=p_data["description"],
                image=p_data["image"],
                category=p_data["category_slug"],
                category_id=cat_id,
                store_id=store.id,
                store_name=store.name,
                stock=random.randint(10, 50),
                rating=round(random.uniform(4.0, 5.0), 1),
                rating_count=random.randint(2, 15),
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30))
            )
            db.add(prod)
            db.commit()
            print(f"  + Producto creado: {prod.name} (Tienda: {store.name})")
        else:
            print(f"  ~ Producto ya existe: {prod.name} (Tienda: {store.name})")
