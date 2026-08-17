from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User
from app.services.notification_service import NotificationService
from app.services.email_service import EmailService

def notify_order_event(order_id: int, customer_id: int, event: str) -> None:
    
    # Customer-facing titles and messages
    customer_titles = {
        "created":"Order Placed",
        "confirmed":"Order Confirmed",
        "shipped":"Order Shipped",
        "delivered":"Order Delivered",
        "cancelled":"Order Cancelled",
    }
    customer_messages = {
        "created":f"Your order #{order_id} has been placed successfully.",
        "confirmed":f"Your order #{order_id} has been confirmed and is being processed.",
        "shipped":f"Your order #{order_id} has been shipped and is on its way.",
        "delivered":f"Your order #{order_id} has been delivered. Enjoy!",
        "cancelled":f"Your order #{order_id} has been cancelled.",
    }
    
    # Staff/Admin-facing titles and messages
    staff_titles = {
        "created":"New Order Received",
        "cancelled":"Order Cancelled",
    }
    staff_messages = {
        "created":f"New order #{order_id} has been placed.",
        "cancelled":f"Order #{order_id} has been cancelled.",
    }
    
    email_bodies = {
        "created": f"""Dear Customer,

Thank you for your order!

Order Details:
--------------
Order Number: #{order_id}
Status: Placed

Your order has been received and will be processed shortly.

You can track your order status in your account.

Thank you for shopping with us!

---
Inventory & Order Management System""",
        "confirmed": f"""Dear Customer,

Good news! Your order has been confirmed.

Order Number: #{order_id}
Status: Confirmed

Your order is now being prepared for shipment.

Thank you for your patience!

---
Inventory & Order Management System""",
        "shipped": f"""Dear Customer,

Your order is on its way!

Order Number: #{order_id}
Status: Shipped

Your order has been dispatched and will reach you soon.

Thank you for your order!

---
Inventory & Order Management System""",
        "delivered": f"""Dear Customer,

Your order has been delivered!

Order Number: #{order_id}
Status: Delivered

We hope you enjoy your purchase!

Please consider leaving a review for the products you purchased.

Thank you for choosing us!

---
Inventory & Order Management System""",
        "cancelled": f"""Dear Customer,

Your order has been cancelled.

Order Number: #{order_id}
Status: Cancelled

If you have any questions, please contact our support team.

Thank you!

---
Inventory & Order Management System""",
    }
    
    db: Session = SessionLocal()
    try:
        # Create in-app notification for CUSTOMER
        NotificationService(db).create(
            user_id=customer_id,
            title=customer_titles.get(event, "Order Update"),
            message=customer_messages.get(event, f"Order #{order_id} status updated to {event}."),
            order_id=order_id,
            notification_type=f"order_{event}",
        )
        
        # Send email notification to CUSTOMER
        customer = db.query(User).filter(User.id == customer_id, User.is_deleted.is_(False)).first()
        if customer and customer.email:
            try:
                EmailService.send_email(
                    to_email=customer.email,
                    subject=f"{customer_titles.get(event, 'Order Update')} - Order #{order_id}",
                    body=email_bodies.get(event, f"Your order #{order_id} status has been updated to {event}.")
                )
            except Exception as e:
                print(f"Failed to send order email to {customer.email}: {e}")
        
        # For "created" and "cancelled" events, notify ALL Staff and Admin users
        if event in {"created", "cancelled"}:
            staff_admin_users = (
                db.query(User)
                .filter(User.role.in_(["Admin", "Staff"]), User.is_deleted.is_(False))
                .all()
            )
            
            for user in staff_admin_users:
                # Create in-app notification
                NotificationService(db).create(
                    user_id=user.id,
                    title=staff_titles.get(event, "Order Update"),
                    message=staff_messages.get(event, f"Order #{order_id} status updated."),
                    order_id=order_id,
                    notification_type=f"order_{event}",
                )
                
                # Send email notification
                if user.email:
                    try:
                        email_body = f"""Dear {user.full_name},

{"New Order Notification" if event == "created" else "Order Cancellation Notice"}
{"=" * 25}

Order Number: #{order_id}
Event: {"Order Placed" if event == "created" else "Order Cancelled"}

{"A new order has been placed and requires processing." if event == "created" else "An order has been cancelled."}

Please check the order management system for details.

---
Inventory & Order Management System"""
                        
                        EmailService.send_email(
                            to_email=user.email,
                            subject=f"{staff_titles.get(event, 'Order Update')} - Order #{order_id}",
                            body=email_body
                        )
                    except Exception as e:
                        print(f"Failed to send order email to {user.email}: {e}")
    finally:
        db.close()


