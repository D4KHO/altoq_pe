from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.product import Product as ProductModel
from ..models.category import Category as CategoryModel
from ..schemas.product import ProductResponse as Product, ProductCreate, ProductUpdate

router = APIRouter(prefix="/api/products", tags=["products"])

@router.get("/category/{slug}", response_model=List[Product])
def get_products_by_category(slug: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Obtener productos por slug de categoría"""
    category = db.query(CategoryModel).filter(CategoryModel.slug == slug).first()
    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    products = db.query(ProductModel).filter(ProductModel.category_id == category.id).offset(skip).limit(limit).all()
    return products

@router.get("/search", response_model=List[Product])
def search_products(q: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Buscar productos por nombre o descripción"""
    if not q:
        return []
    
    search_query = f"%{q}%"
    products = db.query(ProductModel).filter(
        (ProductModel.name.ilike(search_query)) | 
        (ProductModel.description.ilike(search_query))
    ).offset(skip).limit(limit).all()
    return products

@router.get("/", response_model=List[Product])
def get_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Obtener lista de productos"""
    products = db.query(ProductModel).offset(skip).limit(limit).all()
    return products

@router.get("/{product_id}", response_model=Product)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Obtener un producto por ID"""
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product

@router.post("/", response_model=Product)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """Crear un nuevo producto"""
    db_product = ProductModel(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.put("/{product_id}", response_model=Product)
def update_product(product_id: int, product: ProductUpdate, db: Session = Depends(get_db)):
    """Actualizar un producto"""
    db_product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    for key, value in product.dict(exclude_unset=True).items():
        setattr(db_product, key, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product

@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Eliminar un producto"""
    db_product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    db.delete(db_product)
    db.commit()
    return {"message": "Producto eliminado"}
