from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.store import Store
from ..schemas.store import StoreResponse, StoreStatusUpdate
from ..utils.security import verify_token

router = APIRouter(prefix="/api/admin/stores", tags=["admin-stores"])
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

@router.get("/", response_model=List[StoreResponse])
def get_all_stores(
    skip: int = 0,
    limit: int = 100,
    admin: dict = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Get list of all stores (admin only)"""
    stores = db.query(Store).offset(skip).limit(limit).all()
    return stores

@router.get("/{store_id}", response_model=StoreResponse)
def get_store(
    store_id: int,
    admin: dict = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Get store details by ID (admin only)"""
    store = db.query(Store).filter(Store.id == store_id).first()
    
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store not found"
        )
    
    return store

@router.patch("/{store_id}/status", response_model=StoreResponse)
def update_store_status(
    store_id: int,
    status_update: StoreStatusUpdate,
    admin: dict = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Update store status (admin only)"""
    store = db.query(Store).filter(Store.id == store_id).first()
    
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store not found"
        )
    
    # Validate status value
    valid_statuses = ['active', 'pending', 'suspended']
    if status_update.status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    store.status = status_update.status
    db.commit()
    db.refresh(store)
    
    return store

@router.delete("/{store_id}")
def delete_store(
    store_id: int,
    admin: dict = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Delete a store (admin only)"""
    store = db.query(Store).filter(Store.id == store_id).first()
    
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store not found"
        )
    
    db.delete(store)
    db.commit()
    
    return {"message": f"Store {store_id} deleted successfully"}
