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
from ..schemas.user import UserResponse, UserCreate, UserUpdate
from ..schemas.address import Address
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

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate,
    admin: dict = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Create a new user (admin only)"""
    db_user = db.query(User).filter(User.email == user_data.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya está registrado."
        )
    
    from ..utils.security import get_password_hash
    hashed_password = get_password_hash(user_data.password)
    
    new_user = User(
        email=user_data.email,
        name=user_data.name,
        password=hashed_password,
        phone=user_data.phone,
        address=user_data.address,
        role=user_data.role.value if hasattr(user_data.role, 'value') else user_data.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    admin: dict = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Update a user's details (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    update_data = user_update.dict(exclude_unset=True)
    if "role" in update_data and update_data["role"] is not None:
        role_val = update_data["role"]
        update_data["role"] = role_val.value if hasattr(role_val, 'value') else role_val

    for field, value in update_data.items():
        setattr(user, field, value)
        
    db.commit()
    db.refresh(user)
    return user

@router.get("/{user_id}/addresses", response_model=List[Address])
def get_user_addresses(
    user_id: int,
    admin: dict = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Get all addresses for a specific user (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return user.addresses

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
