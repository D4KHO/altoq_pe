from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from ..database import get_db
from ..models.inquiry import StoreInquiry
from ..models.store import Store
from ..schemas.inquiry import InquiryCreate, InquiryResponse
from ..dependencies import get_current_user
from ..models.user import User

router = APIRouter(prefix="/api/inquiry", tags=["inquiry"])


def get_current_user_model(
    current_user_email: str = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    user = db.query(User).filter(User.email == current_user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


@router.post("", response_model=InquiryResponse)
def submit_inquiry(inquiry_data: InquiryCreate, db: Session = Depends(get_db)):
    """Endpoint público — visitante envía una consulta a una tienda."""
    store = db.query(Store).filter(Store.id == inquiry_data.store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Tienda no encontrada")

    inquiry = StoreInquiry(
        store_id=inquiry_data.store_id,
        name=inquiry_data.name,
        email=inquiry_data.email,
        phone=inquiry_data.phone,
        message=inquiry_data.message,
        is_read=False,
        created_at=datetime.utcnow(),
    )
    db.add(inquiry)
    db.commit()
    db.refresh(inquiry)
    return inquiry


@router.get("/my-store", response_model=List[InquiryResponse])
def get_my_store_inquiries(
    current_user: User = Depends(get_current_user_model),
    db: Session = Depends(get_db),
):
    """Devuelve todas las consultas recibidas por la tienda del vendedor autenticado."""
    store = db.query(Store).filter(Store.user_id == current_user.id).first()
    if not store:
        raise HTTPException(status_code=404, detail="No tienes una tienda registrada")

    inquiries = (
        db.query(StoreInquiry)
        .filter(StoreInquiry.store_id == store.id)
        .order_by(StoreInquiry.created_at.desc())
        .all()
    )
    return inquiries


@router.patch("/{inquiry_id}/read")
def mark_inquiry_read(
    inquiry_id: int,
    current_user: User = Depends(get_current_user_model),
    db: Session = Depends(get_db),
):
    """Marca una consulta como leída."""
    store = db.query(Store).filter(Store.user_id == current_user.id).first()
    if not store:
        raise HTTPException(status_code=403, detail="Acceso denegado")

    inquiry = db.query(StoreInquiry).filter(
        StoreInquiry.id == inquiry_id,
        StoreInquiry.store_id == store.id
    ).first()
    if not inquiry:
        raise HTTPException(status_code=404, detail="Consulta no encontrada")

    inquiry.is_read = True
    db.commit()
    return {"message": "Consulta marcada como leída"}
