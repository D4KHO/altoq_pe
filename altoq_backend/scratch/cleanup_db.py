import sys
import os

# Agregar el directorio actual al path para importar correctamente los módulos de app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.chat import Chat, Message
from app.models.delivery_code import DeliveryCode
from app.models.order import Order
from app.models.password_reset import PasswordResetCode
from app.models.inquiry import StoreInquiry
from app.models.review import Review

def main():
    print("=" * 60)
    print("       LIMPIADOR DE TRANSACCIONES DE BASE DE DATOS")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        # 1. Eliminar mensajes de chat
        print("Eliminando mensajes de chat...")
        num_messages = db.query(Message).delete()
        print(f"[OK] {num_messages} mensajes eliminados.")
        
        # 2. Eliminar chats
        print("Eliminando chats...")
        num_chats = db.query(Chat).delete()
        print(f"[OK] {num_chats} chats eliminados.")
        
        # 3. Eliminar códigos de entrega
        print("Eliminando códigos de entrega...")
        num_delivery_codes = db.query(DeliveryCode).delete()
        print(f"[OK] {num_delivery_codes} codigos de entrega eliminados.")
        
        # 4. Eliminar reseñas de productos (ya que referencian a órdenes/pedidos)
        print("Eliminando reseñas de productos...")
        num_reviews = db.query(Review).delete()
        print(f"[OK] {num_reviews} resenas de productos eliminadas.")
        
        # 5. Eliminar pedidos (órdenes)
        print("Eliminando pedidos...")
        num_orders = db.query(Order).delete()
        print(f"[OK] {num_orders} pedidos eliminados.")
        
        # 6. Eliminar códigos de restablecimiento de contraseña
        print("Eliminando códigos de recuperación de contraseña...")
        num_resets = db.query(PasswordResetCode).delete()
        print(f"[OK] {num_resets} codigos eliminados.")

        # 7. Eliminar consultas de tiendas
        print("Eliminando consultas de contacto/tienda...")
        num_inquiries = db.query(StoreInquiry).delete()
        print(f"[OK] {num_inquiries} consultas eliminadas.")
        
        # Confirmar los cambios en la BD
        db.commit()
        
        print("\n" + "=" * 60)
        print(" [OK] Limpieza de base de datos completada exitosamente!")
        print("=" * 60)
        
    except Exception as e:
        db.rollback()
        print(f"\n[ERROR] Ocurrio un error al limpiar la base de datos: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()
