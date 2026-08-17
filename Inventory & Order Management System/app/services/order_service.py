from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.constants import VALID_TRANSITIONS
from app.models.order import Order, OrderItem
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.order import OrderCreate
from app.services.coupon_service import CouponService


class OrderService:
    def __init__(self, db: Session):
        self.db = db
        self.order_repo = OrderRepository(db)
        self.product_repo = ProductRepository(db)
        self.inv_repo = InventoryRepository(db)

    def create_order(self, customer_id: int, requesting_role: str, payload: OrderCreate) -> Order:
        """Validate items, reduce stock, create order."""
        # Only customers can create orders
        if requesting_role not in {"Customer"}:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only customers can create orders"
            )
        
        if not payload.items:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Order must contain at least one item")

        order_items = []
        total_amount = 0.0

        for item_in in payload.items:
            product = self.product_repo.get_by_id(item_in.product_id)
            if not product:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product {item_in.product_id} not found")
            if product.status != "Active":
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Product '{product.name}' is not active")

            inv = self.inv_repo.get_by_product_id(item_in.product_id)
            available = inv.current_stock if inv else product.stock_quantity
            if available < item_in.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient stock for '{product.name}'. "
                           f"Available: {available}, requested: {item_in.quantity}",
                )

            subtotal = round(product.price * item_in.quantity, 2)
            total_amount += subtotal
            order_items.append((product, item_in.quantity, subtotal, inv))

        # Apply coupon if provided
        coupon = None
        discount_amount = 0.0
        final_total = round(total_amount, 2)
        
        if payload.coupon_code:
            coupon_service = CouponService(self.db)
            coupon, discounted_total = coupon_service.apply_coupon(payload.coupon_code, total_amount)
            discount_amount = round(total_amount - discounted_total, 2)
            final_total = round(discounted_total, 2)

        # create order header
        order = Order(
            customer_id=customer_id, 
            total_amount=final_total,
            coupon_id=coupon.id if coupon else None,
            coupon_code=coupon.code if coupon else None,
            discount_amount=discount_amount
        )
        self.db.add(order)
        self.db.flush()  # get order.id without committing

        # create items and reduce stock
        low_stock_products = []  # Track products that dropped to low stock
        for product, qty, subtotal, inv in order_items:
            oi = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=qty,
                unit_price=product.price,
                subtotal=subtotal,
            )
            self.db.add(oi)
            # reduce stock
            if inv:
                inv.current_stock -= qty
                product.stock_quantity = inv.current_stock
                # Check if stock dropped to or below minimum level
                if inv.current_stock <= inv.min_stock_level:
                    low_stock_products.append(inv)
            else:
                product.stock_quantity -= qty

        # Increment coupon usage after successful order creation
        if coupon:
            coupon_service.increment_usage(coupon)

        self.db.commit()
        self.db.refresh(order)
        
        # Return order and list of inventories that need low stock notification
        return order, low_stock_products

    def get_order(self, order_id: int, requesting_user_id: int,
                  requesting_role: str) -> Order:
        order = self.order_repo.get_by_id(order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        if requesting_role == "Customer" and order.customer_id != requesting_user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not allowed to view this order")
        return order

    def list_orders(self, requesting_user_id: int, requesting_role: str,
                    skip: int = 0, limit: int = 100,
                    status_filter: str | None = None) -> list[Order]:
        customer_id = requesting_user_id if requesting_role == "Customer" else None
        return self.order_repo.get_all(skip=skip, limit=limit,customer_id=customer_id,status=status_filter)

    def update_status(self, order_id: int, new_status: str,
                      requesting_user_id: int, requesting_role: str) -> Order:
        order = self.order_repo.get_by_id(order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Order not found")

        # Role-based permissions for order status changes
        if requesting_role == "Customer":
            # Customers can only cancel their own orders
            if order.customer_id != requesting_user_id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not allowed to modify this order")
            if new_status != "Cancelled":
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Customers can only cancel orders")
        elif requesting_role in {"Admin", "Staff"}:
            # Admin and Staff can confirm, ship, deliver orders
            pass  # They have full access
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Invalid role")

        # Check if order is already in the requested status
        if order.status == new_status:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Order is already in '{new_status}' status"
            )

        # Validate status transition with helpful error messages
        allowed = VALID_TRANSITIONS.get(order.status, set())
        if new_status not in allowed:
            # Provide specific guidance based on the attempted transition
            error_msg = self._get_transition_error_message(order.status, new_status)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )

        # restore stock if cancelling
        if new_status == "Cancelled":
            self._restore_stock(order)

        order.status = new_status
        return self.order_repo.update(order)

    def _restore_stock(self, order: Order) -> None:
        for item in order.items:
            inv = self.inv_repo.get_by_product_id(item.product_id)
            if inv:
                inv.current_stock += item.quantity
                item.product.stock_quantity = inv.current_stock
            elif item.product:
                item.product.stock_quantity += item.quantity

    def _get_transition_error_message(self, current_status: str, new_status: str) -> str:
        """Generate helpful error messages for invalid status transitions."""
        # Handle attempts to change final statuses
        if current_status == "Delivered":
            return "Cannot change status of delivered orders."
        
        if current_status == "Cancelled":
            return "Cannot change status of cancelled orders."
        
        # Provide specific guidance for common invalid transitions
        transition_messages = {
            ("Pending", "Shipped"): "Cannot transition order from 'Pending' to 'Shipped'. Order must be Confirmed first",
            ("Pending", "Delivered"): "Cannot transition order from 'Pending' to 'Delivered'. Order must be Confirmed and Shipped first",
            ("Confirmed", "Delivered"): "Cannot transition order from 'Confirmed' to 'Delivered'. Order must be Shipped first",
            ("Confirmed", "Pending"): "Cannot move order back to 'Pending' status. Orders can only move forward or be cancelled",
            ("Shipped", "Pending"): "Cannot move order back to 'Pending' status. Orders can only move forward or be cancelled",
            ("Shipped", "Confirmed"): "Cannot move order back to 'Confirmed' status. Orders can only move forward or be cancelled",
        }
        
        # Check if we have a specific message for this transition
        key = (current_status, new_status)
        if key in transition_messages:
            return transition_messages[key]
        
        # Default message for other invalid transitions
        return f"Cannot transition order from '{current_status}' to '{new_status}'"
