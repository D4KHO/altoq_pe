import sys
import os
import random
from datetime import datetime, date, timedelta
from decimal import Decimal

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import func
from app.database import SessionLocal, Base, engine
from app.models.user import User
from app.models.store import Store
from app.models.product import Product
from app.models.category import Category
from app.models.order import Order
from app.models.delivery_code import DeliveryCode
from app.models.store_metric import StoreMetric
from app.models.review import Review
from app.utils.security import get_password_hash

# 1. Definición de Categorías de Retail Físico (Excluye Comida)
CATEGORIES = [
    {"name": "Ropa y Moda", "slug": "ropa-y-moda", "description": "Prendas de vestir, calzado y accesorios de última moda", "icon": "👕"},
    {"name": "Electrónica", "slug": "electronica", "description": "Celulares, laptops, audífonos y gadgets de última generación", "icon": "📱"},
    {"name": "Hogar y Jardín", "slug": "hogar-y-jardin", "description": "Muebles, decoración y herramientas para tu hogar", "icon": "🏠"},
    {"name": "Salud y Belleza", "slug": "salud-y-belleza", "description": "Cuidado facial, personal, maquillaje y perfumes", "icon": "💄"},
    {"name": "Deportes", "slug": "deportes", "description": "Ropa deportiva, calzado y accesorios de entrenamiento", "icon": "⚽"},
    {"name": "Juguetes", "slug": "juguetes", "description": "Juguetes educativos, interactivos y juegos de mesa", "icon": "🧸"},
    {"name": "Libros", "slug": "libros", "description": "Novelas, literatura infantil y artículos de papelería", "icon": "📚"}
]

