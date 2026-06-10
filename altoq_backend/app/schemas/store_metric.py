from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional

class StoreMetricBase(BaseModel):
    store_id: int
    date: date
    visits: int = 0
    products_published: int = 0
    orders_delivered: int = 0
    revenue: float = 0.0
    chat_sessions: int = 0
    template_usage: int = 0
    new_users: int = 0
    avg_rating: float = 0.0

class StoreMetricCreate(StoreMetricBase):
    pass

class StoreMetricUpdate(BaseModel):
    visits: Optional[int] = None
    products_published: Optional[int] = None
    orders_delivered: Optional[int] = None
    revenue: Optional[float] = None
    chat_sessions: Optional[int] = None
    template_usage: Optional[int] = None
    new_users: Optional[int] = None
    avg_rating: Optional[float] = None

class StoreMetricResponse(StoreMetricBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DashboardSummary(BaseModel):
    store_id: int
    total_visits: int
    total_products: int
    total_orders_delivered: int
    total_revenue: float
    total_chat_sessions: int
    average_rating: float
    today_visits: int
    today_orders: int
    today_revenue: float
    weekly_growth: Optional[float] = None  # Porcentaje de crecimiento semanal

class MetricPeriod(BaseModel):
    period: str  # "daily", "weekly", "monthly"
    start_date: date
    end_date: date
    metrics: list[StoreMetricResponse]
