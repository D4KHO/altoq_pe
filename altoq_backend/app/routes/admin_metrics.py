from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, datetime, timedelta
from typing import List

from ..database import get_db
from ..models.user import User
from ..models.store import Store
from ..models.order import Order
from ..models.store_metric import StoreMetric
from ..schemas.admin_metrics import AdminMetricsSummary, AdminMetricChartPoint, AdminStoreRanking
from .admin_stores import verify_admin

router = APIRouter(prefix="/api/admin/metrics", tags=["admin-metrics"])

@router.get("/summary", response_model=AdminMetricsSummary)
def get_admin_metrics_summary(
    admin: dict = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """
    Obtiene un resumen global de las métricas de la plataforma para el administrador.
    """
    try:
        # Contar usuarios por rol
        total_users = db.query(User).count()
        total_buyers = db.query(User).filter(User.role == "buyer").count()
        total_sellers = db.query(User).filter(User.role == "seller").count()

        # Contar tiendas por estado
        total_stores = db.query(Store).count()
        active_stores = db.query(Store).filter(Store.status == "active").count()
        pending_stores = db.query(Store).filter(Store.status == "pending").count()
        suspended_stores = db.query(Store).filter(Store.status == "suspended").count()

        # Ventas y órdenes (sumar de StoreMetrics o de Order directamente)
        # Hacemos coalesce para evitar recibir None de la base de datos
        total_revenue_metrics = db.query(func.coalesce(func.sum(StoreMetric.revenue), 0.0)).scalar()
        total_orders_metrics = db.query(func.coalesce(func.sum(StoreMetric.orders_delivered), 0)).scalar()

        # Por si acaso StoreMetrics no está completamente integrado, usamos Orders completados como fallback
        total_revenue_orders = db.query(func.coalesce(func.sum(Order.total_amount), 0.0)).filter(Order.status == "completed").scalar()
        total_orders_count = db.query(Order).filter(Order.status == "completed").count()

        # Elegimos el mayor valor (para asegurar que si se crearon órdenes directamente, se reflejen)
        total_revenue = float(max(total_revenue_metrics, total_revenue_orders))
        total_orders = int(max(total_orders_metrics, total_orders_count))

        # Sumatorias de otras métricas de interacción
        total_visits = int(db.query(func.coalesce(func.sum(StoreMetric.visits), 0)).scalar())
        total_chats = int(db.query(func.coalesce(func.sum(StoreMetric.chat_sessions), 0)).scalar())
        total_templates = int(db.query(func.coalesce(func.sum(StoreMetric.template_usage), 0)).scalar())

        # Si total_chats es 0 en StoreMetrics, contamos directamente chats creados
        if total_chats == 0:
            from ..models.chat import Chat
            total_chats = db.query(Chat).count()

        return AdminMetricsSummary(
            total_revenue=total_revenue,
            total_orders=total_orders,
            total_users=total_users,
            total_buyers=total_buyers,
            total_sellers=total_sellers,
            total_stores=total_stores,
            active_stores=active_stores,
            pending_stores=pending_stores,
            suspended_stores=suspended_stores,
            total_visits=total_visits,
            total_chats=total_chats,
            total_templates=total_templates
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener el resumen de métricas: {str(e)}"
        )

@router.get("/charts", response_model=List[AdminMetricChartPoint])
def get_admin_metrics_charts(
    days: int = Query(30, description="Número de días a retroceder", ge=1, le=365),
    admin: dict = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """
    Obtiene las métricas agregadas por día para armar gráficos temporales en el dashboard de administración.
    """
    try:
        today = date.today()
        start_date = today - timedelta(days=days)
        start_datetime = datetime.combine(start_date, datetime.min.time())

        # 1. Agrupar ingresos y órdenes por día
        order_stats = db.query(
            func.date(Order.created_at).label("day"),
            func.count(Order.id).label("orders"),
            func.sum(Order.total_amount).label("revenue")
        ).filter(
            Order.status == "completed",
            Order.created_at >= start_datetime
        ).group_by(
            func.date(Order.created_at)
        ).all()

        orders_map = {str(row.day): (int(row.orders), float(row.revenue or 0.0)) for row in order_stats}

        # 2. Agrupar visitas y chats por día
        metric_stats = db.query(
            StoreMetric.date.label("day"),
            func.coalesce(func.sum(StoreMetric.visits), 0).label("visits"),
            func.coalesce(func.sum(StoreMetric.chat_sessions), 0).label("chats")
        ).filter(
            StoreMetric.date >= start_date
        ).group_by(
            StoreMetric.date
        ).all()

        metrics_map = {str(row.day): (int(row.visits), int(row.chats)) for row in metric_stats}

        # 3. Agrupar nuevos usuarios registrados por día
        user_stats = db.query(
            func.date(User.created_at).label("day"),
            func.count(User.id).label("new_users")
        ).filter(
            User.created_at >= start_datetime
        ).group_by(
            func.date(User.created_at)
        ).all()

        users_map = {str(row.day): int(row.new_users) for row in user_stats}

        # 4. Combinar datos en un solo set por fecha
        chart_points = []
        for i in range(days + 1):
            current_day = start_date + timedelta(days=i)
            day_str = str(current_day)

            # Buscar valores en los diccionarios mapeados
            orders_count, revenue = orders_map.get(day_str, (0, 0.0))
            _, chats_count = metrics_map.get(day_str, (0, 0))
            new_users_count = users_map.get(day_str, 0)

            # Si no hay chats registrados en las métricas, como fallback podemos contar
            # de la tabla de chats directamente para ese día.
            if chats_count == 0:
                from ..models.chat import Chat
                day_start = datetime.combine(current_day, datetime.min.time())
                day_end = datetime.combine(current_day, datetime.max.time())
                chats_count = db.query(Chat).filter(
                    Chat.created_at >= day_start,
                    Chat.created_at <= day_end
                ).count()

            chart_points.append(
                AdminMetricChartPoint(
                    date=day_str,
                    revenue=revenue,
                    orders=orders_count,
                    chats=chats_count,
                    new_users=new_users_count
                )
            )

        return chart_points
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener datos de gráficos: {str(e)}"
        )

@router.get("/rankings", response_model=List[AdminStoreRanking])
def get_admin_store_rankings(
    limit: int = Query(5, description="Número de tiendas a retornar", ge=1, le=50),
    admin: dict = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """
    Obtiene el ranking de las mejores tiendas ordenadas por ingresos.
    """
    try:
        # Hacemos un join de Store con StoreMetric para sumar su revenue y visitas agregadas
        rankings = db.query(
            Store.id.label("store_id"),
            Store.name.label("name"),
            Store.owner_name.label("owner_name"),
            Store.email.label("email"),
            Store.status.label("status"),
            func.coalesce(func.sum(StoreMetric.revenue), 0.0).label("revenue"),
            func.coalesce(func.sum(StoreMetric.orders_delivered), 0).label("orders_count"),
            func.coalesce(func.sum(StoreMetric.visits), 0).label("visits_count"),
            func.coalesce(func.avg(StoreMetric.avg_rating), 0.0).label("avg_rating")
        ).join(
            StoreMetric, StoreMetric.store_id == Store.id, isouter=True
        ).group_by(
            Store.id, Store.name, Store.owner_name, Store.email, Store.status
        ).order_by(
            func.coalesce(func.sum(StoreMetric.revenue), 0.0).desc()
        ).limit(limit).all()

        result = []
        for row in rankings:
            result.append(
                AdminStoreRanking(
                    store_id=row.store_id,
                    name=row.name,
                    owner_name=row.owner_name,
                    email=row.email,
                    revenue=float(row.revenue),
                    orders_count=int(row.orders_count),
                    avg_rating=float(row.avg_rating),
                    visits_count=int(row.visits_count),
                    status=row.status or "pending"
                )
            )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener el ranking de tiendas: {str(e)}"
        )
