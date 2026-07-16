import random
from datetime import datetime, date, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.store import Store
from app.models.product import Product
from app.models.order import Order
from app.models.delivery_code import DeliveryCode
from app.models.store_metric import StoreMetric

def run(db: Session):
    print("\n[5/5] Sembrando pedidos, entregas e historial de métricas...")
    
    buyer_user = db.query(User).filter(User.email == "buyer_demo@example.com").first()
    if not buyer_user:
        print("  [ERROR] No se pudo sembrar pedidos porque el usuario 'buyer_demo@example.com' no existe.")
        return
        
    stores = db.query(Store).all()
    all_products = db.query(Product).all()
    
    # 1. Limpiar pedidos de pruebas previos
    demo_order_ids = [o.id for o in db.query(Order).filter(Order.shipping_address.like("%(Seeder Demo)%")).all()]
    if demo_order_ids:
        db.query(DeliveryCode).filter(DeliveryCode.order_id.in_(demo_order_ids)).delete(synchronize_session=False)
    demo_orders_count = db.query(Order).filter(Order.shipping_address.like("%(Seeder Demo)%")).delete(synchronize_session=False)
    db.commit()
    if demo_orders_count > 0:
        print(f"  ~ Eliminadas {demo_orders_count} órdenes del semillero anterior.")

    # 2. Crear pedidos entregados
    for store in stores:
        store_prods = [p for p in all_products if p.store_id == store.id]
        if not store_prods:
            continue

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

            # Generar código de entrega verificado
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

    # 3. Limpiar y regenerar métricas diarias históricas para los últimos 14 días
    print("  ~ Limpiando métricas anteriores...")
    db.query(StoreMetric).delete()
    db.commit()

    print("  ~ Generando métricas diarias históricas (14 días atrás)...")
    hoy = date.today()
    for store in stores:
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
            
            if order_date_only not in date_sales:
                date_sales[order_date_only] = {"revenue": Decimal("0.0"), "orders": 0}
            
            date_sales[order_date_only]["revenue"] += Decimal(str(subtotal))
            date_sales[order_date_only]["orders"] += 1

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
    print("  [OK] Historial de métricas completado para todas las tiendas.")
