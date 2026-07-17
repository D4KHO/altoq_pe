from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.product import Product as ProductModel
from ..models.category import Category as CategoryModel
from ..models.order import Order as OrderModel
from ..schemas.product import ProductResponse as Product, ProductCreate, ProductUpdate

router = APIRouter(prefix="/api/products", tags=["products"])


def _populate_products_sales(db: Session, products: List[ProductModel]):
    """Poblar el total de ventas acumuladas para una lista de productos en una única consulta de base de datos."""
    if not products:
        return products
        
    product_ids = {p.id for p in products}
    # Traer todas las órdenes completadas una sola vez
    completed_orders = db.query(OrderModel).filter(OrderModel.status == "completed").all()
    
    # Calcular y acumular ventas en memoria
    sales_map = {}
    for order in completed_orders:
        products_json = order.products or []
        for p in products_json:
            if isinstance(p, dict):
                p_id = p.get("productId")
                if p_id in product_ids:
                    qty = p.get("quantity", 1)
                    sales_map[p_id] = sales_map.get(p_id, 0) + qty
                    
    for p in products:
        p.sales = sales_map.get(p.id, 0)
        
    return products


def _populate_product_sales(db: Session, product: ProductModel):
    """Fallback compatible con llamadas a productos individuales."""
    _populate_products_sales(db, [product])
    return product


@router.get("/category/{slug}", response_model=List[Product])
def get_products_by_category(slug: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Obtener productos por slug de categoría"""
    category = db.query(CategoryModel).filter(CategoryModel.slug == slug).first()
    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    products = db.query(ProductModel).filter(ProductModel.category_id == category.id).offset(skip).limit(limit).all()
    _populate_products_sales(db, products)
    return products


@router.get("/search", response_model=List[Product])
def search_products(q: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Buscar productos por nombre o descripción con soporte de múltiples palabras y relevancia"""
    if not q:
        return []
    
    from sqlalchemy import and_
    
    # Limpiar y separar en palabras de búsqueda
    search_query = q.strip()
    words = [w.lower() for w in search_query.split() if w.strip()]
    if not words:
        return []
    
    # Construir filtros para que TODAS las palabras ingresadas coincidan parcial o totalmente
    filters = []
    for word in words:
        filters.append(
            (ProductModel.name.ilike(f"%{word}%")) | 
            (ProductModel.description.ilike(f"%{word}%"))
        )
    
    # Consultar base de datos limitando a 500 resultados para ordenar por relevancia en memoria
    raw_products = db.query(ProductModel).filter(and_(*filters)).limit(500).all()
    
    # Calcular relevancia (scoring) en memoria
    scored_products = []
    for p in raw_products:
        name_lower = p.name.lower()
        desc_lower = (p.description or "").lower()
        q_lower = search_query.lower()
        
        score = 0
        
        # 1. Coincidencia exacta de la consulta completa en el nombre (mayor prioridad)
        if q_lower in name_lower:
            score += 1000
            if name_lower == q_lower:
                score += 500
        
        # 2. Coincidencia de palabras individuales en el nombre
        words_in_name = sum(1 for w in words if w in name_lower)
        score += (words_in_name / len(words)) * 500
        
        # 3. Coincidencia exacta de la consulta completa en la descripción
        if q_lower in desc_lower:
            score += 200
        
        # 4. Coincidencia de palabras individuales en la descripción
        words_in_desc = sum(1 for w in words if w in desc_lower)
        score += (words_in_desc / len(words)) * 100
        
        scored_products.append((p, score))
    
    # Ordenar por relevancia descendente
    scored_products.sort(key=lambda item: item[1], reverse=True)
    
    # Extraer los productos ordenados, aplicar paginación y poblar ventas por lote
    paginated_products = []
    for p, score in scored_products[skip : skip + limit]:
        paginated_products.append(p)
        
    _populate_products_sales(db, paginated_products)
        
    return paginated_products


@router.get("/", response_model=List[Product])
def get_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Obtener lista de productos"""
    products = db.query(ProductModel).order_by(ProductModel.id.desc()).offset(skip).limit(limit).all()
    _populate_products_sales(db, products)
    return products


@router.get("/{product_id}", response_model=Product)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Obtener un producto por ID"""
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    _populate_products_sales(db, [product])
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
    _populate_products_sales(db, [db_product])
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
