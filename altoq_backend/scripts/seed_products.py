from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.product import Product
import random

def seed_products():
    db: Session = SessionLocal()

    products_data = [
        {
            "name": "Smartphone X Pro",
            "description": "Último modelo con cámara de alta resolución y batería de larga duración. Ideal para fotografía y juegos.",
            "price": 2599.99,
            "category": "Tecnología",
            "image": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=500&auto=format&fit=crop&q=60",
            "stock": 50,
            "rating": 4.8,
            "rating_count": 340,
            "specifications": {
                "Pantalla": "6.7 pulgadas AMOLED",
                "Procesador": "Snapdragon 8 Gen 2",
                "RAM": "12 GB",
                "Almacenamiento": "256 GB",
                "Cámara": "108 MP + 12 MP + 10 MP",
                "Batería": "5000 mAh",
                "Sistema Operativo": "Android 13"
            }
        },
        {
            "name": "Laptop UltraThin",
            "description": "Portátil ligera y potente para profesionales en movimiento. Procesador i7, 16GB RAM.",
            "price": 3499.00,
            "category": "Computación",
            "image": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=500&auto=format&fit=crop&q=60",
            "stock": 25,
            "rating": 4.6,
            "rating_count": 120
        },
        {
            "name": "Auriculares NoiseCancelling",
            "description": "Sonido inmersivo con cancelación de ruido activa. Perfectos para viajes y trabajo.",
            "price": 399.50,
            "category": "Audio",
            "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&auto=format&fit=crop&q=60",
            "stock": 100,
            "rating": 4.5,
            "rating_count": 850
        },
        {
            "name": "Smartwatch Fitness",
            "description": "Monitorea tu salud y actividad física. Resistente al agua y con GPS integrado.",
            "price": 199.99,
            "category": "Wearables",
            "image": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500&auto=format&fit=crop&q=60",
            "stock": 75,
            "rating": 4.2,
            "rating_count": 210
        },
        {
            "name": "Cámara DSLR Pro",
            "description": "Captura momentos inolvidables con calidad profesional. Incluye lente 18-55mm.",
            "price": 1850.00,
            "category": "Fotografía",
            "image": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=500&auto=format&fit=crop&q=60",
            "stock": 15,
            "rating": 4.9,
            "rating_count": 45
        },
        {
            "name": "Zapatillas Running Velocidad",
            "description": "Diseñadas para corredores exigentes. Amortiguación superior y peso ligero.",
            "price": 289.90,
            "category": "Deportes",
            "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500&auto=format&fit=crop&q=60",
            "stock": 60,
            "rating": 4.7,
            "rating_count": 530
        },
        {
            "name": "Mochila Impermeable",
            "description": "Protege tus pertenencias en cualquier clima. Múltiples compartimentos y diseño ergonómico.",
            "price": 120.00,
            "category": "Accesorios",
            "image": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=500&auto=format&fit=crop&q=60",
            "stock": 200,
            "rating": 4.3,
            "rating_count": 150
        },
        {
            "name": "Cafetera Espresso",
            "description": "Disfruta del café de calidad barista en casa. Fácil de usar y limpiar.",
            "price": 450.00,
            "category": "Hogar",
            "image": "https://images.unsplash.com/photo-1520031607889-25372d829141?w=500&auto=format&fit=crop&q=60",
            "stock": 40,
            "rating": 4.4,
            "rating_count": 89
        },
        {
            "name": "Silla Ergonómica Oficina",
            "description": "Comodidad para largas jornadas de trabajo. Soporte lumbar ajustable.",
            "price": 599.00,
            "category": "Muebles",
            "image": "https://images.unsplash.com/photo-1505843490538-5133c6c7d0e1?w=500&auto=format&fit=crop&q=60",
            "stock": 30,
            "rating": 4.1,
            "rating_count": 65
        },
        {
            "name": "Monitor 4K UltraHD",
            "description": "Colores vibrantes y detalles nítidos. Ideal para diseñadores y gamers.",
            "price": 1100.00,
            "category": "Computación",
            "image": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=500&auto=format&fit=crop&q=60",
            "stock": 45,
            "rating": 4.8,
            "rating_count": 190
        }
    ]

    print("Iniciando inserción de productos...")
    
    for p_data in products_data:
        # Verificar si ya existe para no duplicar (opcional, por nombre)
        existing = db.query(Product).filter(Product.name == p_data["name"]).first()
        if not existing:
            product = Product(**p_data)
            db.add(product)
            print(f"Agregando: {p_data['name']}")
        else:
            print(f"Ya existe: {p_data['name']}")
    
    db.commit()
    db.close()
    print("Carga de productos completada.")

if __name__ == "__main__":
    seed_products()
