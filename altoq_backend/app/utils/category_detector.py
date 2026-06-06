from sqlalchemy.orm import Session
from ..models.template import ProductTemplate
from typing import Optional, Dict, Any

class CategoryDetector:
    """Servicio para detectar automáticamente la categoría de un producto basado en palabras clave"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def detect_category(self, product_name: str) -> Dict[str, Any]:
        """
        Detecta la categoría de un producto basado en palabras clave.
        
        Args:
            product_name: Nombre del producto a analizar
            
        Returns:
            Diccionario con información de la categoría detectada:
            - category_id: ID de la categoría detectada
            - template_id: ID del template asociado
            - template_name: Nombre del template
            - fields: Campos específicos del template
            - confidence: Nivel de confianza (0-1)
        """
        # Obtener todos los templates activos
        templates = self.db.query(ProductTemplate).filter(
            ProductTemplate.is_active == True
        ).all()
        
        if not templates:
            return {
                "category_id": None,
                "template_id": None,
                "template_name": None,
                "fields": None,
                "confidence": 0
            }
        
        # Normalizar el nombre del producto
        product_name_lower = product_name.lower()
        product_words = set(product_name_lower.split())
        
        best_match = None
        max_score = 0
        
        for template in templates:
            score = self._calculate_match_score(product_name_lower, product_words, template)
            
            if score > max_score:
                max_score = score
                best_match = template
        
        if best_match and max_score > 0.3:  # Umbral mínimo de confianza
            return {
                "category_id": best_match.category_id,
                "template_id": best_match.id,
                "template_name": best_match.name,
                "fields": best_match.fields,
                "confidence": round(max_score, 2)
            }
        
        return {
            "category_id": None,
            "template_id": None,
            "template_name": None,
            "fields": None,
            "confidence": 0
        }
    
    def _calculate_match_score(self, product_name_lower: str, product_words: set, template: ProductTemplate) -> float:
        """
        Calcula el puntaje de coincidencia entre el producto y el template.
        
        Args:
            product_name_lower: Nombre del producto en minúsculas
            product_words: Set de palabras del producto
            template: Template a evaluar
            
        Returns:
            Puntaje de coincidencia (0-1)
        """
        if not template.keywords:
            return 0
        
        keyword_matches = 0
        total_keywords = len(template.keywords)
        
        for keyword in template.keywords:
            keyword_lower = keyword.lower()
            
            # Coincidencia exacta de palabra
            if keyword_lower in product_words:
                keyword_matches += 1
            # Coincidencia parcial (subcadena)
            elif keyword_lower in product_name_lower:
                keyword_matches += 0.5
        
        # Calcular puntaje base
        base_score = keyword_matches / total_keywords if total_keywords > 0 else 0
        
        # Bonus por múltiples coincidencias
        if keyword_matches >= 2:
            base_score *= 1.2
        elif keyword_matches >= 3:
            base_score *= 1.4
        
        # Limitar a máximo 1.0
        return min(base_score, 1.0)
    
    def get_suggested_categories(self, product_name: str, limit: int = 3) -> list:
        """
        Obtiene una lista de categorías sugeridas ordenadas por confianza.
        
        Args:
            product_name: Nombre del producto a analizar
            limit: Número máximo de sugerencias
            
        Returns:
            Lista de diccionarios con información de las categorías sugeridas
        """
        templates = self.db.query(ProductTemplate).filter(
            ProductTemplate.is_active == True
        ).all()
        
        if not templates:
            return []
        
        product_name_lower = product_name.lower()
        product_words = set(product_name_lower.split())
        
        scores = []
        
        for template in templates:
            score = self._calculate_match_score(product_name_lower, product_words, template)
            if score > 0.2:  # Umbral mínimo para incluir en sugerencias
                scores.append({
                    "category_id": template.category_id,
                    "template_id": template.id,
                    "template_name": template.name,
                    "fields": template.fields,
                    "confidence": round(score, 2)
                })
        
        # Ordenar por confianza descendente
        scores.sort(key=lambda x: x["confidence"], reverse=True)
        
        return scores[:limit]
