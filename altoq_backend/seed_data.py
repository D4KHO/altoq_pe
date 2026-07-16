import sys
import os
import random
from datetime import datetime, date, timedelta
from decimal import Decimal

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, Base, engine
from app.models.user import User
from app.models.store import Store
from app.models.product import Product
from app.models.category import Category
from app.models.order import Order
from app.models.delivery_code import DeliveryCode
from app.models.store_metric import StoreMetric
from app.utils.security import get_password_hash

# Datos para categorías
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

# Datos de tiendas ficticias y sus productos
STORE_TEMPLATES = [
    {
        "name": "Panadería El Trigal",
        "description": "Panes artesanales y pasteles hechos con amor",
        "email": "trigal@example.com",
        "owner": "Mariela Espinoza",
        "phone": "+51 987 654 321",
        "theme": "bakery",
        "ruc": "20123456789",
        "category_slug": "comida",
        "products": [
            {"name": "Torta de Tres Leches", "price": 45.00, "description": "Torta húmeda tradicional de tres leches decorada con merengue", "image": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=600&auto=format&fit=crop"},
            {"name": "Croissant de Mantequilla", "price": 4.50, "description": "Crujiente croissant de pura mantequilla recién horneado", "image": "https://images.unsplash.com/photo-1555507036-ab1f4038808a?w=600&auto=format&fit=crop"},
            {"name": "Pan Ciabatta rústico (x6)", "price": 6.00, "description": "Paquete de 6 panes ciabatta crujientes ideales para sandwiches", "image": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=600&auto=format&fit=crop"},
            {"name": "Empanada de Carne", "price": 7.50, "description": "Empanada rellena de carne picada sazonada al horno", "image": "https://images.unsplash.com/photo-1554995207-c18c203602cb?w=600&auto=format&fit=crop"}
        ]
    },
    {
        "name": "TechZone Perú",
        "description": "Lo último en gadgets, audio y accesorios de computación",
        "email": "techzone@example.com",
        "owner": "Carlos Huamán",
        "phone": "+51 954 123 456",
        "theme": "tech",
        "ruc": "20556677889",
        "category_slug": "electronica",
        "products": [
            {"name": "Audífonos Inalámbricos Bluetooth", "price": 129.90, "description": "Audífonos in-ear con cancelación de ruido y 24h de batería", "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&auto=format&fit=crop"},
            {"name": "Cargador Rápido GaN 65W", "price": 89.00, "description": "Cargador ultra compacto de pared con puertos USB-C y USB-A", "image": "https://images.unsplash.com/photo-1583863788434-e58a36330cf0?w=600&auto=format&fit=crop"},
            {"name": "Mouse Gamer Ergonómico RGB", "price": 75.00, "description": "Mouse óptico con hasta 7200 DPI y retroiluminación personalizable", "image": "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=600&auto=format&fit=crop"}
        ]
    },
    {
        "name": "Boutique Bella & Co",
        "description": "Ropa y calzado de última tendencia para damas y caballeros",
        "email": "bellaco@example.com",
        "owner": "Sandra Beltrán",
        "phone": "+51 991 882 773",
        "theme": "fashion",
        "ruc": "20998877665",
        "category_slug": "ropa-y-moda",
        "products": [
            {"name": "Casaca Denim Oversized", "price": 120.00, "description": "Casaca jean clásica estilo oversized para toda temporada", "image": "https://images.unsplash.com/photo-1576995853123-5a10305d93c0?w=600&auto=format&fit=crop"},
            {"name": "Zapatillas Urbanas Blancas", "price": 149.90, "description": "Zapatillas minimalistas de cuero sintético, cómodas y ligeras", "image": "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=600&auto=format&fit=crop"},
            {"name": "Lentes de Sol Polarizados", "price": 65.00, "description": "Lentes unisex con protección UV400 y montura de policarbonato", "image": "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=600&auto=format&fit=crop"}
        ]
    },
    {
        "name": "EcoHogar",
        "description": "Decoración sostenible y artículos funcionales para tu hogar",
        "email": "ecohogar@example.com",
        "owner": "Diego Benavides",
        "phone": "+51 922 333 444",
        "theme": "home",
        "ruc": "20776655443",
        "category_slug": "hogar-y-jardin",
        "products": [
            {"name": "Set de 3 Macetas de Cerámica", "price": 55.00, "description": "Macetas minimalistas con base de madera de bambú", "image": "https://images.unsplash.com/photo-1485955900006-10f4d324d411?w=600&auto=format&fit=crop"},
            {"name": "Lámpara de Escritorio Nórdica", "price": 95.00, "description": "Lámpara de madera y metal blanco con cabezal articulado", "image": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=600&auto=format&fit=crop"},
            {"name": "Cojines Decorativos Algodón (x2)", "price": 40.00, "description": "Par de fundas de cojín con textura geométrica moderna", "image": "https://images.unsplash.com/photo-1584100936595-c0654b55a2e2?w=600&auto=format&fit=crop"}
        ]
    },
    {
        "name": "Glossy Skincare",
        "description": "Productos de cuidado facial y maquillaje con ingredientes naturales",
        "email": "glossy@example.com",
        "owner": "Gabriela Paz",
        "phone": "+51 966 555 444",
        "theme": "default",
        "ruc": "20334422115",
        "category_slug": "salud-y-belleza",
        "products": [
            {"name": "Sérum Facial de Ácido Hialurónico", "price": 69.90, "description": "Hidratación profunda para todo tipo de piel, frasco de 30ml", "image": "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=600&auto=format&fit=crop"},
            {"name": "Protector Solar Gel FPS 50+", "price": 59.00, "description": "Efecto toque seco, protección alta contra rayos UVA/UVB", "image": "https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?w=600&auto=format&fit=crop"},
            {"name": "Bálsamo Labial Hidratante", "price": 15.00, "description": "Nutrición con aroma a frutos rojos y manteca de karité", "image": "https://images.unsplash.com/photo-1512496015851-a90fb38ba796?w=600&auto=format&fit=crop"}
        ]
    },
    {
        "name": "Alto Deporte",
        "description": "Artículos de entrenamiento, pesas, yoga y más",
        "email": "altodeporte@example.com",
        "owner": "Jorge Mendoza",
        "phone": "+51 988 777 666",
        "theme": "default",
        "ruc": "20448855221",
        "category_slug": "deportes",
        "products": [
            {"name": "Mat de Yoga Antideslizante", "price": 49.00, "description": "Mat de TPE ecológico de 6mm con líneas de alineación", "image": "https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=600&auto=format&fit=crop"},
            {"name": "Par de Mancuernas de Neopreno 3kg", "price": 39.90, "description": "Mancuernas hexagonales antideslizantes para tonificación", "image": "https://images.unsplash.com/photo-1583454110551-21f2fa2afe61?w=600&auto=format&fit=crop"},
            {"name": "Tomatodo Deportivo Motivacional 1L", "price": 25.00, "description": "Tomatodo de Tritan libre de BPA con sorbete y marcas de agua", "image": "https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=600&auto=format&fit=crop"}
        ]
    },
    {
        "name": "Juguetería Pekes",
        "description": "Juegos didácticos y entretenimiento sano para los más chicos",
        "email": "pekes@example.com",
        "owner": "Natalia Rivas",
        "phone": "+51 944 332 211",
        "theme": "default",
        "ruc": "20885544112",
        "category_slug": "juguetes",
        "products": [
            {"name": "Bloques de Construcción de Madera", "price": 55.00, "description": "Set de 50 bloques de madera de colores con bolsa de almacenamiento", "image": "https://images.unsplash.com/photo-1515488042361-404e9250afef?w=600&auto=format&fit=crop"},
            {"name": "Puzle Infantil Mapamundi", "price": 38.00, "description": "Rompecabezas de cartón grueso de 60 piezas sobre geografía", "image": "https://images.unsplash.com/photo-1587654780291-39c9404d746b?w=600&auto=format&fit=crop"},
            {"name": "Juego de Mesa 'Torre de Madera'", "price": 25.00, "description": "Juego de equilibrio clásico de 54 bloques estilo Jenga", "image": "https://images.unsplash.com/photo-1610890716171-6b1bb98ffd09?w=600&auto=format&fit=crop"}
        ]
    },
    {
        "name": "Librería Estudiante",
        "description": "Textos escolares, novelas, mangas y papelería fina",
        "email": "estudiante@example.com",
        "owner": "Víctor Cáceres",
        "phone": "+51 912 345 678",
        "theme": "default",
        "ruc": "20551122334",
        "category_slug": "libros",
        "products": [
            {"name": "Set de Cuadernos Bullet Journal", "price": 35.00, "description": "Pack de 2 cuadernos de hojas punteadas de 100g para planner", "image": "https://images.unsplash.com/photo-1531346878377-a5be20888e57?w=600&auto=format&fit=crop"},
            {"name": "Novela Best Seller del Año", "price": 59.90, "description": "Edición tapa blanda de la novela de drama y misterio más leída", "image": "https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=600&auto=format&fit=crop"},
            {"name": "Lapiceros Gel de Colores (x12)", "price": 22.00, "description": "Estuche con 12 bolígrafos gel de punta fina colores vibrantes", "image": "https://images.unsplash.com/photo-1513542789411-b6a5d4f31634?w=600&auto=format&fit=crop"}
        ]
    },
    {
        "name": "Pizzería Nápoles",
        "description": "Auténticas pizzas napolitanas al horno de piedra",
        "email": "napoles@example.com",
        "owner": "Fabrizio Rossi",
        "phone": "+51 933 666 999",
        "theme": "food",
        "ruc": "20336699118",
        "category_slug": "comida",
        "products": [
            {"name": "Pizza Margarita Familiar", "price": 39.00, "description": "Masa delgada, pomodoro, queso mozzarella fresca y albahaca", "image": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=600&auto=format&fit=crop"},
            {"name": "Pizza Pepperoni Especial", "price": 44.00, "description": "Con abundante pepperoni, queso mozzarella y orégano", "image": "https://images.unsplash.com/photo-1628840042765-356cda07504e?w=600&auto=format&fit=crop"},
            {"name": "Pan al Ajo Simple (4 unidades)", "price": 12.00, "description": "Baguette tostada con mantequilla de ajo y finas hierbas", "image": "https://images.unsplash.com/photo-1573140247632-f8fd74997d5c?w=600&auto=format&fit=crop"}
        ]
    },
    {
        "name": "La Casa del Postre",
        "description": "Dulces tradicionales, muffins, cheesecakes y helados",
        "email": "casapostre@example.com",
        "owner": "Rosa María Ortiz",
        "phone": "+51 966 333 111",
        "theme": "bakery",
        "ruc": "20119988224",
        "category_slug": "comida",
        "products": [
            {"name": "Cheesecake de Fresa", "price": 48.00, "description": "Clásico cheesecake frío con salsa de fresas naturales", "image": "https://images.unsplash.com/photo-1524351199679-46cddf530c04?w=600&auto=format&fit=crop"},
            {"name": "Caja de Muffins Surtidos (x6)", "price": 24.00, "description": "Contiene 2 muffins de chocolate, 2 de arándanos y 2 de plátano", "image": "https://images.unsplash.com/photo-1587314168485-3236d6710814?w=600&auto=format&fit=crop"},
            {"name": "Suspiro a la Limeña (Pote)", "price": 9.50, "description": "Postre limeño dulce tradicional cubierto de merengue al oporto", "image": "https://images.unsplash.com/photo-1551024506-0bccd828d307?w=600&auto=format&fit=crop"}
        ]
    }
]

def main():
    print("=" * 60)
    print("      SEMILLERO DE DATOS (SEEDER) - MARKETPLACE ALTOQ")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # 1. Asegurar categorías del sistema
        print("\n[1/5] Verificando categorías...")
        category_map = {}
        for cat_data in CATEGORIES:
            cat = db.query(Category).filter(Category.slug == cat_data["slug"]).first()
            if not cat:
                cat = Category(**cat_data)
                db.add(cat)
                db.commit()
                db.refresh(cat)
                print(f"  + Categoría creada: {cat.name}")
            else:
                cat.description = cat_data["description"]
                cat.icon = cat_data["icon"]
                db.commit()
                print(f"  ~ Categoría verificada: {cat.name}")
            category_map[cat_data["slug"]] = cat.id

        # 2. Crear un comprador genérico para las compras ficticias
        print("\n[2/5] Creando usuarios compradores...")
        buyer_user = db.query(User).filter(User.email == "buyer_demo@example.com").first()
        if not buyer_user:
            buyer_user = User(
                email="buyer_demo@example.com",
                name="Juan Perez (Demo Compras)",
                password=get_password_hash("password123"),
                address="Av. Larco 456, Miraflores, Lima",
                phone="+51 988 888 888",
                role="buyer"
            )
            db.add(buyer_user)
            db.commit()
            db.refresh(buyer_user)
            print("  + Usuario comprador demo creado.")
        else:
            print("  ~ Usuario comprador demo ya existe.")

        # 3. Crear tiendas y vendedores
        print("\n[3/5] Creando vendedores, tiendas y productos...")
        stores_created = []
        for i, st in enumerate(STORE_TEMPLATES, 1):
            # Buscar o crear usuario vendedor
            seller_email = f"vendedor{i}@example.com"
            seller = db.query(User).filter(User.email == seller_email).first()
            if not seller:
                seller = User(
                    email=seller_email,
                    name=st["owner"],
                    password=get_password_hash("password123"),
                    phone=st["phone"],
                    address="Calle Comercio " + str(100 + i) + ", Lima",
                    role="seller"
                )
                db.add(seller)
                db.commit()
                db.refresh(seller)
                print(f"  + Vendedor creado: {st['owner']} ({seller_email})")

            # Buscar o crear tienda
            store = db.query(Store).filter(Store.email == st["email"]).first()
            if not store:
                store = Store(
                    name=st["name"],
                    email=st["email"],
                    owner_name=st["owner"],
                    phone=st["phone"],
                    description=st["description"],
                    ruc=st["ruc"],
                    theme=st["theme"],
                    status="active",
                    user_id=seller.id
                )
                db.add(store)
                db.commit()
                db.refresh(store)
                print(f"    -> Tienda creada: {st['name']}")
            else:
                store.status = "active"
                store.user_id = seller.id
                db.commit()
                print(f"    ~ Tienda verificada: {st['name']}")
            
            stores_created.append(store)

            # Cargar productos
            cat_id = category_map.get(st["category_slug"])
            for prod_data in st["products"]:
                prod = db.query(Product).filter(Product.name == prod_data["name"], Product.store_id == store.id).first()
                if not prod:
                    prod = Product(
                        name=prod_data["name"],
                        price=prod_data["price"],
                        description=prod_data["description"],
                        image=prod_data["image"],
                        category=st["category_slug"],
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
                    print(f"       * Producto creado: {prod.name}")

        # 4. Crear órdenes e historial de ventas
        print("\n[4/5] Creando órdenes y ventas históricas para las tiendas...")
        
        # Obtener todos los productos para cruzarlos
        all_products = db.query(Product).all()
        
        # Limpiar órdenes demo anteriores para evitar duplicados infinitos
        demo_order_ids = [o.id for o in db.query(Order).filter(Order.shipping_address.like("%(Seeder Demo)%")).all()]
        if demo_order_ids:
            db.query(DeliveryCode).filter(DeliveryCode.order_id.in_(demo_order_ids)).delete(synchronize_session=False)
        demo_orders_count = db.query(Order).filter(Order.shipping_address.like("%(Seeder Demo)%")).delete(synchronize_session=False)
        db.commit()
        if demo_orders_count > 0:
            print(f"  ~ Eliminadas {demo_orders_count} ordenes del semillero anterior.")

        for store in stores_created:
            store_prods = [p for p in all_products if p.store_id == store.id]
            if not store_prods:
                continue

            # Crear entre 3 y 6 órdenes por tienda en fechas variables de los últimos 14 días
            num_orders = random.randint(3, 6)
            for _ in range(num_orders):
                chosen_prods = random.sample(store_prods, k=min(len(store_prods), random.randint(1, 2)))
                order_items_json = []
                total = 0.0
                
                for cp in chosen_prods:
                    qty = random.randint(1, 3)
                    price = cp.price
                    total += price * qty
                    order_items_json.append({
                        "productId": cp.id,
                        "quantity": qty,
                        "price": price,
                        "name": cp.name
                    })

                order_date = datetime.utcnow() - timedelta(days=random.randint(0, 14), hours=random.randint(1, 23))
                
                new_order = Order(
                    user_id=buyer_user.id,
                    products=order_items_json,
                    total_amount=total,
                    status="delivered",
                    created_at=order_date,
                    updated_at=order_date + timedelta(hours=random.randint(1, 4)),
                    shipping_address="Calle Comprador " + str(random.randint(100, 999)) + ", Lima (Seeder Demo)",
                    contact_phone="+51 911 222 333",
                    shipping_latitude=-12.046374 + random.uniform(-0.05, 0.05),
                    shipping_longitude=-77.042793 + random.uniform(-0.05, 0.05),
                    delivery_latitude=-12.046374 + random.uniform(-0.05, 0.05),
                    delivery_longitude=-77.042793 + random.uniform(-0.05, 0.05),
                    delivery_status="delivered"
                )
                db.add(new_order)
                db.commit()
                db.refresh(new_order)

                char_pool = "ABCDEFGHJKLMNOPQRSTUVWXYZ23456789"
                delivery_code_str = "".join(random.choice(char_pool) for _ in range(6))
                
                delivery_code = DeliveryCode(
                    order_id=new_order.id,
                    code=delivery_code_str,
                    is_used=True,
                    created_at=order_date,
                    expires_at=order_date + timedelta(days=30),
                    used_at=new_order.updated_at
                )
                db.add(delivery_code)
                db.commit()

            print(f"    -> Creadas {num_orders} órdenes entregadas para la tienda: {store.name}")

        # 5. Generar historial de métricas para los últimos 14 días
        print("\n[5/5] Generando historial de métricas diarias (14 días atrás)...")
        
        # Eliminar métricas anteriores para recrear limpio
        db.query(StoreMetric).delete()
        db.commit()

        hoy = date.today()
        for store in stores_created:
            prod_count = db.query(Product).filter(Product.store_id == store.id).count()
            
            store_prods = db.query(Product).filter(Product.store_id == store.id).all()
            store_prod_ids = {p.id for p in store_prods}

            orders_all = db.query(Order).filter(Order.shipping_address.like("%(Seeder Demo)%")).all()
            
            date_sales = {}
            for o in orders_all:
                order_date_only = o.created_at.date()
                store_items_in_order = [item for item in o.products if item.get("productId") in store_prod_ids]
                if not store_items_in_order:
                    continue
                
                subtotal = sum(item["price"] * item["quantity"] for item in store_items_in_order)
                qty_delivered = 1
                
                if order_date_only not in date_sales:
                    date_sales[order_date_only] = {"revenue": Decimal("0.0"), "orders": 0}
                
                date_sales[order_date_only]["revenue"] += Decimal(str(subtotal))
                date_sales[order_date_only]["orders"] += qty_delivered

            for d in range(14):
                fecha_metrica = hoy - timedelta(days=d)
                sales_today = date_sales.get(fecha_metrica, {"revenue": Decimal("0.0"), "orders": 0})
                
                base_visits = random.randint(15, 60)
                if sales_today["orders"] > 0:
                    base_visits += sales_today["orders"] * random.randint(10, 30)
                
                chats = random.randint(1, 8)
                if sales_today["orders"] > 0:
                    chats += sales_today["orders"] * random.randint(1, 3)

                metric = StoreMetric(
                    store_id=store.id,
                    date=fecha_metrica,
                    visits=base_visits,
                    products_published=prod_count,
                    orders_delivered=sales_today["orders"],
                    revenue=sales_today["revenue"],
                    chat_sessions=chats,
                    template_usage=random.randint(0, 4),
                    new_users=random.randint(1, 6) if sales_today["orders"] > 0 else random.randint(0, 2),
                    avg_rating=round(random.uniform(4.2, 4.8), 1),
                    created_at=datetime.combine(fecha_metrica, datetime.min.time()),
                    updated_at=datetime.combine(fecha_metrica, datetime.max.time())
                )
                db.add(metric)

        db.commit()
        print("  [OK] Historial de metras completado para todas las tiendas.")

        print("\n" + "=" * 60)
        print("  [OK] ¡Se ha sembrado la Base de Datos exitosamente!")
        print("Detalles:")
        print(" - 10 Tiendas activas con disenos unicos.")
        print(" - Mas de 30 productos con imagenes y categorias.")
        print(" - Cuentas de vendedor asociadas (vendedor1@example.com a vendedor10@example.com - Clave: password123)")
        print(" - Compras ficticias y entregas registradas.")
        print(" - Metricas del vendedor rellenadas para visualizacion de graficos.")
        print("=" * 60)
        
    except Exception as e:
        db.rollback()
        print(f"\n[ERROR] Error al sembrar los datos: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()
