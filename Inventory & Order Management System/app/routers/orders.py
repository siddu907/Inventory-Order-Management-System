import csv
import io
from datetime import datetime
from enum import Enum

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.oauth2 import get_current_user
from app.core.permissions import require_roles
from app.core.constants import ORDER_STATUSES
from app.database import get_db
from app.models.user import User
from app.schemas.order import OrderCreate, OrderOut
from app.services.order_service import OrderService
from app.background.notification_tasks import notify_order_event, notify_low_stock


# Enum for order status to provide dropdown in Swagger UI
class OrderStatusEnum(str, Enum):
    PENDING = "Pending"
    CONFIRMED = "Confirmed"
    SHIPPED = "Shipped"
    DELIVERED = "Delivered"
    CANCELLED = "Cancelled"

router = APIRouter()


@router.post("", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def create_order(
    payload: OrderCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order, low_stock_products = OrderService(db).create_order(current_user.id, current_user.role, payload)
    
    # Trigger order created notification (in-app + email)
    background_tasks.add_task(notify_order_event, order.id, order.customer_id, "created")
    
    # Trigger low stock notifications for any products that dropped to low stock
    for inv in low_stock_products:
        if inv.product:
            background_tasks.add_task(
                notify_low_stock,
                product_id=inv.product_id,
                product_name=inv.product.name,
                product_sku=inv.product.sku,
                current_stock=inv.current_stock,
                min_stock=inv.min_stock_level
            )
    
    return order


@router.get("", response_model=list[OrderOut])
def list_orders(
    order_status: str | None = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return OrderService(db).list_orders(
        requesting_user_id=current_user.id,
        requesting_role=current_user.role,
        skip=skip, limit=limit,
        status_filter=order_status,
    )


@router.get("/export/csv")
def export_orders_csv(
    order_status: OrderStatusEnum | None = Query(
        default=None,
        description="Leave empty or",

    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Export all orders to CSV format. Only accessible by Admin and Staff."""
    # Only Admin and Staff can export orders
    require_roles(current_user, {"Admin", "Staff"})
    
    # Convert enum to string for service layer, handle None
    status_filter = order_status.value if order_status else None
    
    # Validate status if provided
    if status_filter and status_filter not in ORDER_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid order status '{status_filter}'. Valid values are: {', '.join(sorted(ORDER_STATUSES))}"
        )
    
    # Fetch all orders (no pagination for export)
    try:
        orders = OrderService(db).list_orders(
            requesting_user_id=current_user.id,
            requesting_role=current_user.role,
            skip=0,
            limit=10000,  # Large limit to get all orders
            status_filter=status_filter,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch orders: {str(e)}"
        )
    
    if not orders:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No orders found{f' with status {status_filter}' if status_filter else ''}"
        )
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write CSV headers
    writer.writerow([
        "Order ID",
        "Customer ID",
        "Customer Name",
        "Customer Email",
        "Order Date",
        "Order Status",
        "Product Name",
        "SKU",
        "Quantity",
        "Unit Price",
        "Item Subtotal",
        "Coupon Code",
        "Discount Amount",
        "Order Total",
        "Payment Status",
        "Payment Method"
    ])
    
    # Write order data - one row per order item
    for order in orders:
        # Get common order info
        order_id = order.id
        customer_id = order.customer_id if hasattr(order, 'customer_id') else "N/A"
        customer_name = order.customer.full_name if (hasattr(order, 'customer') and order.customer) else "N/A"
        customer_email = order.customer.email if (hasattr(order, 'customer') and order.customer) else "N/A"
        order_date_str = order.order_date.strftime("%Y-%m-%d %H:%M:%S") if order.order_date else "N/A"
        order_status_val = order.status
        order_total = f"{order.total_amount:.0f}"
        
        # Get coupon info
        coupon_code = order.coupon_code if hasattr(order, 'coupon_code') and order.coupon_code else "N/A"
        discount_amount = f"{order.discount_amount:.0f}" if hasattr(order, 'discount_amount') and order.discount_amount else "0"
        
        # Get payment info
        payment_status = "Unpaid"
        payment_method = "N/A"
        if hasattr(order, 'payment') and order.payment:
            payment_status = order.payment.status
            payment_method = order.payment.payment_method if hasattr(order.payment, 'payment_method') else "N/A"
        
        # Write one row for each order item
        if hasattr(order, 'items') and order.items:
            for item in order.items:
                product_name = item.product.name if (hasattr(item, 'product') and item.product) else "N/A"
                sku = item.product.sku if (hasattr(item, 'product') and item.product) else "N/A"
                quantity = item.quantity
                unit_price = f"{item.unit_price:.0f}"
                item_subtotal = f"{item.subtotal:.0f}"
                
                writer.writerow([
                    order_id,
                    customer_id,
                    customer_name,
                    customer_email,
                    order_date_str,
                    order_status_val,
                    product_name,
                    sku,
                    quantity,
                    unit_price,
                    item_subtotal,
                    coupon_code,
                    discount_amount,
                    order_total,
                    payment_status,
                    payment_method
                ])
        else:
            # If order has no items, write one row with N/A for product info
            writer.writerow([
                order_id,
                customer_id,
                customer_name,
                customer_email,
                order_date_str,
                order_status_val,
                "N/A",
                "N/A",
                "0",
                "0",
                "0",
                coupon_code,
                discount_amount,
                order_total,
                payment_status,
                payment_method
            ])
    
    # Prepare response
    output.seek(0)
    status_suffix = f"_{status_filter.lower()}" if status_filter else ""
    filename = f"orders_export{status_suffix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/{order_id}", response_model=OrderOut)
def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return OrderService(db).get_order(order_id, current_user.id, current_user.role)


@router.put("/{order_id}/confirm", response_model=OrderOut)
def confirm_order(
    order_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = OrderService(db).update_status(order_id, "Confirmed", current_user.id, current_user.role)
    background_tasks.add_task(notify_order_event, order.id, order.customer_id, "confirmed")
    return order


@router.put("/{order_id}/ship", response_model=OrderOut)
def ship_order(
    order_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = OrderService(db).update_status(order_id, "Shipped", current_user.id, current_user.role)
    background_tasks.add_task(notify_order_event, order.id, order.customer_id, "shipped")
    return order


@router.put("/{order_id}/deliver", response_model=OrderOut)
def deliver_order(
    order_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = OrderService(db).update_status(order_id, "Delivered", current_user.id, current_user.role)
    background_tasks.add_task(notify_order_event, order.id, order.customer_id, "delivered")
    return order


@router.put("/{order_id}/cancel", response_model=OrderOut)
def cancel_order(
    order_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = OrderService(db).update_status(order_id, "Cancelled", current_user.id, current_user.role)
    background_tasks.add_task(notify_order_event, order.id, order.customer_id, "cancelled")
    return order
