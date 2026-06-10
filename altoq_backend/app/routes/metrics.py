from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
from typing import List, Optional
from ..database import get_db
from ..models.store_metric import StoreMetric
from ..models.store import Store
from ..models.user import User
from ..schemas.store_metric import StoreMetricResponse, DashboardSummary, MetricPeriod
from ..dependencies import get_current_user
from ..utils.metrics import (
    get_or_create_metric,
    calculate_dashboard_summary,
    get_metrics_by_period,
    increment_visits,
    update_products_published,
    update_average_rating
)

router = APIRouter(prefix="/api/seller/metrics", tags=["metrics"])

@router.get("/dashboard", response_model=DashboardSummary)
def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene el resumen del dashboard para la tienda del usuario actual.
    """
    # Verificar que el usuario tenga una tienda
    store = db.query(Store).filter(Store.user_id == current_user.id).first()
    if not store:
        raise HTTPException(status_code=404, detail="El usuario no tiene una tienda")
    
    # Calcular resumen del dashboard
    summary = calculate_dashboard_summary(db, store.id)
    
    return DashboardSummary(**summary)

@router.get("/", response_model=List[StoreMetricResponse])
def get_metrics(
    period: str = Query("daily", description="Periodo: daily, weekly, monthly"),
    days: int = Query(30, description="Número de días a retroceder", ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene las métricas de la tienda para un período específico.
    """
    # Verificar que el usuario tenga una tienda
    store = db.query(Store).filter(Store.user_id == current_user.id).first()
    if not store:
        raise HTTPException(status_code=404, detail="El usuario no tiene una tienda")
    
    # Validar período
    if period not in ["daily", "weekly", "monthly"]:
        raise HTTPException(status_code=400, detail="Periodo inválido. Use: daily, weekly, monthly")
    
    # Obtener métricas
    metrics = get_metrics_by_period(db, store.id, period, days)
    
    return metrics

@router.get("/date/{metric_date}", response_model=StoreMetricResponse)
def get_metric_by_date(
    metric_date: date,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene las métricas de una fecha específica.
    """
    # Verificar que el usuario tenga una tienda
    store = db.query(Store).filter(Store.user_id == current_user.id).first()
    if not store:
        raise HTTPException(status_code=404, detail="El usuario no tiene una tienda")
    
    # Buscar métrica
    metric = db.query(StoreMetric).filter(
        StoreMetric.store_id == store.id,
        StoreMetric.date == metric_date
    ).first()
    
    if not metric:
        raise HTTPException(status_code=404, detail="No hay métricas para esa fecha")
    
    return metric

@router.post("/visit")
def record_visit(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Registra una visita a la tienda del usuario actual.
    """
    # Verificar que el usuario tenga una tienda
    store = db.query(Store).filter(Store.user_id == current_user.id).first()
    if not store:
        raise HTTPException(status_code=404, detail="El usuario no tiene una tienda")
    
    # Incrementar visitas
    metric = increment_visits(db, store.id)
    
    return {
        "message": "Visita registrada exitosamente",
        "date": metric.date,
        "total_visits": metric.visits
    }

@router.post("/refresh")
def refresh_metrics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualiza manualmente las métricas de la tienda (productos publicados y rating promedio).
    """
    # Verificar que el usuario tenga una tienda
    store = db.query(Store).filter(Store.user_id == current_user.id).first()
    if not store:
        raise HTTPException(status_code=404, detail="El usuario no tiene una tienda")
    
    # Actualizar productos publicados
    metric_products = update_products_published(db, store.id)
    
    # Actualizar rating promedio
    metric_rating = update_average_rating(db, store.id)
    
    return {
        "message": "Métricas actualizadas exitosamente",
        "products_published": metric_products.products_published,
        "average_rating": metric_rating.average_rating
    }

@router.get("/summary", response_model=dict)
def get_metrics_summary(
    start_date: date = Query(..., description="Fecha de inicio"),
    end_date: date = Query(..., description="Fecha de fin"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene un resumen de métricas para un rango de fechas específico.
    """
    # Verificar que el usuario tenga una tienda
    store = db.query(Store).filter(Store.user_id == current_user.id).first()
    if not store:
        raise HTTPException(status_code=404, detail="El usuario no tiene una tienda")
    
    # Validar fechas
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="La fecha de inicio debe ser anterior a la fecha de fin")
    
    # Obtener métricas en el rango
    metrics = db.query(StoreMetric).filter(
        StoreMetric.store_id == store.id,
        StoreMetric.date >= start_date,
        StoreMetric.date <= end_date
    ).all()
    
    if not metrics:
        raise HTTPException(status_code=404, detail="No hay métricas en el rango de fechas especificado")
    
    # Calcular totales
    total_visits = sum(m.visits for m in metrics)
    total_orders = sum(m.orders_delivered for m in metrics)
    total_revenue = sum(m.revenue for m in metrics)
    total_chats = sum(m.chat_sessions for m in metrics)
    total_templates = sum(m.template_usage for m in metrics)
    total_new_customers = sum(m.new_users for m in metrics)
    
    # Calcular promedios
    avg_daily_visits = total_visits / len(metrics) if metrics else 0
    avg_daily_orders = total_orders / len(metrics) if metrics else 0
    avg_daily_revenue = total_revenue / len(metrics) if metrics else 0
    
    return {
        "period": {
            "start_date": start_date,
            "end_date": end_date,
            "days": len(metrics)
        },
        "totals": {
            "visits": total_visits,
            "orders_delivered": total_orders,
            "revenue": float(total_revenue),
            "chat_sessions": total_chats,
            "template_usage": total_templates,
            "new_customers": total_new_customers
        },
        "averages": {
            "daily_visits": round(avg_daily_visits, 2),
            "daily_orders": round(avg_daily_orders, 2),
            "daily_revenue": round(avg_daily_revenue, 2)
        }
    }

