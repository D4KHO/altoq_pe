from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from ..database import get_db
from ..models.user import User
from ..models.product import Product
from ..models.store import Store
from ..models.chat import Chat
from ..schemas.user import UserResponse
from ..utils.security import verify_token

router = APIRouter(prefix="/api/admin/users", tags=["admin-users"])
security = HTTPBearer()

def verify_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency to verify admin authentication"""
    token = credentials.credentials
    payload = verify_token(token)
    
    if not payload or payload.get("type") != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin authentication required"
        )
    return payload

@router.get("/", response_model=List[UserResponse])
def get_all_users(
    skip: int = 0,
    limit: int = 100,
    admin: dict = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Get list of all users (admin only)"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    admin: dict = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Get user details by ID (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    admin: dict = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Delete a user, their stores and products safely (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    try:
        # 1. Eliminar primero de forma ordenada las tiendas y sus productos
        for store in user.stores:
            # Eliminar todos los productos de esta tienda primero
            db.query(Product).filter(Product.store_id == store.id).delete()
            # Eliminar la tienda
            db.delete(store)
        
        # 2. Eliminar chats donde este usuario participe como comprador o vendedor
        db.query(Chat).filter(
            (Chat.buyer_id == user.id) | (Chat.seller_id == user.id)
        ).delete(synchronize_session=False)

        # 3. Eliminar al usuario físico (las direcciones 'Address' se eliminan en cascada)
        db.delete(user)
        db.commit()
        
    except IntegrityError:
        db.rollback()
        # Si arroja IntegrityError es porque el usuario tiene compras/pedidos registrados (Order.user_id no nullable)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar físicamente al usuario porque tiene un historial de pedidos asociados. Por favor, suspenda su cuenta o su tienda en su lugar para desactivarlo."
        )
    
    return {"message": f"User {user_id} deleted successfully"}
