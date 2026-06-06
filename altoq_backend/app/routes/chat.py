from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.chat import Chat, Message
from ..models.user import User
from ..models.product import Product
from ..schemas.chat import ChatCreate, ChatResponse, MessageCreate, MessageResponse
from ..dependencies import get_current_user

router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.post("/start", response_model=ChatResponse)
def start_chat(
    chat_data: ChatCreate,
    current_user: User = Depends(get_current_user),
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
        return existing_chat
    
    # Crear nuevo chat
    new_chat = Chat(
        buyer_id=current_user.id,
        seller_id=chat_data.seller_id,
        product_id=chat_data.product_id
    )
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)
    
    return new_chat

@router.get("/my-chats", response_model=List[ChatResponse])
def get_my_chats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener todos los chats del usuario (como comprador o vendedor)"""
    chats = db.query(Chat).filter(
        (Chat.buyer_id == current_user.id) | (Chat.seller_id == current_user.id),
        Chat.is_active == True
    ).order_by(Chat.updated_at.desc()).all()
    return chats

@router.get("/{chat_id}", response_model=ChatResponse)
def get_chat(
    chat_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obener detalles de un chat específico"""
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat no encontrado")
    
    # Verificar que el usuario es parte del chat
    if chat.buyer_id != current_user.id and chat.seller_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes acceso a este chat")
    
    return chat

@router.get("/{chat_id}/messages", response_model=List[MessageResponse])
def get_chat_messages(
    chat_id: int,
    current_user: User = Depends(get_current_user),
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
    current_user: User = Depends(get_current_user),
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
    current_user: User = Depends(get_current_user),
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
