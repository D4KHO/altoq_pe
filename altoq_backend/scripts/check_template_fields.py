import os
import sys
from sqlalchemy.orm import Session

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.template import ProductTemplate, TemplateField
from app.models.category import Category

def check_template_fields():
    db: Session = SessionLocal()
    
    try:
        # Obtener todos los templates
        templates = db.query(ProductTemplate).all()
        print(f"Templates encontrados: {len(templates)}")
        
        for template in templates:
            category = db.query(Category).filter(Category.id == template.category_id).first()
            print(f"\nTemplate ID: {template.id}, Category: {category.name if category else 'N/A'}")
            print(f"  Keywords: {template.keywords}")
            
            # Obtener campos de este template
            fields = db.query(TemplateField).filter(
                TemplateField.template_id == template.id
            ).all()
            print(f"  Campos encontrados: {len(fields)}")
            
            for field in fields:
                print(f"    - {field.field_name}: {field.field_label} ({field.field_type})")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_template_fields()
