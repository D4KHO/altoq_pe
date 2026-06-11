import os
import sys
from sqlalchemy.orm import Session

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.category import Category
from app.models.template import ProductTemplate, TemplateField

def get_keywords_for_category(slug: str) -> str:
    """Retorna las palabras clave para una categoría específica"""
    keywords_map = {
        "electronica": "celular,telefono,laptop,computadora,tablet,electronico,gadget,tecnologia",
        "ropa-moda": "camiseta,pantalon,zapatos,vestido,ropa,moda,calzado",
        "hogar-jardin": "mueble,silla,mesa,lampara,decoracion,hogar,casa",
        "deportes": "balon,futbol,deporte,calzado,ropa,implemento",
        "juguetes-ninos": "juguete,nino,bebida,educativo,infantil",
        "libros": "libro,lectura,escritura,papel,libreria",
        "belleza-cuidado": "maquillaje,crema,perfume,belleza,cuidado",
        "alimentos-bebidas": "torta,pastel,comida,alimento,postre,panaderia,reposteria,bebida"
    }
    return keywords_map.get(slug, "")

def get_fields_for_category(slug: str, template_id: int) -> list:
    """Retorna los campos específicos para una categoría"""
    fields_map = {
        "electronica": [
            TemplateField(template_id=template_id, field_name="marca", field_label="Marca", field_type="text", is_required=1),
            TemplateField(template_id=template_id, field_name="modelo", field_label="Modelo", field_type="text", is_required=1),
            TemplateField(template_id=template_id, field_name="garantia", field_label="Garantía (meses)", field_type="number", is_required=0),
        ],
        "ropa-moda": [
            TemplateField(template_id=template_id, field_name="talla", field_label="Talla", field_type="text", is_required=1),
            TemplateField(template_id=template_id, field_name="material", field_label="Material", field_type="text", is_required=0),
            TemplateField(template_id=template_id, field_name="color", field_label="Color", field_type="text", is_required=0),
        ],
        "hogar-jardin": [
            TemplateField(template_id=template_id, field_name="material", field_label="Material", field_type="text", is_required=1),
            TemplateField(template_id=template_id, field_name="dimensiones", field_label="Dimensiones (cm)", field_type="text", is_required=0),
            TemplateField(template_id=template_id, field_name="color", field_label="Color", field_type="text", is_required=0),
        ],
        "deportes": [
            TemplateField(template_id=template_id, field_name="deporte", field_label="Deporte", field_type="text", is_required=1),
            TemplateField(template_id=template_id, field_name="talla", field_label="Talla", field_type="text", is_required=0),
            TemplateField(template_id=template_id, field_name="material", field_label="Material", field_type="text", is_required=0),
        ],
        "juguetes-ninos": [
            TemplateField(template_id=template_id, field_name="edad_recomendada", field_label="Edad recomendada", field_type="text", is_required=1),
            TemplateField(template_id=template_id, field_name="material", field_label="Material", field_type="text", is_required=0),
            TemplateField(template_id=template_id, field_name="genero", field_label="Género", field_type="text", is_required=0),
        ],
        "libros": [
            TemplateField(template_id=template_id, field_name="autor", field_label="Autor", field_type="text", is_required=1),
            TemplateField(template_id=template_id, field_name="genero", field_label="Género literario", field_type="text", is_required=0),
            TemplateField(template_id=template_id, field_name="paginas", field_label="Número de páginas", field_type="number", is_required=0),
        ],
        "belleza-cuidado": [
            TemplateField(template_id=template_id, field_name="tipo", field_label="Tipo de producto", field_type="text", is_required=1),
            TemplateField(template_id=template_id, field_name="marca", field_label="Marca", field_type="text", is_required=0),
            TemplateField(template_id=template_id, field_name="tamaño", field_label="Tamaño (ml/g)", field_type="text", is_required=0),
        ],
        "alimentos-bebidas": [
            TemplateField(template_id=template_id, field_name="ingredientes", field_label="Ingredientes principales", field_type="text", is_required=1),
            TemplateField(template_id=template_id, field_name="sabor", field_label="Sabor principal", field_type="text", is_required=1),
            TemplateField(template_id=template_id, field_name="peso", field_label="Peso (kg)", field_type="number", is_required=0),
            TemplateField(template_id=template_id, field_name="alergenos", field_label="Alergenos", field_type="text", is_required=0),
        ]
    }
    return fields_map.get(slug, [])

def create_sample_templates():
    db: Session = SessionLocal()
    
    try:
        # Obtener categorías existentes
        categories = db.query(Category).all()
        print(f"Categorías encontradas: {len(categories)}")
        
        if not categories:
            print("No hay categorías. Creando categorías de ejemplo...")
            # Crear categorías de ejemplo si no existen
            categories_data = [
                {"name": "Comida", "slug": "comida", "icon": "🍔"},
                {"name": "Tecnología", "slug": "tecnologia", "icon": "💻"},
                {"name": "Ropa", "slug": "ropa", "icon": "👕"},
                {"name": "Hogar", "slug": "hogar", "icon": "🏠"}
            ]
            for cat_data in categories_data:
                category = Category(**cat_data)
                db.add(category)
            db.commit()
            db.refresh_all()
            categories = db.query(Category).all()
        
        # Actualizar keywords de templates existentes
        for category in categories:
            # Buscar template existente para esta categoría
            existing_template = db.query(ProductTemplate).filter(
                ProductTemplate.category_id == category.id
            ).first()
            
            if existing_template:
                print(f"Actualizando keywords para categoría {category.name}...")
                # Actualizar keywords del template existente
                keywords = get_keywords_for_category(category.slug)
                existing_template.keywords = keywords
                db.commit()
                print(f"  - Keywords actualizados: {keywords}")
            else:
                print(f"No existe template para categoría {category.name}, creando...")
                # Crear template según la categoría
                keywords = get_keywords_for_category(category.slug)
                template = ProductTemplate(
                    category_id=category.id,
                    name=f"Template de {category.name}",
                    keywords=keywords,
                    fields=[]  # JSON vacío para la columna fields
                )
                db.add(template)
                db.commit()
                db.refresh(template)
                
                # Agregar campos específicos según la categoría
                fields = get_fields_for_category(category.slug, template.id)
                for field in fields:
                    db.add(field)
                db.commit()
                
                print(f"Template creado para categoría {category.name}")
        
        print("\n✓ Templates de ejemplo creados exitosamente")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_templates()
