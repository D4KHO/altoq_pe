import os
import uuid
import shutil
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime

from ..database import get_db
from ..dependencies import get_current_user
from ..models.review import Review as ReviewModel
from ..models.user import User as UserModel
from ..models.product import Product as ProductModel
from ..models.order import Order as OrderModel
from ..schemas.review import ReviewCreate, ReviewResponse

router = APIRouter(prefix="/api/reviews", tags=["reviews"])


@router.post("/", response_model=ReviewResponse)
def create_review(
    review_data: ReviewCreate,
    current_user_email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crear una reseña para un producto comprado en un pedido completado"""
    # 1. Obtener usuario actual
    user = db.query(UserModel).filter(UserModel.email == current_user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # 2. Obtener pedido
    order = db.query(OrderModel).filter(OrderModel.id == review_data.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    # Validar que el pedido pertenece al usuario
    if order.user_id != user.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para reseñar este pedido")

    # Validar que el pedido esté completado
    if order.status != "completed":
        raise HTTPException(
            status_code=400, 
            detail="Solo puedes dejar reseñas de pedidos completados y entregados"
        )

    # 3. Validar que el producto existe
    product = db.query(ProductModel).filter(ProductModel.id == review_data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    # Validar que el producto sea parte de este pedido
    products_in_order = order.products or []
    is_product_in_order = False
    for p in products_in_order:
        if isinstance(p, dict) and p.get("productId") == review_data.product_id:
            is_product_in_order = True
            break
    if not is_product_in_order:
        raise HTTPException(status_code=400, detail="Este producto no forma parte del pedido")

    # 4. Validar que no se haya reseñado este producto en esta orden ya
    existing_review = db.query(ReviewModel).filter(
        ReviewModel.user_id == user.id,
        ReviewModel.order_id == review_data.order_id,
        ReviewModel.product_id == review_data.product_id
    ).first()

    if existing_review:
        raise HTTPException(status_code=400, detail="Ya has reseñado este producto para este pedido")

    # 5. Guardar la reseña
    new_review = ReviewModel(
        user_id=user.id,
        product_id=review_data.product_id,
        store_id=product.store_id or 1,
        order_id=review_data.order_id,
        rating=review_data.rating,
        store_rating=review_data.store_rating,
        comment=review_data.comment,
        image_url=review_data.image_url,
        created_at=datetime.utcnow()
    )
    db.add(new_review)
    db.commit()
    db.refresh(new_review)

    # 6. Recalcular el rating promedio del producto
    # Obtener el promedio de rating y la cantidad de calificaciones
    stats = db.query(
        func.avg(ReviewModel.rating),
        func.count(ReviewModel.id)
    ).filter(ReviewModel.product_id == review_data.product_id).first()

    avg_rating = stats[0] if stats and stats[0] is not None else 0.0
    rating_count = stats[1] if stats and stats[1] is not None else 0

    product.rating = round(float(avg_rating), 1)
    product.rating_count = int(rating_count)
    db.commit()

    # Devolver respuesta
    response = ReviewResponse.from_orm(new_review)
    response.user_name = user.name
    return response


@router.get("/product/{product_id}", response_model=List[ReviewResponse])
def get_product_reviews(product_id: int, db: Session = Depends(get_db)):
    """Obtener todas las reseñas para un producto específico"""
    reviews = db.query(ReviewModel).filter(ReviewModel.product_id == product_id).order_by(ReviewModel.created_at.desc()).all()
    
    result = []
    for r in reviews:
        resp = ReviewResponse.from_orm(r)
        resp.user_name = r.user.name if r.user else "Usuario de AltoQ"
        result.append(resp)
    return result


@router.get("/order/{order_id}", response_model=List[ReviewResponse])
def get_order_reviews(
    order_id: int, 
    current_user_email: str = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Obtener todas las reseñas realizadas por el usuario para una orden en específico"""
    user = db.query(UserModel).filter(UserModel.email == current_user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    reviews = db.query(ReviewModel).filter(
        ReviewModel.order_id == order_id,
        ReviewModel.user_id == user.id
    ).all()

    result = []
    for r in reviews:
        resp = ReviewResponse.from_orm(r)
        resp.user_name = user.name
        result.append(resp)
    return result


@router.post("/upload")
def upload_review_image(
    request: Request,
    file: UploadFile = File(...),
    current_user_email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Subir una foto del producto comprado para adjuntarla a la reseña"""
    user = db.query(UserModel).filter(UserModel.email == current_user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen válida")

    # Asegurar que el directorio de uploads de reseñas exista
    upload_dir = "static/uploads/reviews"
    os.makedirs(upload_dir, exist_ok=True)

    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"review_{user.id}_{uuid.uuid4().hex}{file_extension}"
    file_path = os.path.join(upload_dir, unique_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    base_url = str(request.base_url).rstrip("/")
    public_url = f"{base_url}/static/uploads/reviews/{unique_filename}"
    return {"message": "Imagen subida exitosamente", "image_url": public_url}


@router.get("/pending-review/product/{product_id}")
def check_pending_review_for_product(
    product_id: int,
    current_user_email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verificar si el usuario tiene un pedido completado con este producto que aún no ha sido reseñado"""
    user = db.query(UserModel).filter(UserModel.email == current_user_email).first()
    if not user:
        return {"can_review": False, "order_id": None}

    # Buscar pedidos completados del usuario
    completed_orders = db.query(OrderModel).filter(
        OrderModel.user_id == user.id,
        OrderModel.status == "completed"
    ).all()

    for order in completed_orders:
        products_in_order = order.products or []
        product_found = False
        for p in products_in_order:
            if isinstance(p, dict) and p.get("productId") == product_id:
                product_found = True
                break

        if product_found:
            # Verificar si ya existe una reseña para esta orden y producto
            existing_review = db.query(ReviewModel).filter(
                ReviewModel.user_id == user.id,
                ReviewModel.order_id == order.id,
                ReviewModel.product_id == product_id
            ).first()

            if not existing_review:
                return {"can_review": True, "order_id": order.id}

    return {"can_review": False, "order_id": None}


@router.get("/store/{store_id}", response_model=List[ReviewResponse])
def get_store_reviews(store_id: int, db: Session = Depends(get_db)):
    """Obtener todas las reseñas de los productos de una tienda específica"""
    reviews = db.query(ReviewModel).filter(ReviewModel.store_id == store_id).order_by(ReviewModel.created_at.desc()).all()
    
    result = []
    for r in reviews:
        resp = ReviewResponse.from_orm(r)
        resp.user_name = r.user.name if r.user else "Usuario de AltoQ"
        result.append(resp)
    return result

