from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.order import Order as OrderModel
from ..schemas.order import Order, OrderCreate

router = APIRouter(prefix="/api/orders", tags=["orders"])

@router.post("/", response_model=Order)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    """Crear una nueva orden"""
    # Convertir products a JSON
    products_json = [item.dict() for item in order.products]
    
    db_order = OrderModel(
        user_id=order.user_id,
        products=products_json,
        total_amount=order.total_amount,
        status=order.status,
        shipping_address=order.shipping_address,
        contact_phone=order.contact_phone
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

@router.get("/user", response_model=List[Order])
def get_user_orders(user_id: int = 1, db: Session = Depends(get_db)):
    """Obtener órdenes de un usuario"""
    orders = db.query(OrderModel).filter(OrderModel.user_id == user_id).all()
    return orders

@router.get("/{order_id}", response_model=Order)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """Obtener una orden por ID"""
    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    return order

@router.put("/{order_id}", response_model=Order)
def update_order_status(order_id: int, status: str, db: Session = Depends(get_db)):
    """Actualizar estado de una orden"""
    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    
    order.status = status
    db.commit()
    db.refresh(order)
    return order

@router.delete("/{order_id}")
def cancel_order(order_id: int, db: Session = Depends(get_db)):
    """Cancelar una orden"""
    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    
    order.status = "canceled"
    db.commit()
    return {"message": "Orden cancelada"}
