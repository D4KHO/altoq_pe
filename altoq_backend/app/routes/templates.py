from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.template import ProductTemplate, TemplateField
from ..models.category import Category
from ..schemas.template import TemplateCreate, TemplateResponse, TemplateFieldCreate, TemplateFieldResponse
from ..dependencies import get_current_user
from ..models.user import User

router = APIRouter(prefix="/api/templates", tags=["templates"])

@router.post("/", response_model=TemplateResponse)
def create_template(
    template_data: TemplateCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crear un nuevo template de producto para una categoría"""
    # Verificar que la categoría existe
    category = db.query(Category).filter(Category.id == template_data.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    # Crear template
    new_template = ProductTemplate(
        category_id=template_data.category_id,
        name=template_data.name,
        description=template_data.description,
        keywords=template_data.keywords,
        fields=template_data.fields
    )
    db.add(new_template)
    db.commit()
    db.refresh(new_template)
    
    return new_template

@router.get("/", response_model=List[TemplateResponse])
def get_templates(
    category_id: int = None,
    db: Session = Depends(get_db)
):
    """Obtener todos los templates, opcionalmente filtrados por categoría"""
    query = db.query(ProductTemplate).filter(ProductTemplate.is_active == True)
    
    if category_id:
        query = query.filter(ProductTemplate.category_id == category_id)
    
    templates = query.order_by(ProductTemplate.name).all()
    return templates

@router.get("/{template_id}", response_model=TemplateResponse)
def get_template(
    template_id: int,
    db: Session = Depends(get_db)
):
    """Obtener un template específico"""
    template = db.query(ProductTemplate).filter(ProductTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template no encontrado")
    
    return template

@router.post("/detect-category")
def detect_category(
    product_name: str,
    db: Session = Depends(get_db)
):
    """Detectar la categoría de un producto basado en palabras clave"""
    templates = db.query(ProductTemplate).filter(ProductTemplate.is_active == True).all()
    
    best_match = None
    max_matches = 0
    
    product_name_lower = product_name.lower()
    
    for template in templates:
        matches = 0
        # template.keywords es una cadena separada por comas, convertirla a lista
        keywords_list = template.keywords.split(',') if template.keywords else []
        for keyword in keywords_list:
            if keyword.lower().strip() in product_name_lower:
                matches += 1
        
        if matches > max_matches:
            max_matches = matches
            best_match = template
    
    if best_match:
        # Obtener los campos del template desde la tabla template_fields
        template_fields = db.query(TemplateField).filter(
            TemplateField.template_id == best_match.id
        ).order_by(TemplateField.order).all()
        
        print(f"DEBUG: Template ID: {best_match.id}")
        print(f"DEBUG: Campos encontrados: {len(template_fields)}")
        
        # Convertir los campos a formato JSON para el frontend
        fields_json = [
            {
                "name": field.field_name,
                "label": field.field_label,
                "type": field.field_type,
                "required": field.is_required == 1,
                "placeholder": field.placeholder,
                "options": field.options
            }
            for field in template_fields
        ]
        
        print(f"DEBUG: Fields JSON: {fields_json}")
        
        return {
            "category_id": best_match.category_id,
            "template_id": best_match.id,
            "template_name": best_match.name,
            "fields": fields_json,
            "confidence": max_matches
        }
    
    return {"category_id": None, "template_id": None, "confidence": 0}

@router.post("/{template_id}/fields", response_model=TemplateFieldResponse)
def add_template_field(
    template_id: int,
    field_data: TemplateFieldCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Agregar un campo a un template"""
    template = db.query(ProductTemplate).filter(ProductTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template no encontrado")
    
    new_field = TemplateField(
        template_id=template_id,
        field_name=field_data.field_name,
        field_label=field_data.field_label,
        field_type=field_data.field_type,
        options=field_data.options,
        is_required=field_data.is_required,
        placeholder=field_data.placeholder,
        validation_regex=field_data.validation_regex,
        order=field_data.order
    )
    db.add(new_field)
    db.commit()
    db.refresh(new_field)
    
    return new_field

@router.get("/{template_id}/fields", response_model=List[TemplateFieldResponse])
def get_template_fields(
    template_id: int,
    db: Session = Depends(get_db)
):
    """Obtener los campos de un template"""
    template = db.query(ProductTemplate).filter(ProductTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template no encontrado")
    
    fields = db.query(TemplateField).filter(TemplateField.template_id == template_id).order_by(TemplateField.order).all()
    return fields
