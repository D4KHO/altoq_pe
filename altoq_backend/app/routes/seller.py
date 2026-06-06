from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User, UserRole
from ..models.store import Store
from ..schemas.user import UserUpdate
from ..schemas.store import StoreCreate, StoreResponse
from ..dependencies import get_current_user

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
    
    return {"message": "Tienda creada exitosamente", "store": StoreResponse.from_orm(new_store)}

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
    
    return StoreResponse.from_orm(store)
