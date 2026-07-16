import sys
import os

# Agregar el directorio actual al path para importar correctamente los módulos de app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.chat import Chat, Message
from app.models.delivery_code import DeliveryCode
from app.models.review import Review
from app.models.order import Order
from app.models.store_metric import StoreMetric
from app.models.inquiry import StoreInquiry
from app.models.product import Product
from app.models.address import Address
from app.models.store import Store
from app.models.password_reset import PasswordResetCode
from app.models.template import ProductTemplate, TemplateField
from app.models.category import Category
from app.models.user import User
from app.models.admin import Admin

def main():
    print("=" * 60)
    print("      BORRADOR TOTAL DE BASE DE DATOS (CLEAR ALL)")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        # 1. Eliminar mensajes de chat
        print("Eliminando mensajes de chat...")
        db.query(Message).delete()
        
        # 2. Eliminar chats
        print("Eliminando chats...")
        db.query(Chat).delete()
        
        # 3. Eliminar códigos de entrega
        print("Eliminando codigos de entrega...")
        db.query(DeliveryCode).delete()
        
        # 4. Eliminar reseñas de productos
        print("Eliminando resenas de productos...")
        db.query(Review).delete()
        
        # 5. Eliminar pedidos (órdenes)
        print("Eliminando pedidos...")
        db.query(Order).delete()
        
        # 6. Eliminar métricas de tienda
        print("Eliminando metricas de tienda...")
        db.query(StoreMetric).delete()
        
        # 7. Eliminar consultas de contacto/tienda
        print("Eliminando consultas...")
        db.query(StoreInquiry).delete()
        
        # 8. Eliminar campos de plantillas
        print("Eliminando campos de plantillas...")
        db.query(TemplateField).delete()
        
        # 9. Eliminar plantillas de productos
        print("Eliminando plantillas de productos...")
        db.query(ProductTemplate).delete()
        
        # 10. Eliminar productos
        print("Eliminando productos...")
        db.query(Product).delete()
        
        # 11. Eliminar direcciones
        print("Eliminando direcciones de entrega...")
        db.query(Address).delete()
        
        # 12. Eliminar tiendas
        print("Eliminando tiendas...")
        db.query(Store).delete()
        
        # 13. Eliminar códigos de recuperación de contraseña
        print("Eliminando codigos de recuperacion...")
        db.query(PasswordResetCode).delete()
        
        # 14. Eliminar categorías
        print("Eliminando categorias...")
        db.query(Category).delete()
        
        # 15. Eliminar usuarios
        print("Eliminando usuarios...")
        db.query(User).delete()
        
        # 16. Eliminar administradores
        print("Eliminando administradores...")
        db.query(Admin).delete()
        
        # Confirmar todos los cambios
        db.commit()
        
        print("\n" + "=" * 60)
        print(" [OK] Base de datos vaciada completamente con exito!")
        print("=" * 60)
        
    except Exception as e:
        db.rollback()
        print(f"\n[ERROR] Ocurrio un error al vaciar la base de datos: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()
