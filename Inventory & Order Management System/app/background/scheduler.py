from apscheduler.schedulers.background import BackgroundScheduler
scheduler = BackgroundScheduler()

def check_low_stock_periodic() -> None:
    """Periodically scan inventory for low-stock products and notify admins/staff."""
    from app.database import SessionLocal
    from app.repositories.inventory_repository import InventoryRepository
    from app.background.notification_tasks import notify_low_stock

    db = SessionLocal()
    try:
        low_items = InventoryRepository(db).get_low_stock(limit=500)
        for inv in low_items:
            if inv.product:
                notify_low_stock(
                    product_id=inv.product_id,
                    product_name=inv.product.name,
                    product_sku=inv.product.sku,
                    current_stock=inv.current_stock,
                    min_stock=inv.min_stock_level,
                )
    finally:
        db.close()


def send_low_stock_email_batch() -> None:
    """Periodically send email alerts for all low-stock products (every 10 minutes)."""
    from app.database import SessionLocal
    from app.repositories.inventory_repository import InventoryRepository
    from app.models.user import User
    from app.services.email_service import EmailService

    db = SessionLocal()
    try:
        # Get all low stock items
        low_items = InventoryRepository(db).get_low_stock(limit=500)
        
        if not low_items:
            return  # No low stock items, skip email
        
        # Get all Admin and Staff users
        admins_staff = db.query(User).filter(
            User.role.in_(["Admin", "Staff"]),
            User.is_deleted.is_(False)
        ).all()
        
        if not admins_staff:
            return  # No recipients
        
        # Build email content
        subject = f"Low Stock Alert - {len(low_items)} Product(s) Need Attention"
        
        # Create email body with list of low stock products
        body = "Low Stock Alert Summary\n"
        body += "=" * 50 + "\n\n"
        body += f"The following {len(low_items)} product(s) are currently low on stock:\n\n"
        
        for idx, inv in enumerate(low_items, 1):
            if inv.product:
                body += f"{idx}. Product: {inv.product.name}\n"
                body += f"   SKU: {inv.product.sku}\n"
                body += f"   Current Stock: {inv.current_stock}\n"
                body += f"   Minimum Level: {inv.min_stock_level}\n"
                body += f"   Shortage: {inv.min_stock_level - inv.current_stock} units\n\n"
        
        body += "=" * 50 + "\n"
        body += "Please take necessary action to restock these items.\n"
        body += "\nThis is an automated alert sent every 10 minutes.\n"
        
        # Send email to each Admin/Staff
        for user in admins_staff:
            try:
                EmailService.send_email(
                    to_email=user.email,
                    subject=subject,
                    body=body
                )
            except Exception as e:
                # Log error but continue sending to other users
                print(f"Failed to send email to {user.email}: {e}")
    
    finally:
        db.close()


# Scheduler jobs
scheduler.add_job(check_low_stock_periodic, "interval", minutes=30, id="low_stock_check")
# Note: Batch email runs every 30 minutes as a backup/summary (immediate emails already sent per product)
scheduler.add_job(send_low_stock_email_batch, "interval", minutes=30, id="low_stock_email_batch")
