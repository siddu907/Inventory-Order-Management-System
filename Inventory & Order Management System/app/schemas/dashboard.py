from pydantic import BaseModel


class AdminDashboardStats(BaseModel):
    total_customers: int
    total_staff: int
    total_products: int
    total_categories:int
    total_orders: int
    pending_orders:int
    completed_orders:int
    cancelled_orders:int
    low_stock_products:int
    total_revenue:float


class StaffDashboardStats(BaseModel):
    total_products:int
    low_stock_products:int
    today_orders:int
    pending_orders:int
    completed_orders:int


class CustomerDashboardStats(BaseModel):
    total_orders:int
    pending_orders:int
    completed_orders:int
    cancelled_orders:int
    total_amount_spent:float
