from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models.user import User as UserModel
from ..models.address import Address as AddressModel
from ..schemas.user import User, UserUpdate, PasswordChange
from ..schemas.address import Address, AddressCreate, AddressUpdate
from ..utils.security import get_current_user, verify_password, get_password_hash

router = APIRouter(prefix="/api/users", tags=["users"])

def get_user_from_token(authorization: str = Header(...), db: Session = Depends(get_db)) -> UserModel:
    """Extract user from Authorization header"""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    
    token = authorization.replace("Bearer ", "")
    email = get_current_user(token)
    
    user = db.query(UserModel).filter(UserModel.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

# ===== USER PROFILE ENDPOINTS =====

@router.get("/me", response_model=User)
def get_my_profile(current_user: UserModel = Depends(get_user_from_token)):
    """Get current user profile"""
    return current_user

@router.put("/me", response_model=User)
def update_my_profile(
    user_update: UserUpdate,
    current_user: UserModel = Depends(get_user_from_token),
    db: Session = Depends(get_db)
):
    """Update current user profile"""
    update_data = user_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    return current_user

@router.put("/me/password")
def change_password(
    password_data: PasswordChange,
    current_user: UserModel = Depends(get_user_from_token),
    db: Session = Depends(get_db)
):
    """Change user password"""
    # Verify old password
    if not verify_password(password_data.old_password, current_user.password):
        raise HTTPException(status_code=400, detail="Incorrect current password")
    
    # Update password
    current_user.password = get_password_hash(password_data.new_password)
    db.commit()
    
    return {"message": "Password updated successfully"}

# ===== ADDRESS MANAGEMENT ENDPOINTS =====

@router.get("/me/addresses", response_model=List[Address])
def get_my_addresses(current_user: UserModel = Depends(get_user_from_token)):
    """Get all addresses for current user"""
    return current_user.addresses

@router.post("/me/addresses", response_model=Address)
def create_address(
    address: AddressCreate,
    current_user: UserModel = Depends(get_user_from_token),
    db: Session = Depends(get_db)
):
    """Create a new address for current user"""
    # If this is set as default, unset other defaults
    if address.is_default:
        db.query(AddressModel).filter(
            AddressModel.user_id == current_user.id,
            AddressModel.is_default == True
        ).update({"is_default": False})
    
    db_address = AddressModel(
        **address.dict(),
        user_id=current_user.id
    )
    db.add(db_address)
    db.commit()
    db.refresh(db_address)
    
    return db_address

@router.put("/me/addresses/{address_id}", response_model=Address)
def update_address(
    address_id: int,
    address_update: AddressUpdate,
    current_user: UserModel = Depends(get_user_from_token),
    db: Session = Depends(get_db)
):
    """Update an address"""
    db_address = db.query(AddressModel).filter(
        AddressModel.id == address_id,
        AddressModel.user_id == current_user.id
    ).first()
    
    if not db_address:
        raise HTTPException(status_code=404, detail="Address not found")
    
    update_data = address_update.dict(exclude_unset=True)
    
    # If setting as default, unset other defaults
    if update_data.get("is_default"):
        db.query(AddressModel).filter(
            AddressModel.user_id == current_user.id,
            AddressModel.id != address_id,
            AddressModel.is_default == True
        ).update({"is_default": False})
    
    for field, value in update_data.items():
        setattr(db_address, field, value)
    
    db.commit()
    db.refresh(db_address)
    
    return db_address

@router.delete("/me/addresses/{address_id}")
def delete_address(
    address_id: int,
    current_user: UserModel = Depends(get_user_from_token),
    db: Session = Depends(get_db)
):
    """Delete an address"""
    db_address = db.query(AddressModel).filter(
        AddressModel.id == address_id,
        AddressModel.user_id == current_user.id
    ).first()
    
    if not db_address:
        raise HTTPException(status_code=404, detail="Address not found")
    
    db.delete(db_address)
    db.commit()
    
    return {"message": "Address deleted successfully"}
