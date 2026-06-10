from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Numeric, Date
from sqlalchemy.orm import relationship
from datetime import datetime, date
from ..database import Base

class StoreMetric(Base):
    __tablename__ = "store_metrics"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)  # Fecha del registro (un documento por día por tienda)
    
    # Métricas de visitas
    visits = Column(Integer, default=0)  # Número de visitas a la tienda ese día
    
    # Métricas de productos
    products_published = Column(Integer, default=0)  # Productos activos en el catálogo en esa fecha
    
    # Métricas de pedidos
    orders_delivered = Column(Integer, default=0)  # Pedidos con código de entrega validado ese día
    revenue = Column(Numeric(precision=10, scale=2), default=0.0)  # Monto total generado ese día en S/
    
    # Métricas de chat
    chat_sessions = Column(Integer, default=0)  # Chats de pedidos iniciados ese día en la tienda
    
    # Métricas de uso
    template_usage = Column(Integer, default=0)  # Veces que se usó el flujo de templates para publicar productos ese día
    new_users = Column(Integer, default=0)  # Compradores nuevos que interactuaron con la tienda ese día
    
    # Métricas de calidad
    avg_rating = Column(Float, default=0.0)  # Promedio de calificaciones de todas las reseñas acumuladas hasta esa fecha
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    store = relationship("Store", backref="metrics")

    def __repr__(self):
        return f"<StoreMetric(store_id={self.store_id}, date={self.date}, visits={self.visits})>"
