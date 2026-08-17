USER_ROLES = {"Admin", "Staff", "Customer"}

ORDER_STATUSES = {"Pending", "Confirmed", "Shipped", "Delivered", "Cancelled"}

VALID_TRANSITIONS = {
    "Pending": {"Confirmed", "Cancelled"},
    "Confirmed":{"Shipped",   "Cancelled"},
    "Shipped": {"Delivered", "Cancelled"},
    "Delivered": set(),
    "Cancelled": set(),
}

PAYMENT_STATUSES = {"Pending", "Paid", "Failed", "Refunded"}
PAYMENT_METHODS  = {"Cash", "Card", "UPI", "Online"}

PRODUCT_STATUSES  = {"Active", "Inactive"}
CATEGORY_STATUSES = {"Active", "Inactive"}

LOW_STOCK_NOTIFICATION_TITLE = "Low Stock Alert"
