from sqlalchemy.orm import Session
from app.models.store import Store
from app.models.user import User

STORES_DATA = [
    {
        "name": "Panadería El Trigal",
        "description": "Panes artesanales y pasteles hechos con amor",
        "email": "trigal@example.com",
        "owner": "Mariela Espinoza",
        "phone": "+51 987 654 321",
        "theme": "bakery",
        "ruc": "20123456789",
        "seller_email": "vendedor1@example.com"
    },
    {
        "name": "TechZone Perú",
        "description": "Lo último en gadgets, audio y accesorios de computación",
        "email": "techzone@example.com",
        "owner": "Carlos Huamán",
        "phone": "+51 954 123 456",
        "theme": "tech",
        "ruc": "20556677889",
        "seller_email": "vendedor2@example.com"
    },
    {
        "name": "Boutique Bella & Co",
        "description": "Ropa y calzado de última tendencia para damas y caballeros",
        "email": "bellaco@example.com",
        "owner": "Sandra Beltrán",
        "phone": "+51 991 882 773",
        "theme": "fashion",
        "ruc": "20998877665",
        "seller_email": "vendedor3@example.com"
    },
    {
        "name": "EcoHogar",
        "description": "Decoración sostenible y artículos funcionales para tu hogar",
        "email": "ecohogar@example.com",
        "owner": "Diego Benavides",
        "phone": "+51 922 333 444",
        "theme": "home",
        "ruc": "20776655443",
        "seller_email": "vendedor4@example.com"
    },
    {
        "name": "Glossy Skincare",
        "description": "Productos de cuidado facial y maquillaje con ingredientes naturales",
        "email": "glossy@example.com",
        "owner": "Gabriela Paz",
        "phone": "+51 966 555 444",
        "theme": "default",
        "ruc": "20334422115",
        "seller_email": "vendedor5@example.com"
    },
    {
        "name": "Alto Deporte",
        "description": "Artículos de entrenamiento, pesas, yoga y más",
        "email": "altodeporte@example.com",
        "owner": "Jorge Mendoza",
        "phone": "+51 988 777 666",
        "theme": "default",
        "ruc": "20448855221",
        "seller_email": "vendedor6@example.com"
    },
    {
        "name": "Juguetería Pekes",
        "description": "Juegos didácticos y entretenimiento sano para los más chicos",
        "email": "pekes@example.com",
        "owner": "Natalia Rivas",
        "phone": "+51 944 332 211",
        "theme": "default",
        "ruc": "20885544112",
        "seller_email": "vendedor7@example.com"
    },
    {
        "name": "Librería Estudiante",
        "description": "Textos escolares, novelas, mangas y papelería fina",
        "email": "estudiante@example.com",
        "owner": "Víctor Cáceres",
        "phone": "+51 912 345 678",
        "theme": "default",
        "ruc": "20551122334",
        "seller_email": "vendedor8@example.com"
    },
    {
        "name": "Pizzería Nápoles",
        "description": "Auténticas pizzas napolitanas al horno de piedra",
        "email": "napoles@example.com",
        "owner": "Fabrizio Rossi",
        "phone": "+51 933 666 999",
        "theme": "food",
        "ruc": "20336699118",
        "seller_email": "vendedor9@example.com"
    },
    {
        "name": "La Casa del Postre",
        "description": "Dulces tradicionales, muffins, cheesecakes y helados",
        "email": "casapostre@example.com",
        "owner": "Rosa María Ortiz",
        "phone": "+51 966 333 111",
        "theme": "bakery",
        "ruc": "20119988224",
        "seller_email": "vendedor10@example.com"
    }
]

def run(db: Session):
    print("\n[3/5] Sembrando tiendas...")
    for st in STORES_DATA:
        seller = db.query(User).filter(User.email == st["seller_email"]).first()
        if not seller:
            print(f"  [ERROR] No se pudo crear la tienda '{st['name']}' porque el vendedor '{st['seller_email']}' no existe.")
            continue
            
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
            print(f"  + Tienda creada: {st['name']} (Vendedor: {st['owner']})")
        else:
            store.status = "active"
            store.user_id = seller.id
            db.commit()
            print(f"  ~ Tienda verificada: {st['name']}")
