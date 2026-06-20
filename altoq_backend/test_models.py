import sys
from app.database import engine, Base
from app.models.store import Store
from app.models.product import Product

try:
    print("Models imported successfully")
    Base.metadata.create_all(bind=engine)
    print("Metadata created successfully")
except Exception as e:
    import traceback
    traceback.print_exc()
