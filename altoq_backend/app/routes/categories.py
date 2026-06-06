from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from ..database import get_db
from ..models.category import Category as CategoryModel
from ..models.product import Product as ProductModel
from ..schemas.category import Category, CategoryCreate, CategoryUpdate, CategoryWithProducts, CategoryTree

router = APIRouter(prefix="/api/categories", tags=["categories"])

@router.get("/", response_model=List[Category])
def get_categories(db: Session = Depends(get_db)):
    """Get all categories"""
    categories = db.query(CategoryModel).all()
    return categories

@router.get("/tree", response_model=List[CategoryTree])
def get_category_tree(db: Session = Depends(get_db)):
    """Get categories in tree structure"""
    # Get only parent categories (no parent_id)
    parent_categories = db.query(CategoryModel).filter(CategoryModel.parent_id == None).all()
    return parent_categories

@router.get("/with-counts", response_model=List[CategoryWithProducts])
def get_categories_with_product_counts(db: Session = Depends(get_db)):
    """Get categories with product counts"""
    categories = db.query(
        CategoryModel,
        func.count(ProductModel.id).label('product_count')
    ).outerjoin(ProductModel).group_by(CategoryModel.id).all()
    
    result = []
    for category, count in categories:
        cat_dict = {
            "id": category.id,
            "name": category.name,
            "slug": category.slug,
            "description": category.description,
            "icon": category.icon,
            "parent_id": category.parent_id,
            "created_at": category.created_at,
            "product_count": count
        }
        result.append(cat_dict)
    
    return result

@router.get("/{category_id}", response_model=Category)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """Get a specific category"""
    category = db.query(CategoryModel).filter(CategoryModel.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.get("/slug/{slug}", response_model=Category)
def get_category_by_slug(slug: str, db: Session = Depends(get_db)):
    """Get category by slug"""
    category = db.query(CategoryModel).filter(CategoryModel.slug == slug).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.post("/", response_model=Category)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """Create a new category"""
    # Check if slug already exists
    existing = db.query(CategoryModel).filter(CategoryModel.slug == category.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category with this slug already exists")
    
    db_category = CategoryModel(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.put("/{category_id}", response_model=Category)
def update_category(category_id: int, category: CategoryUpdate, db: Session = Depends(get_db)):
    """Update a category"""
    db_category = db.query(CategoryModel).filter(CategoryModel.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    update_data = category.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_category, field, value)
    
    db.commit()
    db.refresh(db_category)
    return db_category

@router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    """Delete a category"""
    db_category = db.query(CategoryModel).filter(CategoryModel.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check if category has products
    product_count = db.query(ProductModel).filter(ProductModel.category_id == category_id).count()
    if product_count > 0:
        raise HTTPException(status_code=400, detail=f"Cannot delete category with {product_count} products")
    
    db.delete(db_category)
    db.commit()
    return {"message": "Category deleted successfully"}
