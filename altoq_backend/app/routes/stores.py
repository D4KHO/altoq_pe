from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from ..database import get_db
from ..models.store import Store
from ..models.product import Product as ProductModel
from ..models.review import Review as ReviewModel
from ..models.order import Order as OrderModel
from ..schemas.store import StorePublicResponse
from ..schemas.product import ProductResponse as Product

router = APIRouter(prefix="/api/stores", tags=["stores"])


def _calculate_store_rating_and_sales(db: Session, store_id: int):
    # 1. Calcular rating promedio y count de reseñas de esta tienda
    stats = db.query(
        func.avg(ReviewModel.store_rating),
        func.count(ReviewModel.id)
    ).filter(ReviewModel.store_id == store_id).first()
    
    avg_rating = stats[0] if stats and stats[0] is not None else 0.0
    rating_count = stats[1] if stats and stats[1] is not None else 0

    # 2. Calcular total de ventas (cantidades de productos en pedidos completados)
    completed_orders = db.query(OrderModel).filter(OrderModel.status == "completed").all()
    sales_count = 0
    for order in completed_orders:
        products_json = order.products or []
        for p in products_json:
            if isinstance(p, dict):
                p_id = p.get("productId")
                if p_id:
                    prod = db.query(ProductModel).filter(ProductModel.id == p_id).first()
                    if prod and prod.store_id == store_id:
                        sales_count += p.get("quantity", 1)

    return round(float(avg_rating), 1), int(rating_count), int(sales_count)


@router.get("", response_model=List[StorePublicResponse])
def get_all_public_stores(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Obtener lista de todas las tiendas activas (público)"""
    stores = db.query(Store).filter(Store.status == "active").offset(skip).limit(limit).all()
    
    # Rellenar métricas dinámicas
    for store in stores:
        rating, rating_count, sales = _calculate_store_rating_and_sales(db, store.id)
        store.rating = rating
        store.rating_count = rating_count
        store.sales = sales
        
    return stores


@router.get("/{store_id}", response_model=StorePublicResponse)
def get_public_store(store_id: int, db: Session = Depends(get_db)):
    """Obtener información pública de una tienda por ID (sin autenticación)"""
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Tienda no encontrada")
        
    rating, rating_count, sales = _calculate_store_rating_and_sales(db, store.id)
    store.rating = rating
    store.rating_count = rating_count
    store.sales = sales
    
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
    
    # Poblar ventas de productos también
    for p in products:
        completed_orders = db.query(OrderModel).filter(OrderModel.status == "completed").all()
        prod_sales = 0
        for order in completed_orders:
            p_json = order.products or []
            for item in p_json:
                if isinstance(item, dict) and item.get("productId") == p.id:
                    prod_sales += item.get("quantity", 1)
        p.sales = prod_sales

    return products
