from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.store import Store
from ..models.product import Product as ProductModel
from ..schemas.store import StorePublicResponse
from ..schemas.product import ProductResponse as Product

router = APIRouter(prefix="/api/stores", tags=["stores"])


@router.get("/{store_id}", response_model=StorePublicResponse)
def get_public_store(store_id: int, db: Session = Depends(get_db)):
    """Obtener información pública de una tienda por ID (sin autenticación)"""
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Tienda no encontrada")
    return store


@router.get("/{store_id}/products", response_model=List[Product])
def get_store_products(store_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Obtener los productos de una tienda (sin autenticación)"""
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Tienda no encontrada")
    products = (
        db.query(ProductModel)
        .filter(ProductModel.store_id == store_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return products
