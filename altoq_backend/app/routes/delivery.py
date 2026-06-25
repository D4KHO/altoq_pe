from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random
import string
from ..database import get_db
from ..models.delivery_code import DeliveryCode
from ..models.order import Order
from ..models.product import Product
from ..models.store import Store
from ..models.user import User
from ..schemas.delivery import DeliveryCodeResponse, DeliveryValidation, DeliveryLocationUpdate, DeliveryStart, DeliveryTrackingResponse
from ..dependencies import get_current_user
import secrets

router = APIRouter(prefix="/api/delivery", tags=["delivery"])


def _generate_code(length: int = 6) -> str:
    """Generar un código alfanumérico único."""
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


@router.post("/generate/{order_id}", response_model=DeliveryCodeResponse)
def generate_delivery_code_endpoint(
    order_id: int,
    current_user_email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generar (o recuperar) un código de entrega para un pedido."""
    user = db.query(User).filter(User.email == current_user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    if order.user_id != user.id:
        raise HTTPException(status_code=403, detail="No tienes acceso a este pedido")

    # Si ya existe, devolverlo
    existing_code = db.query(DeliveryCode).filter(DeliveryCode.order_id == order_id).first()
    if existing_code:
        return existing_code

    # Generar código único
    code = _generate_code()
    while db.query(DeliveryCode).filter(DeliveryCode.code == code).first():
        code = _generate_code()

    new_delivery_code = DeliveryCode(
        order_id=order_id,
        code=code,
        is_used=False,
        created_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(days=30),
    )
    db.add(new_delivery_code)
    db.commit()
    db.refresh(new_delivery_code)

    return new_delivery_code


@router.post("/validate", response_model=dict)
def validate_delivery_code(
    validation_data: DeliveryValidation,
    current_user_email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Validar un código de entrega.
    Solo el vendedor de algún producto en la orden puede validarlo.
    Al validar: marca el código como usado y actualiza la orden a 'completed'.
    """
    user = db.query(User).filter(User.email == current_user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    delivery_code = db.query(DeliveryCode).filter(
        DeliveryCode.code == validation_data.code
    ).first()

    if not delivery_code:
        raise HTTPException(status_code=404, detail="Código de entrega no encontrado")

    if delivery_code.is_used:
        raise HTTPException(status_code=400, detail="Este código ya fue utilizado")

    if delivery_code.expires_at and delivery_code.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Este código ha expirado")

    order = delivery_code.order
    if not order:
        raise HTTPException(status_code=404, detail="Orden asociada no encontrada")

    # Verificar que el usuario es vendedor de al menos un producto de la orden
    products_in_order = order.products or []
    product_ids = [p.get("productId") for p in products_in_order if p.get("productId")]

    is_seller = False
    if product_ids:
        seller_store = db.query(Store).filter(Store.user_id == user.id).first()
        if seller_store:
            matching = db.query(Product).filter(
                Product.id.in_(product_ids),
                Product.store_id == seller_store.id
            ).first()
            if matching:
                is_seller = True

    if not is_seller:
        raise HTTPException(
            status_code=403,
            detail="No eres el vendedor de ningún producto en esta orden"
        )

    # Marcar código como usado y completar la orden
    delivery_code.is_used = True
    delivery_code.used_at = datetime.utcnow()
    order.status = "completed"
    order.delivery_status = "completed"
    order.updated_at = datetime.utcnow()

    db.commit()

    return {
        "message": "Código validado exitosamente. La entrega ha sido confirmada.",
        "order_id": order.id,
        "validated_at": delivery_code.used_at.isoformat(),
        "order_status": "completed"
    }


@router.get("/order/{order_id}", response_model=DeliveryCodeResponse)
def get_delivery_code_by_order(
    order_id: int,
    current_user_email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener el código de entrega de un pedido (solo el comprador)."""
    user = db.query(User).filter(User.email == current_user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    if order.user_id != user.id:
        raise HTTPException(status_code=403, detail="No tienes acceso a este pedido")

    delivery_code = db.query(DeliveryCode).filter(DeliveryCode.order_id == order_id).first()
    if not delivery_code:
        raise HTTPException(status_code=404, detail="No hay código de entrega para este pedido")

    return delivery_code


@router.post("/start/{order_id}", response_model=dict)
def start_delivery(
    order_id: int,
    start_data: DeliveryStart,
    current_user_email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Iniciar la entrega de un pedido.
    Solo el vendedor de algún producto de la orden puede iniciarla.
    Genera un token de rastreo temporal público.
    """
    user = db.query(User).filter(User.email == current_user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    if order.status in ("completed", "canceled"):
        raise HTTPException(status_code=400, detail="No se puede iniciar la entrega de un pedido completado o cancelado")

    # Verificar que el usuario es vendedor de al menos un producto de la orden
    products_in_order = order.products or []
    product_ids = [p.get("productId") for p in products_in_order if p.get("productId")]

    is_seller = False
    if product_ids:
        seller_store = db.query(Store).filter(Store.user_id == user.id).first()
        if seller_store:
            matching = db.query(Product).filter(
                Product.id.in_(product_ids),
                Product.store_id == seller_store.id
            ).first()
            if matching:
                is_seller = True

    if not is_seller:
        raise HTTPException(
            status_code=403,
            detail="No eres el vendedor de ningún producto en esta orden"
        )

    # Generar token si no tiene uno
    if not order.delivery_token:
        order.delivery_token = secrets.token_hex(16)

    # Actualizar coordenadas de inicio
    if start_data.latitude is not None and start_data.longitude is not None:
        order.delivery_latitude = start_data.latitude
        order.delivery_longitude = start_data.longitude

    order.delivery_status = "delivering"
    order.status = "delivering"  # Actualizar estado de orden
    order.updated_at = datetime.utcnow()
    db.commit()

    return {
        "message": "Entrega iniciada con éxito",
        "delivery_token": order.delivery_token,
        "delivery_status": "delivering"
    }


@router.post("/update-location/{order_id}", response_model=dict)
def update_delivery_location(
    order_id: int,
    location: DeliveryLocationUpdate,
    current_user_email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualizar la ubicación en tiempo real del repartidor (vendedor).
    """
    user = db.query(User).filter(User.email == current_user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    # Verificar que el usuario es vendedor de al menos un producto de la orden
    products_in_order = order.products or []
    product_ids = [p.get("productId") for p in products_in_order if p.get("productId")]

    is_seller = False
    if product_ids:
        seller_store = db.query(Store).filter(Store.user_id == user.id).first()
        if seller_store:
            matching = db.query(Product).filter(
                Product.id.in_(product_ids),
                Product.store_id == seller_store.id
            ).first()
            if matching:
                is_seller = True

    if not is_seller:
        raise HTTPException(
            status_code=403,
            detail="No eres el vendedor de ningún producto en esta orden"
        )

    order.delivery_latitude = location.latitude
    order.delivery_longitude = location.longitude
    order.updated_at = datetime.utcnow()
    db.commit()

    return {"message": "Ubicación actualizada"}


@router.get("/track/{token}", response_model=DeliveryTrackingResponse)
def track_delivery_public(
    token: str,
    db: Session = Depends(get_db)
):
    """
    Ruta Pública: Obtener información del seguimiento mediante el token temporal.
    No requiere autenticación.
    """
    order = db.query(Order).filter(Order.delivery_token == token).first()
    if not order:
        raise HTTPException(status_code=404, detail="Seguimiento de entrega no encontrado o token inválido")

    # Encontrar nombre de la tienda del vendedor
    products_in_order = order.products or []
    product_ids = [p.get("productId") for p in products_in_order if p.get("productId")]
    store_name = None
    if product_ids:
        matching_product = db.query(Product).filter(Product.id == product_ids[0]).first()
        if matching_product and matching_product.store_id:
            store = db.query(Store).filter(Store.id == matching_product.store_id).first()
            if store:
                store_name = store.name

    return {
        "order_id": order.id,
        "total_amount": order.total_amount,
        "shipping_address": order.shipping_address,
        "shipping_latitude": order.shipping_latitude,
        "shipping_longitude": order.shipping_longitude,
        "delivery_latitude": order.delivery_latitude,
        "delivery_longitude": order.delivery_longitude,
        "delivery_status": order.delivery_status,
        "client_name": order.user.name if order.user else "Cliente",
        "contact_phone": order.contact_phone,
        "store_name": store_name,
        "products": products_in_order
    }

