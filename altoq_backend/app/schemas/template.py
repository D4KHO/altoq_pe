from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Any

class TemplateCreate(BaseModel):
    category_id: int
    name: str
    description: Optional[str] = None
    keywords: List[str]
    fields: dict

class TemplateResponse(BaseModel):
    id: int
    category_id: int
    name: str
    description: Optional[str]
    keywords: List[str]
    fields: dict
    is_active: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TemplateFieldCreate(BaseModel):
    field_name: str
    field_label: str
    field_type: str
    options: Optional[dict] = None
    is_required: int = 1
    placeholder: Optional[str] = None
    validation_regex: Optional[str] = None
    order: int = 0

class TemplateFieldResponse(BaseModel):
    id: int
    template_id: int
    field_name: str
    field_label: str
    field_type: str
    options: Optional[dict]
    is_required: int
    placeholder: Optional[str]
    validation_regex: Optional[str]
    order: int

    class Config:
        from_attributes = True
