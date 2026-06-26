from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
import random
import string

from ..database import get_db
from ..models.order import Order as OrderModel
from ..models.delivery_code import DeliveryCode
from ..models.user import User
from ..models.product import Product
from ..models.store import Store
from ..schemas.order import Order, OrderCreate
from ..dependencies import get_current_user

router = APIRouter(prefix="/api/orders", tags=["orders"])


def _generate_code(length: int = 6) -> str:
    """Genera un código alfanumérico único."""
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def _create_delivery_code(db: Session, order_id: int) -> DeliveryCode:
    """Crea y persiste un código de entrega único para una orden."""
    code = _generate_code()
    while db.query(DeliveryCode).filter(DeliveryCode.code == code).first():
        code = _generate_code()

    new_code = DeliveryCode(
        order_id=order_id,
        code=code,
        is_used=False,
        created_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(days=30),
    )
    db.add(new_code)
    db.commit()
    db.refresh(new_code)
    return new_code

def _populate_order_product_names(orders_data, db: Session):
    if not orders_data:
        return
    if isinstance(orders_data, list):
        for o in orders_data:
            _populate_single_order(o, db)
    else:
        _populate_single_order(orders_data, db)


def _populate_single_order(o, db: Session):
    products = o.products or []
    if isinstance(products, list):
        updated_products = []
        for p in products:
            if isinstance(p, dict):
                p_copy = dict(p)
                if not p_copy.get("name") and p_copy.get("productId"):
                    prod = db.query(Product).filter(Product.id == p_copy["productId"]).first()
                    if prod:
                        p_copy["name"] = prod.name
                updated_products.append(p_copy)
            else:
                updated_products.append(p)
        o.products = updated_products


