# Modelos de base de datos — SQLAlchemy 2.0
# El orden de importación garantiza que las FK se resuelvan correctamente.

# Base (debe importarse primero para que todos los modelos la registren)
from ..database import Base  # noqa: F401

# Entidades independientes (sin FK hacia otras tablas del proyecto)
from .admin import Admin
from .user import User
from .category import Category
from .password_reset import PasswordResetCode

# Entidades que dependen de las anteriores
from .store import Store
from .address import Address
from .product import Product
from .order import Order

# Entidades de comunicación y entrega
from .chat import Chat, Message
from .delivery_code import DeliveryCode

# Templates de productos
from .template import ProductTemplate, TemplateField

# Métricas
from .store_metric import StoreMetric

# Consultas de tienda
from .inquiry import StoreInquiry

# Reseñas
from .review import Review

__all__ = [
    "Base",
    "Admin",
    "User",
    "Category",
    "PasswordResetCode",
    "Store",
    "Address",
    "Product",
    "Order",
    "Chat",
    "Message",
    "DeliveryCode",
    "ProductTemplate",
    "TemplateField",
    "StoreMetric",
    "StoreInquiry",
    "Review",
]
