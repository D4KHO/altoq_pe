from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random
import string
from ..database import get_db
from ..models.delivery_code import DeliveryCode
from ..models.order import Order
from ..models.user import User
from ..schemas.delivery import DeliveryCodeResponse, DeliveryValidation
from ..dependencies import get_current_user

router = APIRouter(prefix="/api/delivery", tags=["delivery"])

def generate_delivery_code(length=6):
    """Generar un código alfanumérico único"""
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

@router.post("/generate/{order_id}", response_model=DeliveryCodeResponse)
def generate_delivery_code(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generar un código de entrega para un pedido"""
    # Verificar que el pedido existe
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    # Verificar que el usuario es el comprador
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes acceso a este pedido")
    
    # Verificar que el pedido esté en estado apropiado
    if order.status not in ["pending", "confirmed"]:
        raise HTTPException(status_code=400, detail="Solo se pueden generar códigos para pedidos pendientes o confirmados")
    
    # Verificar que no exista ya un código para este pedido
    existing_code = db.query(DeliveryCode).filter(DeliveryCode.order_id == order_id).first()
    if existing_code:
        return existing_code
    
    # Generar código único
    code = generate_delivery_code()
    
    # Verificar que el código no exista
    while db.query(DeliveryCode).filter(DeliveryCode.code == code).first():
        code = generate_delivery_code()
    
    # Crear código de entrega (expira en 24 horas)
    new_delivery_code = DeliveryCode(
        order_id=order_id,
        code=code,
        expires_at=datetime.utcnow() + timedelta(hours=24)
    )
    db.add(new_delivery_code)
    db.commit()
    db.refresh(new_delivery_code)
    
    return new_delivery_code

@router.post("/validate", response_model=dict)
def validate_delivery_code(
    validation_data: DeliveryValidation,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Validar un código de entrega"""
    # Buscar el código
    delivery_code = db.query(DeliveryCode).filter(
        DeliveryCode.code == validation_data.code
    ).first()
    
    if not delivery_code:
        raise HTTPException(status_code=404, detail="Código de entrega no encontrado")
    
    # Verificar que el código no haya sido usado
    if delivery_code.is_used:
        raise HTTPException(status_code=400, detail="Este código ya fue utilizado")
    
    # Verificar que el código no haya expirado
    if delivery_code.expires_at and delivery_code.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Este código ha expirado")
    
    # Verificar que el usuario es el vendedor del pedido
    order = delivery_code.order
    # TODO: Verificar que el usuario es el vendedor del producto
    
    # Marcar código como usado
    delivery_code.is_used = True
    delivery_code.used_at = datetime.utcnow()
    
    # Actualizar estado del pedido
    order.status = "completed"
    order.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "message": "Código validado exitosamente",
        "order_id": order.id,
        "validated_at": delivery_code.used_at
    }

@router.get("/order/{order_id}", response_model=DeliveryCodeResponse)
def get_delivery_code_by_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener el código de entrega de un pedido"""
    # Verificar que el pedido existe
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    # Verificar que el usuario es el comprador
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes acceso a este pedido")
    
    # Buscar el código de entrega
    delivery_code = db.query(DeliveryCode).filter(DeliveryCode.order_id == order_id).first()
    if not delivery_code:
        raise HTTPException(status_code=404, detail="No hay código de entrega para este pedido")
    
    return delivery_code
