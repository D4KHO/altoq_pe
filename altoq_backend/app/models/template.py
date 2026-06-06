from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class ProductTemplate(Base):
    __tablename__ = "product_templates"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    keywords = Column(JSON, nullable=False)  # Lista de palabras clave para detectar esta categoría
    fields = Column(JSON, nullable=False)  # Campos específicos del template
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    category = relationship("Category", backref="templates")

class TemplateField(Base):
    __tablename__ = "template_fields"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("product_templates.id"), nullable=False)
    field_name = Column(String(50), nullable=False)
    field_label = Column(String(100), nullable=False)
    field_type = Column(String(20), nullable=False)  # text, number, select, boolean, date
    options = Column(JSON, nullable=True)  # Para campos select
    is_required = Column(Integer, default=1)
    placeholder = Column(String(200), nullable=True)
    validation_regex = Column(String(200), nullable=True)
    order = Column(Integer, default=0)

    # Relationships
    template = relationship("ProductTemplate", backref="template_fields")
