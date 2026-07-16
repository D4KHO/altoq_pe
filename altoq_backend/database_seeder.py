import sys
import os

# Agregar el directorio actual al path para importar correctamente
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, Base, engine
from seeders import category_seeder, user_seeder, store_seeder, product_seeder, order_seeder

def main():
    print("=" * 60)
    # Equivalente a DatabaseSeeder de Laravel
    print("      ORQUESTRADOR DE SEMBRADO (DATABASE SEEDER) - ALTOQ")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        # 1. Sembrar categorías
        category_seeder.run(db)
        
        # 2. Sembrar usuarios (comprador demo + 10 vendedores)
        user_seeder.run(db)
        
        # 3. Sembrar tiendas vinculadas
        store_seeder.run(db)
        
        # 4. Sembrar productos del catálogo
        product_seeder.run(db)
        
        # 5. Sembrar pedidos, códigos e historial de métricas
        order_seeder.run(db)
        
        print("\n" + "=" * 60)
        print("  [OK] ¡La base de datos local ha sido sembrada con éxito!")
        print("=" * 60)
        
    except Exception as e:
        db.rollback()
        print(f"\n[ERROR] Ocurrió un error al sembrar la base de datos: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()
