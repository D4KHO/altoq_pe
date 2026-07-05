from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, datetime, timedelta
from typing import List, Optional
import csv
import io

from ..database import get_db
from ..models.user import User
from ..models.store import Store
from ..models.order import Order
from ..models.store_metric import StoreMetric
from ..schemas.admin_metrics import AdminMetricsSummary, AdminMetricChartPoint, AdminStoreRanking
from .admin_stores import verify_admin

router = APIRouter(prefix="/api/admin/metrics", tags=["admin-metrics"])

def parse_date_range(start_date: Optional[str], end_date: Optional[str], default_days: int = 30):
    """
    Parsea y valida un rango de fechas. Si no se especifican, retrocede default_days a partir de hoy.
    """
    if start_date and end_date:
        try:
            s_date = date.fromisoformat(start_date)
            e_date = date.fromisoformat(end_date)
            if s_date > e_date:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="La fecha de inicio no puede ser posterior a la fecha de fin."
                )
            return s_date, e_date
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de fecha inválido. Use YYYY-MM-DD."
            )
    else:
        e_date = date.today()
        s_date = e_date - timedelta(days=default_days)
        return s_date, e_date

@router.get("/summary", response_model=AdminMetricsSummary)
def get_admin_metrics_summary(
    start_date: Optional[str] = Query(None, description="Fecha de inicio (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Fecha de fin (YYYY-MM-DD)"),
    admin: dict = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """
    Obtiene un resumen global de las métricas de la plataforma, opcionalmente filtrado por un rango de fechas.
    Si no se especifican fechas, retorna el consolidado histórico acumulado de todos los tiempos.
    """
    try:
        # Filtro condicional por fechas
        start_datetime = None
        end_datetime = None
        s_date = None
        e_date = None
        
        if start_date and end_date:
            s_date, e_date = parse_date_range(start_date, end_date)
            start_datetime = datetime.combine(s_date, datetime.min.time())
            end_datetime = datetime.combine(e_date, datetime.max.time())

        # 1. Contar usuarios por rol (registrados en el rango o totales)
        query_user = db.query(User)
        if start_datetime and end_datetime:
            query_user = query_user.filter(User.created_at >= start_datetime, User.created_at <= end_datetime)
            
        total_users = query_user.count()
        total_buyers = query_user.filter(User.role == "buyer").count()
        total_sellers = query_user.filter(User.role == "seller").count()

        # 2. Contar tiendas por estado (registradas en el rango o totales)
        query_store = db.query(Store)
        if start_datetime and end_datetime:
            query_store = query_store.filter(Store.created_at >= start_datetime, Store.created_at <= end_datetime)
            
        total_stores = query_store.count()
        active_stores = query_store.filter(Store.status == "active").count()
        pending_stores = query_store.filter(Store.status == "pending").count()
        suspended_stores = query_store.filter(Store.status == "suspended").count()

        # 3. Ventas y órdenes (sumar de StoreMetric o de Order)
        query_revenue_metrics = db.query(func.coalesce(func.sum(StoreMetric.revenue), 0.0))
        query_orders_metrics = db.query(func.coalesce(func.sum(StoreMetric.orders_delivered), 0))
        query_visits_metrics = db.query(func.coalesce(func.sum(StoreMetric.visits), 0))
        query_chats_metrics = db.query(func.coalesce(func.sum(StoreMetric.chat_sessions), 0))
        query_templates_metrics = db.query(func.coalesce(func.sum(StoreMetric.template_usage), 0))
        
        if s_date and e_date:
            query_revenue_metrics = query_revenue_metrics.filter(StoreMetric.date >= s_date, StoreMetric.date <= e_date)
            query_orders_metrics = query_orders_metrics.filter(StoreMetric.date >= s_date, StoreMetric.date <= e_date)
            query_visits_metrics = query_visits_metrics.filter(StoreMetric.date >= s_date, StoreMetric.date <= e_date)
            query_chats_metrics = query_chats_metrics.filter(StoreMetric.date >= s_date, StoreMetric.date <= e_date)
            query_templates_metrics = query_templates_metrics.filter(StoreMetric.date >= s_date, StoreMetric.date <= e_date)

        total_revenue_metrics = query_revenue_metrics.scalar()
        total_orders_metrics = query_orders_metrics.scalar()
        total_visits = int(query_visits_metrics.scalar())
        total_chats = int(query_chats_metrics.scalar())
        total_templates = int(query_templates_metrics.scalar())

        # Fallback de órdenes reales registradas
        query_revenue_orders = db.query(func.coalesce(func.sum(Order.total_amount), 0.0)).filter(Order.status == "completed")
        query_orders_count = db.query(Order).filter(Order.status == "completed")
        
        if start_datetime and end_datetime:
            query_revenue_orders = query_revenue_orders.filter(Order.created_at >= start_datetime, Order.created_at <= end_datetime)
            query_orders_count = query_orders_count.filter(Order.created_at >= start_datetime, Order.created_at <= end_datetime)
            
        total_revenue_orders = query_revenue_orders.scalar()
        total_orders_count = query_orders_count.count()

        # Elegimos el mayor valor (para asegurar consistencia si hay órdenes directas)
        total_revenue = float(max(total_revenue_metrics, total_revenue_orders))
        total_orders = int(max(total_orders_metrics, total_orders_count))

        # Si total_chats es 0, contamos directamente chats de la tabla
        if total_chats == 0:
            from ..models.chat import Chat
            query_chat_table = db.query(Chat)
            if start_datetime and end_datetime:
                query_chat_table = query_chat_table.filter(Chat.created_at >= start_datetime, Chat.created_at <= end_datetime)
            total_chats = query_chat_table.count()

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
    days: Optional[int] = Query(30, description="Número de días a retroceder (si no se especifican fechas)", ge=1, le=365),
    start_date: Optional[str] = Query(None, description="Fecha de inicio personalizada (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Fecha de fin personalizada (YYYY-MM-DD)"),
    admin: dict = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """
    Obtiene las métricas agregadas por día para armar gráficos temporales en el rango especificado o días relativos.
    """
    try:
        s_date, e_date = parse_date_range(start_date, end_date, default_days=days or 30)
        days_diff = (e_date - s_date).days
        
        if days_diff > 365:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El rango máximo permitido para gráficos diarios es de 365 días."
            )
            
        start_datetime = datetime.combine(s_date, datetime.min.time())
        end_datetime = datetime.combine(e_date, datetime.max.time())

        # 1. Agrupar ingresos y órdenes por día
        order_stats = db.query(
            func.date(Order.created_at).label("day"),
            func.count(Order.id).label("orders"),
            func.sum(Order.total_amount).label("revenue")
        ).filter(
            Order.status == "completed",
            Order.created_at >= start_datetime,
            Order.created_at <= end_datetime
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
            StoreMetric.date >= s_date,
            StoreMetric.date <= e_date
        ).group_by(
            StoreMetric.date
        ).all()

        metrics_map = {str(row.day): (int(row.visits), int(row.chats)) for row in metric_stats}

        # 3. Agrupar nuevos usuarios registrados por día
        user_stats = db.query(
            func.date(User.created_at).label("day"),
            func.count(User.id).label("new_users")
        ).filter(
            User.created_at >= start_datetime,
            User.created_at <= end_datetime
        ).group_by(
            func.date(User.created_at)
        ).all()

        users_map = {str(row.day): int(row.new_users) for row in user_stats}

        # 4. Combinar datos en un solo set por fecha
        chart_points = []
        for i in range(days_diff + 1):
            current_day = s_date + timedelta(days=i)
            day_str = str(current_day)

            # Buscar valores en los diccionarios mapeados
            orders_count, revenue = orders_map.get(day_str, (0, 0.0))
            _, chats_count = metrics_map.get(day_str, (0, 0))
            new_users_count = users_map.get(day_str, 0)

            # Si no hay chats registrados en las métricas, como fallback contamos de la tabla
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
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener datos de gráficos: {str(e)}"
        )

