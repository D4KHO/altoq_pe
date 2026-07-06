from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.user import User
from ..models.store import Store
from ..models.order import Order as OrderModel
from ..models.product import Product
from ..models.delivery_code import DeliveryCode
from ..schemas.user import UserUpdate, UserRole
from ..schemas.store import StoreCreate, StoreResponse, StoreUpdate
from ..schemas.order import Order as OrderSchema
from ..dependencies import get_current_user
from .orders import _populate_order_product_names
from .stores import _calculate_store_rating_and_sales

router = APIRouter(prefix="/api/seller", tags=["seller"])

@router.post("/become-seller")
def become_seller(
    store_data: StoreCreate,
    current_user_email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Permite a un usuario normal convertirse en vendedor creando una tienda"""
    user = db.query(User).filter(User.email == current_user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Verificar si el usuario ya tiene una tienda
    existing_store = db.query(Store).filter(Store.user_id == user.id).first()
    if existing_store:
        raise HTTPException(status_code=400, detail="El usuario ya tiene una tienda")
    
    # Crear la tienda
    store_data_dict = store_data.dict()
    store_data_dict['user_id'] = user.id
    
    new_store = Store(**store_data_dict)
    db.add(new_store)
    
    # Actualizar el rol del usuario
    if user.role == UserRole.BUYER:
        user.role = UserRole.BOTH
    elif user.role == UserRole.SELLER:
        user.role = UserRole.BOTH
    
    db.commit()
    db.refresh(new_store)
    
    return {"message": "Tienda creada exitosamente", "store": StoreResponse.model_validate(new_store)}

@router.put("/switch-role")
def switch_role(
    role: str,
    current_user_email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Permite cambiar entre rol de comprador y vendedor"""
    user = db.query(User).filter(User.email == current_user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Verificar que el usuario tenga el rol BOTH
    if user.role != UserRole.BOTH:
        raise HTTPException(status_code=400, detail="Solo usuarios con rol BOTH pueden cambiar de rol")
    
    # Cambiar el rol activo
    if role == "buyer":
        user.role = UserRole.BUYER
    elif role == "seller":
        user.role = UserRole.SELLER
    else:
        raise HTTPException(status_code=400, detail="Rol inválido. Use 'buyer' o 'seller'")
    
    db.commit()
    db.refresh(user)
    
    return {"message": f"Rol cambiado a {role}", "role": user.role}

def _calculate_seller_unique_clients(db: Session, store_id: int) -> int:
    completed_orders = db.query(OrderModel).filter(OrderModel.status == "completed").all()
    client_ids = set()
    for order in completed_orders:
        products_json = order.products or []
        for p in products_json:
            if isinstance(p, dict):
                p_id = p.get("productId")
                if p_id:
                    prod = db.query(Product).filter(Product.id == p_id).first()
                    if prod and prod.store_id == store_id:
                        client_ids.add(order.user_id)
    return len(client_ids)


@router.get("/my-store")
def get_my_store(
    current_user_email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtiene la tienda del usuario actual"""
    user = db.query(User).filter(User.email == current_user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    store = db.query(Store).filter(Store.user_id == user.id).first()
    if not store:
        raise HTTPException(status_code=404, detail="El usuario no tiene una tienda")
    
    rating, rating_count, sales = _calculate_store_rating_and_sales(db, store.id)
    clients = _calculate_seller_unique_clients(db, store.id)
    store.rating = rating
    store.rating_count = rating_count
    store.sales = sales
    store.clients = clients
    return StoreResponse.model_validate(store)


@router.put("/my-store", response_model=StoreResponse)
def update_my_store(
    store_data: StoreUpdate,
    current_user_email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Permite al vendedor actualizar la información de su tienda"""
    user = db.query(User).filter(User.email == current_user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
    store = db.query(Store).filter(Store.user_id == user.id).first()
    if not store:
        raise HTTPException(status_code=404, detail="No tienes una tienda registrada")

    # Actualizar campos
    for key, value in store_data.dict(exclude_unset=True).items():
        setattr(store, key, value)

    db.commit()
    db.refresh(store)
    
    rating, rating_count, sales = _calculate_store_rating_and_sales(db, store.id)
    clients = _calculate_seller_unique_clients(db, store.id)
    store.rating = rating
    store.rating_count = rating_count
    store.sales = sales
    store.clients = clients
    return StoreResponse.model_validate(store)


@router.put("/my-store/auto-confirm", response_model=StoreResponse)
def update_auto_confirm(
    auto_confirm: bool,
    current_user_email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Permite al vendedor activar o desactivar la confirmación automática de pedidos"""
    user = db.query(User).filter(User.email == current_user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
    store = db.query(Store).filter(Store.user_id == user.id).first()
    if not store:
        raise HTTPException(status_code=404, detail="No tienes una tienda registrada")
        
    store.auto_confirm_orders = auto_confirm
    db.commit()
    db.refresh(store)
    
    return StoreResponse.model_validate(store)


@router.get("/orders", response_model=List[OrderSchema])
def get_seller_orders(
    current_user_email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener los pedidos que contienen productos de la tienda del vendedor"""
    user = db.query(User).filter(User.email == current_user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
    store = db.query(Store).filter(Store.user_id == user.id).first()
    if not store:
        raise HTTPException(status_code=404, detail="No tienes una tienda registrada")
        
    store_products = db.query(Product).filter(Product.store_id == store.id).all()
    product_ids = [p.id for p in store_products]
    
    if not product_ids:
        return []
        
    all_orders = db.query(OrderModel).order_by(OrderModel.created_at.desc()).all()
    
    seller_orders = []
    for order in all_orders:
        order_products = order.products or []
        has_seller_product = any(
            p.get("productId") in product_ids for p in order_products
        )
        if has_seller_product:
            order.delivery_code = None  # type: ignore
            order.client_name = order.user.name if order.user else None  # type: ignore
            order.client_email = order.user.email if order.user else None  # type: ignore
            seller_orders.append(order)
            
    _populate_order_product_names(seller_orders, db)
    return seller_orders


@router.put("/orders/{order_id}/cancel")
def cancel_seller_order(
    order_id: int,
    current_user_email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Permite a un vendedor cancelar un pedido que contenga sus productos"""
    from datetime import datetime

    user = db.query(User).filter(User.email == current_user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
    store = db.query(Store).filter(Store.user_id == user.id).first()
    if not store:
        raise HTTPException(status_code=404, detail="No tienes una tienda registrada")
        
    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
        
    # Verificar si el pedido contiene algún producto de la tienda del vendedor
    store_products = db.query(Product).filter(Product.store_id == store.id).all()
    product_ids = [p.id for p in store_products]
    
    order_products = order.products or []
    has_seller_product = any(
        p.get("productId") in product_ids for p in order_products
    )
    
    if not has_seller_product:
        raise HTTPException(status_code=403, detail="No tienes permiso para cancelar este pedido")
        
    if order.status in ("canceled", "completed"):
        raise HTTPException(status_code=400, detail="El pedido ya está finalizado o cancelado")

    # Restaurar stock
    for item in order_products:
        p_id = item.get("productId")
        qty = item.get("quantity")
        if p_id and qty:
            prod = db.query(Product).filter(Product.id == p_id).first()
            if prod and prod.stock is not None:
                prod.stock += qty

    # Cancelar el pedido
    order.status = "canceled"
    order.updated_at = datetime.utcnow()
    
    # Desactivar chats activos asociados a este pedido
    from ..models.chat import Chat
    active_chats = db.query(Chat).filter(Chat.order_id == order_id, Chat.is_active == True).all()
    for chat in active_chats:
        chat.is_active = False
        
    db.commit()
    
    return {"message": "Pedido cancelado exitosamente", "status": order.status}


@router.put("/orders/{order_id}/confirm", response_model=OrderSchema)
def confirm_seller_order(
    order_id: int,
    current_user_email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Permite a un vendedor confirmar/aceptar un pedido que contenga sus productos"""
    from datetime import datetime

    user = db.query(User).filter(User.email == current_user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
    store = db.query(Store).filter(Store.user_id == user.id).first()
    if not store:
        raise HTTPException(status_code=404, detail="No tienes una tienda registrada")
        
    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
        
    # Verificar si el pedido contiene algún producto de la tienda del vendedor
    store_products = db.query(Product).filter(Product.store_id == store.id).all()
    product_ids = [p.id for p in store_products]
    
    order_products = order.products or []
    has_seller_product = any(
        p.get("productId") in product_ids for p in order_products
    )
    
    if not has_seller_product:
        raise HTTPException(status_code=403, detail="No tienes permiso para confirmar este pedido")
        
    if order.status != "pending":
        raise HTTPException(status_code=400, detail="Solo se pueden confirmar pedidos en estado pendiente")
        
    # Confirmar el pedido
    order.status = "confirmed"
    order.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(order)
    
    # Adjuntar código de entrega, cliente, etc.
    dc = db.query(DeliveryCode).filter(DeliveryCode.order_id == order.id).first()
    order.delivery_code = dc.code if dc else None
    order.client_name = order.user.name if order.user else None
    order.client_email = order.user.email if order.user else None
    
    _populate_order_product_names(order, db)
    return order

import uuid
import shutil
import os
from fastapi import File, UploadFile, Request
from pydantic import BaseModel

@router.post("/upload-temp-image")
def upload_temp_image(
    request: Request,
    file: UploadFile = File(...),
    current_user_email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == current_user_email).first()
    store = db.query(Store).filter(Store.user_id == user.id).first()
    
    if not store:
        raise HTTPException(status_code=404, detail="No tienes una tienda registrada")

    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen válida")

    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"temp_{store.id}_{uuid.uuid4().hex}{file_extension}"
    file_path = f"static/uploads/products/{unique_filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    base_url = str(request.base_url).rstrip("/")
    public_url = f"{base_url}/static/uploads/products/{unique_filename}"
    return {"message": "Imagen subida exitosamente", "image_url": public_url}