@router.post("/", response_model=Order)
def create_order(
    order: OrderCreate,
    current_user_email: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Crear una nueva orden y generar su código de entrega automáticamente."""
    user = db.query(User).filter(User.email == current_user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Prevenir que un vendedor compre su propio producto
    user_store = db.query(Store).filter(Store.user_id == user.id).first()
    if user_store:
        order_product_ids = [p.productId for p in order.products]
        own_products = db.query(Product).filter(
            Product.id.in_(order_product_ids),
            Product.store_id == user_store.id
        ).all()
        if own_products:
            product_names = ", ".join([p.name for p in own_products])
            raise HTTPException(
                status_code=400,
                detail=f"No puedes comprar tus propios productos: {product_names}"
            )

    # 1. Validar stock de todos los productos antes de crear la orden
    for item in order.products:
        prod = db.query(Product).filter(Product.id == item.productId).first()
        if not prod:
            raise HTTPException(status_code=404, detail=f"Producto con ID {item.productId} no encontrado")
        if prod.stock is not None:
            if prod.stock < item.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Stock insuficiente para el producto '{prod.name}' (Disponible: {prod.stock}, Solicitado: {item.quantity})"
                )

    # 2. Descontar el stock de los productos
    for item in order.products:
        prod = db.query(Product).filter(Product.id == item.productId).first()
        if prod and prod.stock is not None:
            prod.stock -= item.quantity

    # 3. Determinar si el pedido se confirma automáticamente
    auto_confirm = True
    if order.products:
        first_product_id = order.products[0].productId
        prod = db.query(Product).filter(Product.id == first_product_id).first()
        if prod and prod.store_id:
            store = db.query(Store).filter(Store.id == prod.store_id).first()
            if store:
                auto_confirm = store.auto_confirm_orders

    initial_status = "confirmed" if auto_confirm else "pending"

    products_json = [item.dict() for item in order.products]

    db_order = OrderModel(
        user_id=user.id,
        products=products_json,
        total_amount=order.total_amount,
        status=initial_status,
        shipping_address=order.shipping_address,
        contact_phone=order.contact_phone,
        shipping_latitude=order.shipping_latitude,
        shipping_longitude=order.shipping_longitude,
        delivery_status="pending",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    # Generar código de entrega automáticamente
    delivery = _create_delivery_code(db, db_order.id)

    # Adjuntar el código al response (campo virtual)
    db_order.delivery_code = delivery.code  # type: ignore[attr-defined]
    _populate_order_product_names(db_order, db)
    return db_order


@router.get("/user", response_model=List[Order])
def get_user_orders(
    current_user_email: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Obtener las órdenes del usuario autenticado."""
    user = db.query(User).filter(User.email == current_user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    orders = db.query(OrderModel).filter(
        OrderModel.user_id == user.id
    ).order_by(OrderModel.created_at.desc()).all()

    # Adjuntar el código de entrega a cada orden
    for o in orders:
        dc = db.query(DeliveryCode).filter(DeliveryCode.order_id == o.id).first()
        o.delivery_code = dc.code if dc else None  # type: ignore[attr-defined]
        o.client_name = o.user.name if o.user else None  # type: ignore[attr-defined]
        o.client_email = o.user.email if o.user else None  # type: ignore[attr-defined]

    _populate_order_product_names(orders, db)
    return orders


@router.get("/{order_id}", response_model=Order)
def get_order(
    order_id: int,
    current_user_email: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Obtener una orden por ID (solo el propietario puede verla)."""
    user = db.query(User).filter(User.email == current_user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    
    is_buyer = order.user_id == user.id
    
    is_seller = False
    products_in_order = order.products or []
    product_ids = [p.get("productId") for p in products_in_order if p.get("productId")]
    if product_ids:
        seller_store = db.query(Store).filter(Store.user_id == user.id).first()
        if seller_store:
            matching = db.query(Product).filter(
                Product.id.in_(product_ids),
                Product.store_id == seller_store.id
            ).first()
            if matching:
                is_seller = True

    if not is_buyer and not is_seller:
        raise HTTPException(status_code=403, detail="Sin acceso a esta orden")

    dc = db.query(DeliveryCode).filter(DeliveryCode.order_id == order.id).first()
    if is_buyer:
        order.delivery_code = dc.code if dc else None  # type: ignore[attr-defined]
    else:
        order.delivery_code = None  # type: ignore[attr-defined]
        
    order.client_name = order.user.name if order.user else None  # type: ignore[attr-defined]
    order.client_email = order.user.email if order.user else None  # type: ignore[attr-defined]
    _populate_order_product_names(order, db)
    return order


@router.put("/{order_id}", response_model=Order)
def update_order_status(
    order_id: int,
    status: str,
    current_user_email: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Actualizar estado de una orden."""
    user = db.query(User).filter(User.email == current_user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    if order.user_id != user.id:
        raise HTTPException(status_code=403, detail="Sin acceso a esta orden")

    order.status = status
    order.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(order)

    dc = db.query(DeliveryCode).filter(DeliveryCode.order_id == order.id).first()
    order.delivery_code = dc.code if dc else None  # type: ignore[attr-defined]
    order.client_name = order.user.name if order.user else None  # type: ignore[attr-defined]
    order.client_email = order.user.email if order.user else None  # type: ignore[attr-defined]
    _populate_order_product_names(order, db)
    return order


@router.delete("/{order_id}")
def cancel_order(
    order_id: int,
    current_user_email: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Cancelar una orden."""
    user = db.query(User).filter(User.email == current_user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    if order.user_id != user.id:
        raise HTTPException(status_code=403, detail="Sin acceso a esta orden")

    if order.status in ("canceled", "completed"):
        raise HTTPException(status_code=400, detail="No se puede cancelar un pedido ya finalizado o cancelado")

    # Restaurar stock
    products_in_order = order.products or []
    for item in products_in_order:
        p_id = item.get("productId")
        qty = item.get("quantity")
        if p_id and qty:
            prod = db.query(Product).filter(Product.id == p_id).first()
            if prod and prod.stock is not None:
                prod.stock += qty

    order.status = "canceled"
    order.updated_at = datetime.utcnow()
    db.commit()
    return {"message": "Orden cancelada"}
