from app.database import SessionLocal
from app.models.template import ProductTemplate
from app.models.category import Category
from sqlalchemy.orm import Session

def check_templates():
    db: Session = SessionLocal()
    
    try:
        # Obtener todos los templates
        templates = db.query(ProductTemplate).all()
        print(f"Templates encontrados: {len(templates)}")
        
        for template in templates:
            category = db.query(Category).filter(Category.id == template.category_id).first()
            print(f"ID: {template.id}, Category ID: {template.category_id}, Category Name: {category.name if category else 'N/A'}, Name: {template.name}, Keywords: {template.keywords}")
        
        # Obtener todas las categorías
        categories = db.query(Category).all()
        print(f"\nCategorías encontradas: {len(categories)}")
        
        for category in categories:
            print(f"ID: {category.id}, Name: {category.name}, Slug: {category.slug}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_templates()
