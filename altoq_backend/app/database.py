from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base declarativa SQLAlchemy 2.0 para todos los modelos."""
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