# 2. Definición de Tiendas y Productos (Sin Comida, con imágenes reales de E-commerce)
STORE_TEMPLATES = [
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
            {"name": "Lentes de Sol Polarizados", "price": 65.00, "description": "Lentes unisex con protección UV400 y montura de policarbonato", "image": "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=600&auto=format&fit=crop"},
            {"name": "Polo Básico Algodón Pima", "price": 45.00, "description": "Polo básico de cuello redondo confeccionado en algodón Pima peruano", "image": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=600&auto=format&fit=crop"},
            {"name": "Vestido Casual de Lino", "price": 135.00, "description": "Vestido fresco de lino ideal para días soleados y paseos casuales", "image": "https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=600&auto=format&fit=crop"},
            {"name": "Casaca de Cuero Sintético", "price": 199.00, "description": "Casaca biker de cuero sintético con cierres metálicos y forro suave", "image": "https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=600&auto=format&fit=crop"},
            {"name": "Short Denim Tiro Alto", "price": 79.00, "description": "Short de jean clásico tiro alto con bolsillos y dobladillo desflecado", "image": "https://images.unsplash.com/photo-1591195853828-11db59a44f6b?w=600&auto=format&fit=crop"},
            {"name": "Sombrero de Paja Fedora", "price": 50.00, "description": "Sombrero Fedora tejido a mano de paja toquilla con banda negra", "image": "https://images.unsplash.com/photo-1533055640609-24b498dfd74c?w=600&auto=format&fit=crop"},
            {"name": "Cardigan de Hilo Knitwear", "price": 95.00, "description": "Cardigan ligero de punto fino de hilo con botones frontales", "image": "https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?w=600&auto=format&fit=crop"}
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
            {"name": "Mouse Gamer Ergonómico RGB", "price": 75.00, "description": "Mouse óptico con hasta 7200 DPI y retroiluminación personalizable", "image": "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=600&auto=format&fit=crop"},
            {"name": "Powerbank Carga Rápida 20000mAh", "price": 119.00, "description": "Batería externa portátil de gran capacidad con display de carga", "image": "https://images.unsplash.com/photo-1583863788434-e58a36330cf0?w=600&auto=format&fit=crop"},
            {"name": "Cable USB-C de Nylon 2m", "price": 29.00, "description": "Cable reforzado de carga rápida USB-C a USB-C trenzado de nylon", "image": "https://images.unsplash.com/photo-1583863788434-e58a36330cf0?w=600&auto=format&fit=crop"},
            {"name": "Hub USB-C 8 en 1 Multipuerto", "price": 149.00, "description": "Adaptador multipuerto con puertos HDMI 4K, USB 3.0, SD y carga PD", "image": "https://images.unsplash.com/photo-1468495244123-6c6c332eeece?w=600&auto=format&fit=crop"},
            {"name": "Parlante Inalámbrico IPX7", "price": 199.00, "description": "Parlante Bluetooth resistente al agua con sonido estéreo 360", "image": "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=600&auto=format&fit=crop"},
            {"name": "Micrófono Condensador Podcast USB", "price": 249.00, "description": "Micrófono con trípode y filtro antipop ideal para streaming y llamadas", "image": "https://images.unsplash.com/photo-1590608897129-79da98d15969?w=600&auto=format&fit=crop"},
            {"name": "Aro de Luz LED 10 Pulgadas", "price": 69.00, "description": "Aro de luz con trípode ajustable y soporte para celular para videos", "image": "https://images.unsplash.com/photo-1611162617213-7d7a39e9b1d7?w=600&auto=format&fit=crop"}
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
            {"name": "Cojines Decorativos Algodón (x2)", "price": 40.00, "description": "Par de fundas de cojín con textura geométrica moderna", "image": "https://images.unsplash.com/photo-1584100936595-c0654b55a2e2?w=600&auto=format&fit=crop"},
            {"name": "Espejo de Pared Ovalado", "price": 185.00, "description": "Espejo decorativo con marco elegante de madera natural", "image": "https://images.unsplash.com/photo-1618220179428-22790b461013?w=600&auto=format&fit=crop"},
            {"name": "Estantes Flotantes Set x3", "price": 79.00, "description": "Juego de 3 repisas de madera flotantes con anclaje invisible", "image": "https://images.unsplash.com/photo-1595428774223-ef52624120d2?w=600&auto=format&fit=crop"},
            {"name": "Difusor de Aromas Ultrasónico", "price": 110.00, "description": "Humidificador y difusor con luces LED variables y apagado automático", "image": "https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?w=600&auto=format&fit=crop"},
            {"name": "Alfombra de Yute Redonda", "price": 150.00, "description": "Alfombra tejida a mano de fibras naturales de yute de 1.2m", "image": "https://images.unsplash.com/photo-1600121848594-d8644e57abab?w=600&auto=format&fit=crop"},
            {"name": "Velas Aromáticas de Soya x3", "price": 45.00, "description": "Set de velas aromáticas ecológicas en envases de vidrio", "image": "https://images.unsplash.com/photo-1603006905003-be475563bc59?w=600&auto=format&fit=crop"},
            {"name": "Regadera de Acero Minimalista", "price": 65.00, "description": "Regadera de cuello largo de acero inoxidable para plantas de interior", "image": "https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=600&auto=format&fit=crop"}
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
            {"name": "Bálsamo Labial Hidratante", "price": 15.00, "description": "Nutrición con aroma a frutos rojos y manteca de karité", "image": "https://images.unsplash.com/photo-1512496015851-a90fb38ba796?w=600&auto=format&fit=crop"},
            {"name": "Limpiador Facial Espumoso", "price": 49.00, "description": "Limpiador suave de uso diario con extracto de té verde", "image": "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=600&auto=format&fit=crop"},
            {"name": "Crema Facial de Ceramidas 50g", "price": 79.00, "description": "Crema reparadora de la barrera cutánea con ceramidas y centella", "image": "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=600&auto=format&fit=crop"},
            {"name": "Tónico Hidratante de Rosas", "price": 39.00, "description": "Tónico facial calmante y equilibrante con extractos florales", "image": "https://images.unsplash.com/photo-1601049541289-9b1b7bbbfe19?w=600&auto=format&fit=crop"},
            {"name": "Mascarilla Arcilla Purificante", "price": 45.00, "description": "Mascarilla detox de arcilla caolín para limpieza de poros", "image": "https://images.unsplash.com/photo-1567894340315-735d7c361db0?w=600&auto=format&fit=crop"},
            {"name": "Aceite Facial de Argán Orgánico", "price": 59.00, "description": "Aceite puro de argán prensado en frío para nutrición intensa", "image": "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=600&auto=format&fit=crop"},
            {"name": "Agua Micelar Desmaquillante 200ml", "price": 29.00, "description": "Limpiador y desmaquillante suave apto para pieles sensibles", "image": "https://images.unsplash.com/photo-1601049541289-9b1b7bbbfe19?w=600&auto=format&fit=crop"}
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
            {"name": "Tomatodo Deportivo Motivacional 1L", "price": 25.00, "description": "Tomatodo de Tritan libre de BPA con sorbete y marcas de agua", "image": "https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=600&auto=format&fit=crop"},
            {"name": "Bandas de Resistencia Set x5", "price": 35.00, "description": "Set de 5 bandas elásticas de látex con diferentes niveles de tensión", "image": "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=600&auto=format&fit=crop"},
            {"name": "Cuerda de Saltar de Velocidad", "price": 29.00, "description": "Cuerda con rodamientos metálicos y cable de acero ajustable", "image": "https://images.unsplash.com/photo-1601422407692-ec4eeec1d9b3?w=600&auto=format&fit=crop"},
            {"name": "Foam Roller de Masaje", "price": 45.00, "description": "Rodillo de espuma de alta densidad para recuperación muscular", "image": "https://images.unsplash.com/photo-1600880292089-90a7e086ee0c?w=600&auto=format&fit=crop"},
            {"name": "Muñequeras Elásticas x2", "price": 19.90, "description": "Muñequeras ajustables de algodón con soporte de pulgar", "image": "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=600&auto=format&fit=crop"},
            {"name": "Bolso Deportivo Impermeable 30L", "price": 89.00, "description": "Mochila deportiva con compartimento para zapatillas y ropa húmeda", "image": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=600&auto=format&fit=crop"},
            {"name": "Tobilleras con Peso 1.5kg (Par)", "price": 49.00, "description": "Tobilleras ajustables con pesos de arena para entrenamiento", "image": "https://images.unsplash.com/photo-1599447421416-3414500d18a5?w=600&auto=format&fit=crop"}
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
            {"name": "Bloques de Construcción de Madera", "price": 55.00, "description": "Set de 50 bloques de madera de colores con bolsa de almacenamiento", "image": "https://images.unsplash.com/photo-1596464716127-f2a82984de30?w=600&auto=format&fit=crop"},
            {"name": "Puzle Infantil Mapamundi", "price": 38.00, "description": "Rompecabezas de cartón grueso de 60 piezas sobre geografía", "image": "https://images.unsplash.com/photo-1587654780291-39c9404d746b?w=600&auto=format&fit=crop"},
            {"name": "Juego de Mesa 'Torre de Madera'", "price": 25.00, "description": "Juego de equilibrio clásico de 54 bloques estilo Jenga", "image": "https://images.unsplash.com/photo-1610890716171-6b1bb98ffd09?w=600&auto=format&fit=crop"},
            {"name": "Set de Témperas Lavables", "price": 45.00, "description": "Set de pinturas de dedos no tóxicas con pinceles y paleta", "image": "https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=600&auto=format&fit=crop"},
            {"name": "Pistola de Burbujas Eléctrica", "price": 35.00, "description": "Lanzador de burbujas automático a pilas con líquido incluido", "image": "https://images.unsplash.com/photo-1531608139434-1912ae0713cd?w=600&auto=format&fit=crop"},
            {"name": "Peluche de Jirafa Gigante 60cm", "price": 79.00, "description": "Peluche de jirafa de felpa extrasuave con relleno hipoalergénico", "image": "https://images.unsplash.com/photo-1559251606-c623743a6d76?w=600&auto=format&fit=crop"},
            {"name": "Set de Arena Mágica Moldeable", "price": 39.00, "description": "Contiene 1kg de arena cinética de colores y moldes plásticos", "image": "https://images.unsplash.com/photo-1587654780291-39c9404d746b?w=600&auto=format&fit=crop"},
            {"name": "Coche de Control Remoto", "price": 89.00, "description": "Auto todoterreno a control remoto con batería recargable USB", "image": "https://images.unsplash.com/photo-1594787318286-3d835c1d207f?w=600&auto=format&fit=crop"},
            {"name": "Set de Plastilinas de Colores x12", "price": 29.00, "description": "Estuche con 12 barras de plastilina blanda moldeable y herramientas", "image": "https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=600&auto=format&fit=crop"}
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
            {"name": "Lapiceros Gel de Colores (x12)", "price": 22.00, "description": "Estuche con 12 bolígrafos gel de punta fina colores vibrantes", "image": "https://images.unsplash.com/photo-1513542789411-b6a5d4f31634?w=600&auto=format&fit=crop"},
            {"name": "Resaltadores Pastel Estuche x6", "price": 18.00, "description": "Resaltadores de punta de cincel colores pastel de secado rápido", "image": "https://images.unsplash.com/photo-1513542789411-b6a5d4f31634?w=600&auto=format&fit=crop"},
            {"name": "Organizador de Escritorio Acrílico", "price": 39.00, "description": "Organizador transparente con cajones ideal para maquillaje y notas", "image": "https://images.unsplash.com/photo-1586075010923-2dd4570fb338?w=600&auto=format&fit=crop"},
            {"name": "Libro de Acuarelas e Ilustración", "price": 79.00, "description": "Manual básico ilustrado para aprender técnicas de pintura acuarela", "image": "https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=600&auto=format&fit=crop"},
            {"name": "Agenda y Planificador Anual", "price": 45.00, "description": "Agenda de vista semanal para organización de metas y tareas", "image": "https://images.unsplash.com/photo-1506784983877-45594efa4cbe?w=600&auto=format&fit=crop"},
            {"name": "Caja de Colores Profesionales x36", "price": 69.00, "description": "Estuche metálico de lápices de color de mina suave de cera", "image": "https://images.unsplash.com/photo-1513542789411-b6a5d4f31634?w=600&auto=format&fit=crop"},
            {"name": "Libro de Crecimiento Personal", "price": 49.00, "description": "Guía práctica de hábitos saludables y desarrollo de metas", "image": "https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=600&auto=format&fit=crop"}
        ]
    },
    {
        "name": "Urban Style",
        "description": "Ropa de calle cómoda y moderna con envíos rápidos a todo el país",
        "email": "urbanstyle@example.com",
        "owner": "Elena Rostova",
        "phone": "+51 912 888 777",
        "theme": "fashion",
        "ruc": "20129988443",
        "category_slug": "ropa-y-moda",
        "products": [
            {"name": "Polera Hoodie de Algodón Negra", "price": 99.00, "description": "Polera con capucha, forro polar interior y bolsillo canguro", "image": "https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=600&auto=format&fit=crop"},
            {"name": "Pantalón Jogger Slim Fit", "price": 85.00, "description": "Jogger deportivo con bolsillos laterales y cintura elástica", "image": "https://images.unsplash.com/photo-1551854838-212c50b4c184?w=600&auto=format&fit=crop"},
            {"name": "Casaca Cortavientos Impermeable", "price": 110.00, "description": "Cortavientos ligero ideal para running y días lluviosos", "image": "https://images.unsplash.com/photo-1548883354-7622d03aca27?w=600&auto=format&fit=crop"},
            {"name": "Gorra Trucker Ajustable", "price": 35.00, "description": "Gorra de malla con visera curva y broche plástico ajustable", "image": "https://images.unsplash.com/photo-1588850561407-ed78c282e89b?w=600&auto=format&fit=crop"},
            {"name": "Polo Estampado Streetwear", "price": 55.00, "description": "Polo de algodón con estampado gráfico en pecho y espalda", "image": "https://images.unsplash.com/photo-1503342217505-b0a15ec3261c?w=600&auto=format&fit=crop"},
            {"name": "Zapatillas de Skate Unisex", "price": 169.00, "description": "Zapatillas con suela plana de goma vulcanizada para skate", "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&auto=format&fit=crop"},
            {"name": "Pack de Medias Altas (x3)", "price": 29.00, "description": "Set de 3 pares de calcetines deportivos de algodón acanalado", "image": "https://images.unsplash.com/photo-1582966772680-860e372bb558?w=600&auto=format&fit=crop"},
            {"name": "Mochila Porta Laptop 20L", "price": 129.00, "description": "Mochila con compartimento acolchado para laptop de 15.6 pulgadas", "image": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=600&auto=format&fit=crop"},
            {"name": "Casaca Bomber Satinada", "price": 149.00, "description": "Casaca clásica bomber con puños y cuello elásticos", "image": "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=600&auto=format&fit=crop"}
        ]
    },
    {
        "name": "Gadget World",
        "description": "Accesorios premium y herramientas inteligentes para profesionales y estudiantes",
        "email": "gadgetworld@example.com",
        "owner": "Marcos Del Pino",
        "phone": "+51 932 777 111",
        "theme": "tech",
        "ruc": "20443322117",
        "category_slug": "electronica",
        "products": [
            {"name": "Teclado Mecánico Switch Blue", "price": 189.90, "description": "Teclado mecánico con retroiluminación RGB y switches Outemu Blue", "image": "https://images.unsplash.com/photo-1618384887929-16ec33fab9ef?w=600&auto=format&fit=crop"},
            {"name": "Soporte de Laptop de Aluminio", "price": 45.00, "description": "Soporte plegable y ergonómico con 6 niveles de altura ajustable", "image": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=600&auto=format&fit=crop"},
            {"name": "Smartwatch Deportivo Pro", "price": 159.00, "description": "Reloj inteligente con monitor de ritmo cardíaco, podómetro y notificaciones", "image": "https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=600&auto=format&fit=crop"},
            {"name": "Mouse Pad Gamer Extragrande", "price": 49.00, "description": "Mouse pad de 90x40cm de superficie textil suave y bordes cosidos", "image": "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=600&auto=format&fit=crop"},
            {"name": "Luces LED RGB Inteligentes 5m", "price": 65.00, "description": "Tira LED inteligente controlada por app móvil y asistentes de voz", "image": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=600&auto=format&fit=crop"},
            {"name": "Ventilador Cooler para Laptop", "price": 79.00, "description": "Base enfriadora de laptop con ventiladores silenciosos y puertos USB", "image": "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?w=600&auto=format&fit=crop"},
            {"name": "Cargador Inalámbrico Rápido", "price": 55.00, "description": "Base de carga inalámbrica rápida Qi para teléfonos compatibles", "image": "https://images.unsplash.com/photo-1583863788434-e58a36330cf0?w=600&auto=format&fit=crop"},
            {"name": "Estuche Organizador de Cables", "price": 39.00, "description": "Bolsa de almacenamiento compacta e impermeable para cables y memorias USB", "image": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=600&auto=format&fit=crop"},
            {"name": "Trípode para Celular y Cámara", "price": 89.00, "description": "Trípode de aluminio ligero con cabezal móvil y soporte ajustable", "image": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=600&auto=format&fit=crop"}
        ]
    },
    {
        "name": "Smart Office",
        "description": "Artículos ergonómicos y gadgets organizativos para trabajo remoto u oficina",
        "email": "smartoffice@example.com",
        "owner": "Sofía Alarcón",
        "phone": "+51 945 222 111",
        "theme": "home",
        "ruc": "20887711228",
        "category_slug": "hogar-y-jardin",
        "products": [
            {"name": "Organizador de Escritorio de Bambú", "price": 49.90, "description": "Organizador ecológico con cajones y compartimentos múltiples", "image": "https://images.unsplash.com/photo-1513151233558-d860c5398176?w=600&auto=format&fit=crop"},
            {"name": "Lámpara de Lectura LED Clip", "price": 79.90, "description": "Luz LED recargable con pinza para lectura y 3 modos de temperatura", "image": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=600&auto=format&fit=crop"},
            {"name": "Silla de Escritorio Ergonómica", "price": 320.00, "description": "Silla de oficina giratoria con soporte lumbar y reposabrazos regulables", "image": "https://images.unsplash.com/photo-1505797149-43b0069ec26b?w=600&auto=format&fit=crop"},
            {"name": "Escritorio Regulable Altura", "price": 650.00, "description": "Escritorio eléctrico elevable con panel de control de memoria", "image": "https://images.unsplash.com/photo-1518455027359-f3f8164ba6bd?w=600&auto=format&fit=crop"},
            {"name": "Soporte de Escritorio Celular", "price": 25.00, "description": "Soporte metálico estable de sobremesa con almohadillas de silicona", "image": "https://images.unsplash.com/photo-1586105251261-72a756497a11?w=600&auto=format&fit=crop"},
            {"name": "Pizarra Acrílica Magnética 60x40", "price": 59.00, "description": "Pizarra blanca de pared ideal para notas, incluye imanes y plumón", "image": "https://images.unsplash.com/photo-1506784983877-45594efa4cbe?w=600&auto=format&fit=crop"},
            {"name": "Taza Térmica Acero Inoxidable", "price": 45.00, "description": "Vaso térmico de doble pared que mantiene bebidas calientes por 6 horas", "image": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=600&auto=format&fit=crop"},
            {"name": "Papelera de Malla Metálica", "price": 25.00, "description": "Tacho de basura de oficina de metal mesh color negro", "image": "https://images.unsplash.com/photo-1586075010923-2dd4570fb338?w=600&auto=format&fit=crop"},
            {"name": "Apoya pies Ergonómico", "price": 89.00, "description": "Reposapiés inclinable con rodillos de masaje para descanso activo", "image": "https://images.unsplash.com/photo-1580481072645-022f9a6dbf27?w=600&auto=format&fit=crop"}
        ]
    }
]

# 3. Comentarios realistas de reseñas según categoría
REVIEW_COMMENTS_BY_CATEGORY = {
    "ropa-y-moda": [
        "Excelente calidad de confección, la casaca es abrigadora y de buena tela.",
        "Las zapatillas calzan perfectas. Muy cómodas y el diseño es moderno.",
        "El material superó mis expectativas, la talla corresponde exactamente.",
        "Muy lindo modelo, el envío llegó antes de lo estimado."
    ],
    "electronica": [
        "El sonido es nítido y aísla muy bien el ruido. La batería es duradera.",
        "Carga rápida muy eficiente, ideal para viajes por su tamaño compacto.",
        "El mouse es ergonómico y la respuesta del sensor óptico es excelente.",
        "Excelente teclado, los materiales se sienten robustos y las teclas son suaves."
    ],
    "hogar-y-jardin": [
        "Las macetas se ven preciosas en mi sala. Llegaron súper empaquetadas.",
        "La lámpara alumbra perfecto y el brazo articulado es muy firme y práctico.",
        "Los cojines tienen un tacto muy agradable y el relleno es bastante cómodo.",
        "El organizador es muy estético y de madera resistente, ayuda mucho al orden."
    ],
    "salud-y-belleza": [
        "El sérum me deja la piel sumamente suave y con brillo natural.",
        "El protector solar es ligero, no deja capa blanca y tiene efecto mate.",
        "El bálsamo labial hidrata súper bien y tiene un aroma delicioso a frutas.",
        "Textura fluida, ideal para el uso diario. Muy buena marca."
    ],
    "deportes": [
        "El mat es grueso y tiene buen agarre, no se resbala durante los ejercicios.",
        "Las mancuernas tienen un recubrimiento suave que no daña el suelo.",
        "El tomatodo es resistente, no derrama nada y el diseño motivacional ayuda.",
        "Excelente equipamiento para entrenar en casa. Satisfecho con la compra."
    ],
    "juguetes": [
        "A mis hijos les encantan los bloques, muy coloridos y seguros.",
        "El puzle tiene buena definición y encaja perfectamente.",
        "La torre de madera es divertidísima para jugar en familia los fines de semana.",
        "Juego interactivo y didáctico de excelente calidad de madera."
    ],
    "libros": [
        "Los cuadernos tienen papel de muy buen gramaje, las hojas no traslapan tinta.",
        "Una historia cautivante, no pude parar de leer hasta terminarlo.",
        "Los lapiceros gel pintan súper suave y los colores son muy vibrantes.",
        "Libro en excelente estado, original y sellado de fábrica. Recomendado."
    ]
}

def main():
    print("=" * 60)
    print("  INICIALIZACIÓN DE SEMILLERO DE RETAIL (SEED_RETAIL_DATA)")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # === PASO 1: LIMPIEZA DE DATOS ANTERIORES ===
        print("\n[1/7] Limpiando datos anteriores de base de datos...")
        
        # Eliminar reseñas, códigos de entrega, métricas, y chats
        db.query(Review).delete()
        db.query(DeliveryCode).delete()
        db.query(StoreMetric).delete()
        
        from app.models.chat import Chat, Message
        db.query(Message).delete()
        db.query(Chat).delete()
        
        # Eliminar pedidos
        db.query(Order).delete()
        
        # Eliminar productos
        db.query(Product).delete()
        
        # Eliminar tiendas
        db.query(Store).delete()
        
        # Eliminar usuarios creados por seeder
        demo_emails = [f"vendedor{i}@example.com" for i in range(1, 11)] + ["comprador_demo@example.com"]
        db.query(User).filter(User.email.in_(demo_emails)).delete(synchronize_session=False)
        
        # Eliminar categoría 'comida'
        db.query(Category).filter(Category.slug == "comida").delete(synchronize_session=False)
        db.commit()
        print("  ~ Base de datos limpiada correctamente.")

        # === PASO 2: CREACIÓN DE CATEGORÍAS ===
        print("\n[2/7] Creando categorías de retail...")
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

        # === PASO 3: CREACIÓN DEL COMPRADOR DEMO ===
        print("\n[3/7] Creando usuario comprador demo...")
        buyer_user = User(
            email="comprador_demo@example.com",
            name="Juan Perez (Demo)",
            password=get_password_hash("password123"),
            address="Av. Larco 456, Miraflores, Lima",
            phone="+51 988 888 888",
            role="buyer"
        )
        db.add(buyer_user)
        db.commit()
        db.refresh(buyer_user)
        print("  + Usuario comprador demo creado: comprador_demo@example.com")

        # === PASO 4: CREACIÓN DE VENDEDORES, TIENDAS Y PRODUCTOS ===
        print("\n[4/7] Creando vendedores, tiendas y productos...")
        stores_created = []
        all_products = []

        for i, st in enumerate(STORE_TEMPLATES, 1):
            seller_email = f"vendedor{i}@example.com"
            
            # Crear usuario vendedor
            seller = User(
                email=seller_email,
                name=st["owner"],
                password=get_password_hash("password123"),
                phone=st["phone"],
                address=f"Calle Comercio 10{i}, Miraflores, Lima",
                role="seller"
            )
            db.add(seller)
            db.commit()
            db.refresh(seller)
            print(f"  + Vendedor {i} creado: {st['owner']} ({seller_email})")

            # Crear tienda asociada
            store = Store(
                name=st["name"],
                email=st["email"],
                owner_name=st["owner"],
                phone=st["phone"],
                description=st["description"],
                ruc=st["ruc"],
                theme=st["theme"],
                status="active", # Activa directamente para visualización
                user_id=seller.id,
                auto_confirm_orders=True
            )
            db.add(store)
            db.commit()
            db.refresh(store)
            stores_created.append(store)
            print(f"    -> Tienda creada: {st['name']} (ID: {store.id})")

            # Cargar productos para esta tienda
            cat_id = category_map.get(st["category_slug"])
            for prod_data in st["products"]:
                prod = Product(
                    name=prod_data["name"],
                    price=prod_data["price"],
                    description=prod_data["description"],
                    image=prod_data["image"],
                    category=st["category_slug"],
                    category_id=cat_id,
                    store_id=store.id,
                    store_name=store.name,
                    stock=random.randint(20, 100),
                    rating=0.0,      # Inicialmente 0, se recalcula con reseñas
                    rating_count=0,   # Inicialmente 0, se recalcula con reseñas
                    created_at=datetime.utcnow() - timedelta(days=random.randint(10, 45))
                )
                db.add(prod)
                db.commit()
                db.refresh(prod)
                all_products.append(prod)
                print(f"       * Producto creado: {prod.name} (S/. {prod.price})")

        # === PASO 5: CREACIÓN DE PEDIDOS COMPLETADOS ===
        print("\n[5/7] Generando pedidos completados e históricos de compra...")
        orders_created = []

        # Crear entre 3 y 5 pedidos completados por tienda en las últimas 2 semanas
        for store in stores_created:
            store_prods = [p for p in all_products if p.store_id == store.id]
            if not store_prods:
                continue

            num_orders = random.randint(3, 5)
            for _ in range(num_orders):
                # Tomar 1 o 2 productos aleatorios de la tienda
                chosen_prods = random.sample(store_prods, k=min(len(store_prods), random.randint(1, 2)))
                order_items_json = []
                total = 0.0
                
                for cp in chosen_prods:
                    qty = random.randint(1, 2)
                    price = cp.price
                    total += price * qty
                    order_items_json.append({
                        "productId": cp.id,
                        "quantity": qty,
                        "price": price,
                        "name": cp.name
                    })
                    
                    # Descontar stock
                    if cp.stock is not None:
                        cp.stock -= qty

                order_date = datetime.utcnow() - timedelta(days=random.randint(1, 13), hours=random.randint(1, 23))
                
                new_order = Order(
                    user_id=buyer_user.id,
                    products=order_items_json,
                    total_amount=total,
                    status="completed", # Entregado
                    created_at=order_date,
                    updated_at=order_date + timedelta(hours=random.randint(1, 4)),
                    shipping_address="Calle Las Magnolias " + str(random.randint(100, 999)) + ", Lima",
                    contact_phone="+51 988 888 888",
                    shipping_latitude=-12.046374 + random.uniform(-0.02, 0.02),
                    shipping_longitude=-77.042793 + random.uniform(-0.02, 0.02),
                    delivery_latitude=-12.046374 + random.uniform(-0.02, 0.02),
                    delivery_longitude=-77.042793 + random.uniform(-0.02, 0.02),
                    delivery_status="completed"
                )
                db.add(new_order)
                db.commit()
                db.refresh(new_order)
                orders_created.append(new_order)

                # Generar código de entrega (marcado como usado)
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

            print(f"    -> Creados {num_orders} pedidos entregados para la tienda: {store.name}")

        # === PASO 6: CREACIÓN DE RESEÑAS COHERENTES Y RECÁLCULO DE CALIFICACIONES ===
        print("\n[6/7] Creando reseñas realistas y recalculando promedios de calificación...")
        
        # Para cada pedido completado, escribir reseñas para todos sus productos
        for o in orders_created:
            for item in o.products:
                prod_id = item.get("productId")
                prod = db.query(Product).filter(Product.id == prod_id).first()
                if not prod:
                    continue
                
                # Obtener comentarios realistas según la categoría
                cat_slug = prod.category
                possible_comments = REVIEW_COMMENTS_BY_CATEGORY.get(cat_slug, [
                    "Excelente producto, llegó rápido y bien empaquetado.",
                    "Muy conforme con la compra. El vendedor respondió a tiempo.",
                    "Totalmente recomendado, cumple con lo descrito en la página."
                ])
                
                review_rating = round(random.uniform(4.0, 5.0), 1)
                store_rating = round(random.uniform(4.2, 5.0), 1)
                
                new_review = Review(
                    user_id=buyer_user.id,
                    product_id=prod.id,
                    store_id=prod.store_id,
                    order_id=o.id,
                    rating=review_rating,
                    store_rating=store_rating,
                    comment=random.choice(possible_comments),
                    image_url=None,
                    created_at=o.updated_at + timedelta(hours=random.randint(1, 24))
                )
                db.add(new_review)
                db.commit()

        # Recalcular el rating y rating_count de cada producto en la base de datos
        for prod in all_products:
            stats = db.query(
                func.avg(Review.rating),
                func.count(Review.id)
            ).filter(Review.product_id == prod.id).first()
            
            avg_val = stats[0] if stats and stats[0] is not None else 0.0
            count_val = stats[1] if stats and stats[1] is not None else 0
            
            prod.rating = round(float(avg_val), 1)
            prod.rating_count = int(count_val)
            db.commit()
            print(f"       * Calificación de {prod.name}: {prod.rating} estrellas ({prod.rating_count} reseñas)")

        # === PASO 7: GENERACIÓN DE MÉTRICAS DIARIAS (STOREMETRIC) ===
        print("\n[7/7] Generando historial de métricas diarias (14 días atrás) para Seller Dashboard...")
        
        # Utilizar func global de sqlalchemy
        hoy = date.today()
        for store in stores_created:
            # Obtener cantidad de productos publicados
            prod_count = db.query(Product).filter(Product.store_id == store.id).count()
            
            # Obtener todos los IDs de productos de la tienda
            store_prods = db.query(Product).filter(Product.store_id == store.id).all()
            store_prod_ids = {p.id for p in store_prods}

            # Obtener todos los pedidos
            orders_all = db.query(Order).all()
            
            # Mapear ventas por fecha
            date_sales = {}
            for o in orders_all:
                order_date_only = o.created_at.date()
                store_items_in_order = [item for item in o.products if item.get("productId") in store_prod_ids]
                if not store_items_in_order:
                    continue
                
                subtotal = sum(item["price"] * item["quantity"] for item in store_items_in_order)
                
                if order_date_only not in date_sales:
                    date_sales[order_date_only] = {"revenue": Decimal("0.0"), "orders": 0}
                
                date_sales[order_date_only]["revenue"] += Decimal(str(subtotal))
                date_sales[order_date_only]["orders"] += 1

            # Rellenar métricas diarias para cada uno de los últimos 14 días
            for d in range(14):
                fecha_metrica = hoy - timedelta(days=d)
                sales_today = date_sales.get(fecha_metrica, {"revenue": Decimal("0.0"), "orders": 0})
                
                # Simular visitas: más visitas si hay ventas
                base_visits = random.randint(20, 80)
                if sales_today["orders"] > 0:
                    base_visits += sales_today["orders"] * random.randint(15, 45)
                
                # Simular chats
                chats = random.randint(1, 10)
                if sales_today["orders"] > 0:
                    chats += sales_today["orders"] * random.randint(1, 3)

                # Promedio de rating de la tienda
                stats = db.query(func.avg(Review.store_rating)).filter(Review.store_id == store.id).first()
                avg_rating = stats[0] if stats and stats[0] is not None else 5.0

                metric = StoreMetric(
                    store_id=store.id,
                    date=fecha_metrica,
                    visits=base_visits,
                    products_published=prod_count,
                    orders_delivered=sales_today["orders"],
                    revenue=sales_today["revenue"],
                    chat_sessions=chats,
                    template_usage=random.randint(0, 3),
                    new_users=random.randint(1, 5) if sales_today["orders"] > 0 else random.randint(0, 1),
                    avg_rating=round(float(avg_rating), 1),
                    created_at=datetime.combine(fecha_metrica, datetime.min.time()),
                    updated_at=datetime.combine(fecha_metrica, datetime.max.time())
                )
                db.add(metric)

        db.commit()
        print("  [OK] Historial de métricas completado para las tiendas.")

        print("\n" + "=" * 60)
        print("  [OK] ¡Base de Datos inicializada con el Catálogo de Retail!")
        print("Detalles:")
        print(" - Categoría 'Comida' y datos de alimentos eliminados.")
        print(" - 10 Tiendas de retail (Ropa, Tecnología, Hogar, Belleza, Deportes, Juguetes, Libros).")
        print(" - Productos actualizados con imágenes reales de e-commerce.")
        print(" - Compras ficticias y entregas registradas.")
        print(" - Reseñas y valoraciones coherentes agregadas a los productos.")
        print(" - Métricas diarias de las tiendas pobladas para el dashboard.")
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