def notify_payment_completed(order_id: int, customer_id: int, amount: float, method: str, payment_id: int | None = None) -> None:
    db: Session = SessionLocal()
    try:
        # Create in-app notification for CUSTOMER
        NotificationService(db).create(
            user_id=customer_id,
            title="Payment Successful",
            message=(f"Payment of ₹{amount:.2f} for order #{order_id} "
                     f"was processed successfully via {method}."),
            order_id=order_id,
            payment_id=payment_id,
            notification_type="payment_completed",
        )
        
        # Send email notification to CUSTOMER
        customer = db.query(User).filter(User.id == customer_id, User.is_deleted.is_(False)).first()
        if customer and customer.email:
            try:
                email_body = f"""Dear {customer.full_name},

Your payment has been received successfully!

Payment Details:
----------------
Order Number: #{order_id}
Amount Paid: ₹{amount:.2f}
Payment Method: {method}
Status: Successful

Your order will be processed shortly.

Thank you for your payment!

---
Inventory & Order Management System"""
                
                EmailService.send_email(
                    to_email=customer.email,
                    subject=f"Payment Received - Order #{order_id}",
                    body=email_body
                )
            except Exception as e:
                print(f"Failed to send payment email to {customer.email}: {e}")
        
        # Notify ALL Admin users about payment completion
        admin_users = (
            db.query(User)
            .filter(User.role == "Admin", User.is_deleted.is_(False))
            .all()
        )
        
        for admin in admin_users:
            # Create in-app notification
            NotificationService(db).create(
                user_id=admin.id,
                title="Payment Received",
                message=f"Payment of ₹{amount:.2f} for order #{order_id} has been completed.",
                order_id=order_id,
                payment_id=payment_id,
                notification_type="payment_completed",
            )
            
            # Send email notification
            if admin.email:
                try:
                    admin_email_body = f"""Dear {admin.full_name},

Payment Received
================

Order Number: #{order_id}
Amount: ₹{amount:.2f}
Payment Method: {method}
Status: Completed

The order can now be processed.

---
Inventory & Order Management System"""
                    
                    EmailService.send_email(
                        to_email=admin.email,
                        subject=f"Payment Received - Order #{order_id}",
                        body=admin_email_body
                    )
                except Exception as e:
                    print(f"Failed to send payment email to {admin.email}: {e}")
    finally:
        db.close()


def notify_low_stock(product_id: int, product_name: str, product_sku: str,
                     current_stock: int, min_stock: int) -> None:
    """Notify all Admin and Staff users that a product is low on stock - IMMEDIATE notifications and emails."""
    db: Session = SessionLocal()
    try:
        admins_staff = (
            db.query(User)
            .filter(User.role.in_(["Admin", "Staff"]), User.is_deleted.is_(False))
            .all()
        )
        
        svc = NotificationService(db)
        for user in admins_staff:
            # Create in-app notification
            svc.create(
                user_id=user.id,
                title="Low Stock Alert",
                message=(f"Product '{product_name}' (SKU: {product_sku}) is low on stock. "
                         f"Current: {current_stock}, Minimum level: {min_stock}."),
                notification_type="low_stock",
            )
            
            # Send immediate email notification
            if user.email:
                try:
                    email_body = f"""Dear {user.full_name},

Low Stock Alert
===============

Product Details:
----------------
Product Name: {product_name}
SKU: {product_sku}
Current Stock: {current_stock}
Minimum Level: {min_stock}
Shortage: {min_stock - current_stock} units

Action Required:
Please restock this product as soon as possible to avoid stockouts.

---
Inventory & Order Management System"""
                    
                    EmailService.send_email(
                        to_email=user.email,
                        subject=f"Low Stock Alert - {product_name}",
                        body=email_body
                    )
                except Exception as e:
                    print(f"Failed to send low stock email to {user.email}: {e}")
    finally:
        db.close()


def notify_payment_refunded(order_id: int, customer_id: int, amount: float, method: str, payment_id: int | None = None) -> None:
    """Notify customer that their payment has been refunded."""
    db: Session = SessionLocal()
    try:
        # Create in-app notification for CUSTOMER
        NotificationService(db).create(
            user_id=customer_id,
            title="Payment Refunded",
            message=(f"Refund of ₹{amount:.2f} for order #{order_id} has been processed. "
                     f"The amount will be credited back to your {method}."),
            order_id=order_id,
            payment_id=payment_id,
            notification_type="payment_refunded",
        )
        
        # Send email notification to CUSTOMER
        customer = db.query(User).filter(User.id == customer_id, User.is_deleted.is_(False)).first()
        if customer and customer.email:
            try:
                email_body = f"""Dear {customer.full_name},

Payment Refund Processed
========================

Refund Details:
---------------
Order Number: #{order_id}
Refund Amount: ₹{amount:.2f}
Original Payment Method: {method}
Status: Refunded

The refund has been processed successfully. The amount will be credited back to your {method} within 5-7 business days.

If you have any questions, please contact our support team.

Thank you for your understanding!

---
Inventory & Order Management System"""
                
                EmailService.send_email(
                    to_email=customer.email,
                    subject=f"Refund Processed - Order #{order_id}",
                    body=email_body
                )
            except Exception as e:
                print(f"Failed to send refund email to {customer.email}: {e}")
    finally:
        db.close()
