from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
from typing import Optional
from ..models.store_metric import StoreMetric
from ..models.store import Store
from ..models.product import Product
from ..models.order import Order
from ..models.chat import Chat
from ..models.delivery_code import DeliveryCode

def get_or_create_metric(db: Session, store_id: int, metric_date: date) -> StoreMetric:
    """
    Obtiene o crea un registro de métricas para una tienda en una fecha específica.
    """
    metric = db.query(StoreMetric).filter(
        StoreMetric.store_id == store_id,
        StoreMetric.date == metric_date
    ).first()
    
    if not metric:
        metric = StoreMetric(
            store_id=store_id,
            date=metric_date
        )
        db.add(metric)
        db.commit()
        db.refresh(metric)
    
    return metric

def increment_visits(db: Session, store_id: int, increment: int = 1):
    """
    Incrementa el contador de visitas para una tienda en la fecha actual.
    """
    today = date.today()
    metric = get_or_create_metric(db, store_id, today)
    metric.visits += increment
    metric.updated_at = datetime.utcnow()
    db.commit()
    return metric

def increment_chat_sessions(db: Session, store_id: int, increment: int = 1):
    """
    Incrementa el contador de sesiones de chat para una tienda en la fecha actual.
    """
    today = date.today()
    metric = get_or_create_metric(db, store_id, today)
    metric.chat_sessions += increment
    metric.updated_at = datetime.utcnow()
    db.commit()
    return metric

def increment_template_usage(db: Session, store_id: int, increment: int = 1):
    """
    Incrementa el contador de uso de templates para una tienda en la fecha actual.
    """
    today = date.today()
    metric = get_or_create_metric(db, store_id, today)
    metric.template_usage += increment
    metric.updated_at = datetime.utcnow()
    db.commit()
    return metric

def record_order_delivery(db: Session, store_id: int, order_amount: float):
    """
    Registra una entrega de pedido para una tienda en la fecha actual.
    """
    today = date.today()
    metric = get_or_create_metric(db, store_id, today)
    metric.orders_delivered += 1
    metric.revenue += order_amount
    metric.updated_at = datetime.utcnow()
    db.commit()
    return metric

def record_new_customer(db: Session, store_id: int):
    """
    Registra un nuevo cliente para una tienda en la fecha actual.
    """
    today = date.today()
    metric = get_or_create_metric(db, store_id, today)
    metric.new_users += 1
    metric.updated_at = datetime.utcnow()
    db.commit()
    return metric

def update_products_published(db: Session, store_id: int):
    """
    Actualiza el contador de productos publicados para una tienda en la fecha actual.
    """
    today = date.today()
    metric = get_or_create_metric(db, store_id, today)
    
    # Contar productos activos de la tienda
    active_products = db.query(Product).filter(
        Product.store_id == store_id
    ).count()
    
    metric.products_published = active_products
    metric.updated_at = datetime.utcnow()
    db.commit()
    return metric

def update_average_rating(db: Session, store_id: int):
    """
    Actualiza el rating promedio de una tienda en la fecha actual.
    """
    today = date.today()
    metric = get_or_create_metric(db, store_id, today)
    
    # Calcular rating promedio de todos los productos de la tienda
    products = db.query(Product).filter(Product.store_id == store_id).all()
    
    if products:
        total_rating = sum(p.rating for p in products if p.rating > 0)
        rated_products = sum(1 for p in products if p.rating > 0)
        
        if rated_products > 0:
            metric.avg_rating = total_rating / rated_products
        else:
            metric.avg_rating = 0.0
    else:
        metric.avg_rating = 0.0
    
    metric.updated_at = datetime.utcnow()
    db.commit()
    return metric

def calculate_dashboard_summary(db: Session, store_id: int) -> dict:
    """
    Calcula el resumen del dashboard para una tienda.
    """
    print(f"DEBUG: Calculando dashboard para store_id: {store_id}")
    
    # Métricas totales (históricas)
    total_metrics = db.query(StoreMetric).filter(
        StoreMetric.store_id == store_id
    ).all()
    
    print(f"DEBUG: Total metrics encontrados: {len(total_metrics)}")
    
    total_visits = sum(m.visits for m in total_metrics)
    total_orders_delivered = sum(m.orders_delivered for m in total_metrics)
    total_revenue = sum(m.revenue for m in total_metrics)
    total_chat_sessions = sum(m.chat_sessions for m in total_metrics)
    
    # Productos activos actuales
    total_products = db.query(Product).filter(
        Product.store_id == store_id
    ).count()
    
    print(f"DEBUG: Total productos: {total_products}")
    
    # Rating promedio actual
    products = db.query(Product).filter(Product.store_id == store_id).all()
    average_rating = 0.0
    if products:
        total_rating = sum(p.rating for p in products if p.rating > 0)
        rated_products = sum(1 for p in products if p.rating > 0)
        if rated_products > 0:
            average_rating = total_rating / rated_products
    
    # Métricas de hoy
    today = date.today()
    today_metric = db.query(StoreMetric).filter(
        StoreMetric.store_id == store_id,
        StoreMetric.date == today
    ).first()
    
    today_visits = today_metric.visits if today_metric else 0
    today_orders = today_metric.orders_delivered if today_metric else 0
    today_revenue = float(today_metric.revenue) if today_metric else 0.0
    
    # Crecimiento semanal (comparar esta semana con la anterior)
    weekly_growth = None
    today_weekday = today.weekday()
    week_start = today - timedelta(days=today_weekday)
    week_end = week_start + timedelta(days=6)
    
    last_week_start = week_start - timedelta(days=7)
    last_week_end = week_end - timedelta(days=7)
    
    # Métricas de esta semana
    this_week_metrics = db.query(StoreMetric).filter(
        StoreMetric.store_id == store_id,
        StoreMetric.date >= week_start,
        StoreMetric.date <= week_end
    ).all()
    
    this_week_revenue = sum(m.revenue for m in this_week_metrics)
    
    # Métricas de la semana pasada
    last_week_metrics = db.query(StoreMetric).filter(
        StoreMetric.store_id == store_id,
        StoreMetric.date >= last_week_start,
        StoreMetric.date <= last_week_end
    ).all()
    
    last_week_revenue = sum(m.revenue for m in last_week_metrics)
    
    # Calcular crecimiento
    if last_week_revenue > 0:
        weekly_growth = ((this_week_revenue - last_week_revenue) / last_week_revenue) * 100
    
    result = {
        "store_id": store_id,
        "total_visits": total_visits,
        "total_products": total_products,
        "total_orders_delivered": total_orders_delivered,
        "total_revenue": float(total_revenue),
        "total_chat_sessions": total_chat_sessions,
        "average_rating": average_rating,
        "today_visits": today_visits,
        "today_orders": today_orders,
        "today_revenue": today_revenue,
        "weekly_growth": weekly_growth
    }
    
    print(f"DEBUG: Resultado dashboard: {result}")
    return result

def get_metrics_by_period(db: Session, store_id: int, period: str, days: int = 30) -> list:
    """
    Obtiene métricas para un período específico.
    period: "daily", "weekly", "monthly"
    days: número de días a retroceder
    """
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    metrics = db.query(StoreMetric).filter(
        StoreMetric.store_id == store_id,
        StoreMetric.date >= start_date,
        StoreMetric.date <= end_date
    ).order_by(StoreMetric.date.desc()).all()
    
    return metrics
