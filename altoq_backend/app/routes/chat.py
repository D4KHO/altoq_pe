from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.chat import Chat, Message
from ..models.user import User
from ..models.product import Product
from ..schemas.chat import ChatCreate, ChatForOrderCreate, ChatResponse, MessageCreate, MessageResponse
from ..dependencies import get_current_user

router = APIRouter(prefix="/api/chat", tags=["chat"])


def _populate_chat_metadata(chat: Chat) -> Chat:
    chat.buyer_name = chat.buyer.name if chat.buyer else None
    chat.seller_name = chat.seller.name if chat.seller else None
    chat.product_name = chat.product.name if chat.product else None
    chat.product_image = chat.product.image if chat.product else None
    return chat


def get_current_user_model(
    current_user_email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> User:
    user = db.query(User).filter(User.email == current_user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


@router.post("/start", response_model=ChatResponse)
def start_chat(
    chat_data: ChatCreate,
    current_user: User = Depends(get_current_user_model),
    db: Session = Depends(get_db)
):
    """Iniciar un nuevo chat entre comprador y vendedor"""
    # Verificar que el producto existe
    product = db.query(Product).filter(Product.id == chat_data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    # Verificar que no exista ya un chat activo para este producto entre estos usuarios
    existing_chat = db.query(Chat).filter(
        Chat.buyer_id == current_user.id,
        Chat.product_id == chat_data.product_id,
        Chat.is_active == True
    ).first()
    
    if existing_chat:
        return _populate_chat_metadata(existing_chat)
    
    # Crear nuevo chat
    new_chat = Chat(
        buyer_id=current_user.id,
        seller_id=chat_data.seller_id,
        product_id=chat_data.product_id
    )
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)
    
    return _populate_chat_metadata(new_chat)

@router.post("/start-for-order", response_model=ChatResponse)
def start_chat_for_order(
    chat_data: ChatForOrderCreate,
    current_user: User = Depends(get_current_user_model),
    db: Session = Depends(get_db)
):
    """Iniciar o recuperar un chat de soporte vinculado a un pedido específico.
    El seller_id se resuelve automáticamente desde la tienda del producto.
    """
    from ..models.order import Order
    from ..models.store import Store
    from datetime import datetime

    product = db.query(Product).filter(Product.id == chat_data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    # Verificar que la orden existe y pertenece al usuario
    order = db.query(Order).filter(Order.id == chat_data.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Sin acceso a esta orden")

    # Resolver seller_id desde la tienda del producto
    seller_id = chat_data.seller_id
    if not seller_id and product.store_id:
        store = db.query(Store).filter(Store.id == product.store_id).first()
        if store and store.user_id:
            seller_id = store.user_id

    if not seller_id:
        raise HTTPException(status_code=400, detail="No se pudo determinar el vendedor de este producto")

    # Si ya existe un chat activo para este pedido+producto, devolverlo
    existing_chat = db.query(Chat).filter(
        Chat.buyer_id == current_user.id,
        Chat.order_id == chat_data.order_id,
        Chat.product_id == chat_data.product_id,
        Chat.is_active == True
    ).first()

    if existing_chat:
        return _populate_chat_metadata(existing_chat)

    new_chat = Chat(
        buyer_id=current_user.id,
        seller_id=seller_id,
        product_id=chat_data.product_id,
        order_id=chat_data.order_id,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)
    return _populate_chat_metadata(new_chat)

@router.get("/my-chats", response_model=List[ChatResponse])
def get_my_chats(
    current_user: User = Depends(get_current_user_model),
    db: Session = Depends(get_db)
):
    """Obtener todos los chats del usuario (como comprador o vendedor)"""
    chats = db.query(Chat).filter(
        (Chat.buyer_id == current_user.id) | (Chat.seller_id == current_user.id),
        Chat.is_active == True
    ).order_by(Chat.updated_at.desc()).all()
    
    active_chats = []
    chats_to_deactivate = False
    for chat in chats:
        if chat.order and chat.order.status == "canceled":
            chat.is_active = False
            chats_to_deactivate = True
            continue
        _populate_chat_metadata(chat)
        active_chats.append(chat)
        
    if chats_to_deactivate:
        db.commit()
        
    return active_chats

@router.get("/{chat_id}", response_model=ChatResponse)
def get_chat(
    chat_id: int,
    current_user: User = Depends(get_current_user_model),
    db: Session = Depends(get_db)
):
    """Obener detalles de un chat específico"""
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat no encontrado")
    
    # Verificar que el usuario es parte del chat
    if chat.buyer_id != current_user.id and chat.seller_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes acceso a este chat")
    
    return _populate_chat_metadata(chat)

@router.get("/{chat_id}/messages", response_model=List[MessageResponse])
def get_chat_messages(
    chat_id: int,
    current_user: User = Depends(get_current_user_model),
    db: Session = Depends(get_db)
):
    """Obtener mensajes de un chat"""
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat no encontrado")
    
    # Verificar que el usuario es parte del chat
    if chat.buyer_id != current_user.id and chat.seller_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes acceso a este chat")
    
    messages = db.query(Message).filter(Message.chat_id == chat_id).order_by(Message.created_at.asc()).all()
    
    # Marcar mensajes como leídos si el usuario es el receptor
    for message in messages:
        if message.sender_id != current_user.id and not message.is_read:
            message.is_read = True
    
    db.commit()
    
    return messages

@router.post("/{chat_id}/messages", response_model=MessageResponse)
def send_message(
    chat_id: int,
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user_model),
    db: Session = Depends(get_db)
):
    """Enviar un mensaje en un chat"""
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat no encontrado")
    
    # Verificar que el usuario es parte del chat
    if chat.buyer_id != current_user.id and chat.seller_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes acceso a este chat")
    
    # Verificar que el chat esté activo
    if not chat.is_active:
        raise HTTPException(status_code=400, detail="Este chat está cerrado")
    
    # Crear mensaje
    new_message = Message(
        chat_id=chat_id,
        sender_id=current_user.id,
        content=message_data.content
    )
    db.add(new_message)
    
    # Actualizar timestamp del chat
    chat.updated_at = new_message.created_at
    
    db.commit()
    db.refresh(new_message)
    
    return new_message

@router.post("/{chat_id}/close")
def close_chat(
    chat_id: int,
    current_user: User = Depends(get_current_user_model),
    db: Session = Depends(get_db)
):
    """Cerrar un chat (solo disponible después de validar entrega)"""
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat no encontrado")
    
    # Verificar que el usuario es parte del chat
    if chat.buyer_id != current_user.id and chat.seller_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes acceso a este chat")
    
    # Verificar que el pedido esté completado
    if not chat.order_id:
        raise HTTPException(status_code=400, detail="No se puede cerrar un chat sin pedido asociado")
    
    order = chat.order
    if order.status != "completed":
        raise HTTPException(status_code=400, detail="Solo se pueden cerrar chats de pedidos completados")
    
    chat.is_active = False
    db.commit()
    
    return {"message": "Chat cerrado exitosamente"}

from pydantic import BaseModel
from typing import Optional

class ChatInquiryCreate(BaseModel):
    store_id: int
    name: str
    email: str
    phone: Optional[str] = None
    message: str

@router.post("/inquiry")
def create_store_inquiry(
    inquiry_data: ChatInquiryCreate,
    db: Session = Depends(get_db)
):
    """Crear un chat de consulta general para una tienda desde el formulario de contacto"""
    from ..models.store import Store
    from ..models.user import User as UserModel
    from datetime import datetime
    import hashlib

    # 1. Obtener la tienda y el vendedor
    store = db.query(Store).filter(Store.id == inquiry_data.store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Tienda no encontrada")
    
    seller_id = store.user_id
    if not seller_id:
        raise HTTPException(status_code=400, detail="La tienda no tiene un vendedor asignado")

    # 2. Buscar o crear el usuario comprador (usando el email)
    buyer = db.query(UserModel).filter(UserModel.email == inquiry_data.email).first()
    if not buyer:
        # Si no existe, crear un usuario temporal
        temp_password_hash = hashlib.sha256(b"guest12345").hexdigest()
        buyer = UserModel(
            email=inquiry_data.email,
            name=inquiry_data.name,
            password=temp_password_hash,
            phone=inquiry_data.phone,
            role="buyer"
        )
        db.add(buyer)
        db.commit()
        db.refresh(buyer)

    # 3. Crear el chat
    new_chat = Chat(
        buyer_id=buyer.id,
        seller_id=seller_id,
        product_id=None,  # No está asociado a un producto específico
        order_id=None,    # No está asociado a un pedido
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)

    # 4. Crear el primer mensaje en el chat
    new_message = Message(
        chat_id=new_chat.id,
        sender_id=buyer.id,
        content=inquiry_data.message,
        is_read=False,
        created_at=datetime.utcnow()
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)

    return {"message": "Consulta enviada exitosamente", "chat_id": new_chat.id}

