from pydantic import BaseModel
from typing import Optional, List

class AdminMetricsSummary(BaseModel):
    total_revenue: float
    total_orders: int
    total_users: int
    total_buyers: int
    total_sellers: int
    total_stores: int
    active_stores: int
    pending_stores: int
    suspended_stores: int
    total_visits: int
    total_chats: int
    total_templates: int

class AdminMetricChartPoint(BaseModel):
    date: str
    revenue: float
    orders: int
    chats: int
    new_users: int

class AdminStoreRanking(BaseModel):
    store_id: int
    name: str
    owner_name: Optional[str]
    email: str
    revenue: float
    orders_count: int
    avg_rating: float
    visits_count: int
    status: str

    class Config:
        from_attributes = True
