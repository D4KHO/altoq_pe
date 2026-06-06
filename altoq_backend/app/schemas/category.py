from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class CategoryBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    icon: Optional[str] = None
    parent_id: Optional[int] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    parent_id: Optional[int] = None

class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class Category(CategoryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class CategoryWithProducts(Category):
    product_count: int

class CategoryTree(Category):
    subcategories: List['CategoryTree'] = []

    class Config:
        from_attributes = True