@router.get("/export")
def export_admin_metrics(
    start_date: Optional[str] = Query(None, description="Fecha de inicio (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Fecha de fin (YYYY-MM-DD)"),
    admin: dict = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """
    Exporta el reporte detallado diario de métricas en formato CSV compatible con Microsoft Excel en español.
    """
    try:
        s_date, e_date = parse_date_range(start_date, end_date, default_days=30)
        days_diff = (e_date - s_date).days
        
        if days_diff > 365:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El rango máximo permitido para exportar datos es de 365 días."
            )
            
        start_datetime = datetime.combine(s_date, datetime.min.time())
        end_datetime = datetime.combine(e_date, datetime.max.time())
        
        # 1. Obtener órdenes por día
        order_stats = db.query(
            func.date(Order.created_at).label("day"),
            func.count(Order.id).label("orders"),
            func.sum(Order.total_amount).label("revenue")
        ).filter(
            Order.status == "completed",
            Order.created_at >= start_datetime,
            Order.created_at <= end_datetime
        ).group_by(func.date(Order.created_at)).all()
        orders_map = {str(row.day): (int(row.orders), float(row.revenue or 0.0)) for row in order_stats}
        
        # 2. Obtener chats y visitas por día
        metric_stats = db.query(
            StoreMetric.date.label("day"),
            func.coalesce(func.sum(StoreMetric.visits), 0).label("visits"),
            func.coalesce(func.sum(StoreMetric.chat_sessions), 0).label("chats")
        ).filter(
            StoreMetric.date >= s_date,
            StoreMetric.date <= e_date
        ).group_by(StoreMetric.date).all()
        metrics_map = {str(row.day): (int(row.visits), int(row.chats)) for row in metric_stats}
        
        # 3. Obtener nuevos usuarios por día
        user_stats = db.query(
            func.date(User.created_at).label("day"),
            func.count(User.id).label("new_users")
        ).filter(
            User.created_at >= start_datetime,
            User.created_at <= end_datetime
        ).group_by(func.date(User.created_at)).all()
        users_map = {str(row.day): int(row.new_users) for row in user_stats}
        
        # Generar CSV en memoria
        output = io.StringIO()
        # BOM de UTF-8 para que Excel detecte la codificación de inmediato
        output.write('\ufeff')
        
        # Delimitador punto y coma (;) para compatibilidad en sistemas en español
        writer = csv.writer(output, delimiter=';')
        writer.writerow(["Fecha", "Ingresos (S/.)", "Pedidos Completados", "Interacciones Chat IA", "Nuevos Usuarios Registrados", "Visitas Estimadas"])
        
        for i in range(days_diff + 1):
            current_day = s_date + timedelta(days=i)
            day_str = str(current_day)
            
            orders_count, revenue = orders_map.get(day_str, (0, 0.0))
            visits_count, chats_count = metrics_map.get(day_str, (0, 0))
            new_users_count = users_map.get(day_str, 0)
            
            if chats_count == 0:
                from ..models.chat import Chat
                day_start = datetime.combine(current_day, datetime.min.time())
                day_end = datetime.combine(current_day, datetime.max.time())
                chats_count = db.query(Chat).filter(
                    Chat.created_at >= day_start,
                    Chat.created_at <= day_end
                ).count()
                
            writer.writerow([
                current_day.strftime("%d/%m/%Y"),
                f"{revenue:.2f}",
                orders_count,
                chats_count,
                new_users_count,
                visits_count
            ])
            
        output.seek(0)
        return StreamingResponse(
            io.BytesIO(output.read().encode("utf-8-sig")),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=reporte_altoq_metricas_{s_date}_a_{e_date}.csv",
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar la exportación de métricas: {str(e)}"
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
