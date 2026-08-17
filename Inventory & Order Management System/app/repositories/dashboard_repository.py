from datetime import date, datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.inventory import Inventory
from app.models.order import Order
from app.models.payment import Payment
from app.models.product import Product
from app.models.category import Category
from app.models.user import User


class DashboardRepository:
    def __init__(self, db: Session):
        self.db = db

    def admin_stats(self) -> dict:
        total_customers = (self.db.query(User).filter(User.role == "Customer",User.is_deleted.is_(False)).count())
        total_staff = (self.db.query(User).filter( User.role == "Staff", User.is_deleted.is_(False)).count())
        total_products = ( self.db.query(Product) .filter(Product.is_deleted.is_(False)).count())
        total_categories = (self.db.query(Category)  .filter(Category.is_deleted.is_(False)) .count())
        total_orders = (self.db.query(Order).filter(Order.is_deleted.is_(False)).count())
        pending_orders = ( self.db.query(Order) .filter( Order.status == "Pending", Order.is_deleted.is_(False)) .count())
        completed_orders = (self.db.query(Order).filter(Order.status == "Delivered",Order.is_deleted.is_(False)) .count())
        cancelled_orders = (self.db.query(Order).filter( Order.status == "Cancelled", Order.is_deleted.is_(False)).count())
        low_stock = (self.db.query(Inventory).join(Product).filter(Product.is_deleted.is_(False),Inventory.current_stock <= Inventory.min_stock_level).count())
        total_revenue = (self.db.query(Payment).filter(Payment.status == "Paid").with_entities(func.coalesce(func.sum(Payment.amount), 0 )) .scalar() or 0.0)
        return {
            "total_customers": total_customers,
            "total_staff": total_staff,
            "total_products": total_products,
            "total_categories": total_categories,
            "total_orders": total_orders,
            "pending_orders": pending_orders,
            "completed_orders": completed_orders,
            "cancelled_orders": cancelled_orders,
            "low_stock_products": low_stock,
            "total_revenue": float(total_revenue),
        }

    def staff_stats(self) -> dict:
        total_products = (self.db.query(Product).filter(Product.is_deleted.is_(False)).count())
        low_stock = (self.db.query(Inventory).join(Product).filter(Product.is_deleted.is_(False),Inventory.current_stock <= Inventory.min_stock_level ).count())
        today = date.today()
        today_orders = (self.db.query(Order).filter(Order.is_deleted.is_(False), Order.order_date >= datetime(today.year,today.month,today.day)).count())
        pending_orders = (self.db.query(Order).filter(Order.status == "Pending",Order.is_deleted.is_(False)).count())
        completed_orders = (self.db.query(Order).filter( Order.status == "Delivered",Order.is_deleted.is_(False)).count())
        return {
            "total_products": total_products,
            "low_stock_products": low_stock,
            "today_orders": today_orders,
            "pending_orders": pending_orders,
            "completed_orders": completed_orders,
        }

    def customer_stats(self, customer_id: int) -> dict:
        total_orders = (self.db.query(Order).filter(Order.customer_id == customer_id,Order.is_deleted.is_(False)).count())
        pending_orders = (self.db.query(Order).filter( Order.customer_id == customer_id, Order.status == "Pending", Order.is_deleted.is_(False)).count())
        completed_orders = ( self.db.query(Order) .filter(Order.customer_id == customer_id,Order.status == "Delivered",Order.is_deleted.is_(False)).count())
        cancelled_orders = (self.db.query(Order).filter(Order.customer_id == customer_id,Order.status == "Cancelled",Order.is_deleted.is_(False)).count())
        spent = (self.db.query(Payment).join(Order).filter( Order.customer_id == customer_id,Payment.status == "Paid" ).with_entities(func.coalesce(func.sum(Payment.amount), 0)).scalar()) or 0.0

        return {
            "total_orders": total_orders,
            "pending_orders": pending_orders,
            "completed_orders": completed_orders,
            "cancelled_orders": cancelled_orders,
            "total_amount_spent": float(spent),
        }