@router.get("/comparison")
def get_period_comparison(
    period1_days: int = Query(7, description="Días del período 1 (reciente)", ge=1, le=365),
    period2_days: int = Query(7, description="Días del período 2 (anterior)", ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Compara métricas entre dos períodos para identificar tendencias.
    """
    # Verificar que el usuario tenga una tienda
    store = db.query(Store).filter(Store.user_id == current_user.id).first()
    if not store:
        raise HTTPException(status_code=404, detail="El usuario no tiene una tienda")
    
    today = date.today()
    
    # Período 1 (reciente)
    end_date1 = today
    start_date1 = today - timedelta(days=period1_days)
    
    metrics1 = db.query(StoreMetric).filter(
        StoreMetric.store_id == store.id,
        StoreMetric.date >= start_date1,
        StoreMetric.date <= end_date1
    ).all()
    
    # Período 2 (anterior)
    end_date2 = start_date1 - timedelta(days=1)
    start_date2 = end_date2 - timedelta(days=period2_days)
    
    metrics2 = db.query(StoreMetric).filter(
        StoreMetric.store_id == store.id,
        StoreMetric.date >= start_date2,
        StoreMetric.date <= end_date2
    ).all()
    
    # Calcular totales período 1
    visits1 = sum(m.visits for m in metrics1)
    orders1 = sum(m.orders_delivered for m in metrics1)
    revenue1 = sum(m.revenue for m in metrics1)
    
    # Calcular totales período 2
    visits2 = sum(m.visits for m in metrics2)
    orders2 = sum(m.orders_delivered for m in metrics2)
    revenue2 = sum(m.revenue for m in metrics2)
    
    # Calcular variaciones porcentuales
    visits_change = ((visits1 - visits2) / visits2 * 100) if visits2 > 0 else 0
    orders_change = ((orders1 - orders2) / orders2 * 100) if orders2 > 0 else 0
    revenue_change = ((revenue1 - revenue2) / revenue2 * 100) if revenue2 > 0 else 0
    
    return {
        "period1": {
            "start_date": start_date1,
            "end_date": end_date1,
            "days": period1_days,
            "visits": visits1,
            "orders": orders1,
            "revenue": float(revenue1)
        },
        "period2": {
            "start_date": start_date2,
            "end_date": end_date2,
            "days": period2_days,
            "visits": visits2,
            "orders": orders2,
            "revenue": float(revenue2)
        },
        "changes": {
            "visits_percent": round(visits_change, 2),
            "orders_percent": round(orders_change, 2),
            "revenue_percent": round(revenue_change, 2)
        }
    }
