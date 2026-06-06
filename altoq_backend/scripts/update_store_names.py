from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.product import Product

def update_store_names():
    db: Session = SessionLocal()
    
    # Mapeo simple de marcas por palabras clave en el nombre o categoría
    store_mapping = {
        "Smartphone": "Samsung Store",
        "Laptop": "TechWorld",
        "Auriculares": "AudioPro",
        "Smartwatch": "Garmin Center",
        "Cámara": "Nikon Official",
        "Zapatillas": "Nike",
        "Mochila": "Samsonite",
        "Cafetera": "Oster",
        "Silla": "ErgoOffice",
        "Monitor": "LG Display"
    }

    products = db.query(Product).all()
    print(f"Encontrados {len(products)} productos para actualizar.")

    for product in products:
        store = "Tienda Genérica"
        for key, value in store_mapping.items():
            if key in product.name:
                store = value
                break
        
        product.store_name = store
        print(f"Actualizando '{product.name}' -> Tienda: {store}")

    db.commit()
    db.close()
    print("Actualización de tiendas completada.")

if __name__ == "__main__":
    update_store_names()
