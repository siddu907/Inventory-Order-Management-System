"""Initial schema for Inventory & Order Management System

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # users
    # ------------------------------------------------------------------
    op.create_table(
        "users",
        sa.Column("id",              sa.Integer,     primary_key=True),
        sa.Column("email",           sa.String,      nullable=False),
        sa.Column("full_name",       sa.String,      nullable=False),
        sa.Column("hashed_password", sa.String,      nullable=False),
        sa.Column("role",            sa.String(20),  nullable=False, server_default="Customer"),
        sa.Column("phone",           sa.String,      nullable=False),
        sa.Column("address",         sa.String,      nullable=False),
        sa.Column("profile_image",   sa.String,      nullable=True),
        sa.Column("is_active",       sa.Boolean,     server_default=sa.true()),
        sa.Column("is_deleted",      sa.Boolean,     server_default=sa.false()),
    )
    op.create_index("ix_users_id",    "users", ["id"])
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_phone", "users", ["phone"], unique=True)

    # ------------------------------------------------------------------
    # categories
    # ------------------------------------------------------------------
    op.create_table(
        "categories",
        sa.Column("id",          sa.Integer,      primary_key=True),
        sa.Column("name",        sa.String(100),  nullable=False),
        sa.Column("description", sa.Text,         nullable=True),
        sa.Column("status",      sa.String(20),   nullable=False, server_default="Active"),
        sa.Column("is_deleted",  sa.Boolean,      server_default=sa.false()),
        sa.Column("created_at",  sa.DateTime,     server_default=sa.func.now()),
        sa.Column("updated_at",  sa.DateTime,     server_default=sa.func.now()),
        sa.UniqueConstraint("name", name="uq_category_name"),
    )
    op.create_index("ix_categories_id",   "categories", ["id"])
    op.create_index("ix_categories_name", "categories", ["name"], unique=True)

    # ------------------------------------------------------------------
    # products
    # ------------------------------------------------------------------
    op.create_table(
        "products",
        sa.Column("id",             sa.Integer,      primary_key=True),
        sa.Column("name",           sa.String(200),  nullable=False),
        sa.Column("description",    sa.Text,         nullable=True),
        sa.Column("category_id",    sa.Integer,      sa.ForeignKey("categories.id"), nullable=False),
        sa.Column("price",          sa.Float,        nullable=False),
        sa.Column("sku",            sa.String(100),  nullable=False),
        sa.Column("stock_quantity", sa.Integer,      nullable=False, server_default="0"),
        sa.Column("status",         sa.String(20),   nullable=False, server_default="Active"),
        sa.Column("product_image",  sa.String,       nullable=True),
        sa.Column("is_deleted",     sa.Boolean,      server_default=sa.false()),
        sa.Column("created_at",     sa.DateTime,     server_default=sa.func.now()),
        sa.Column("updated_at",     sa.DateTime,     server_default=sa.func.now()),
    )
    op.create_index("ix_products_id",          "products", ["id"])
    op.create_index("ix_products_name",        "products", ["name"])
    op.create_index("ix_products_sku",         "products", ["sku"], unique=True)
    op.create_index("ix_products_category_id", "products", ["category_id"])

    # ------------------------------------------------------------------
    # inventory
    # ------------------------------------------------------------------
    op.create_table(
        "inventory",
        sa.Column("id",              sa.Integer, primary_key=True),
        sa.Column("product_id",      sa.Integer, sa.ForeignKey("products.id"), nullable=False),
        sa.Column("current_stock",   sa.Integer, nullable=False, server_default="0"),
        sa.Column("min_stock_level", sa.Integer, nullable=False, server_default="0"),
        sa.Column("max_stock_level", sa.Integer, nullable=False, server_default="100"),
        sa.Column("last_updated",    sa.DateTime, server_default=sa.func.now()),
        sa.UniqueConstraint("product_id", name="uq_inventory_product"),
    )
    op.create_index("ix_inventory_id",         "inventory", ["id"])
    op.create_index("ix_inventory_product_id", "inventory", ["product_id"], unique=True)

    # ------------------------------------------------------------------
    # orders
    # ------------------------------------------------------------------
    op.create_table(
        "orders",
        sa.Column("id",           sa.Integer,     primary_key=True),
        sa.Column("customer_id",  sa.Integer,     sa.ForeignKey("users.id"), nullable=False),
        sa.Column("total_amount", sa.Float,       nullable=False, server_default="0"),
        sa.Column("order_date",   sa.DateTime,    server_default=sa.func.now()),
        sa.Column("status",       sa.String(30),  nullable=False, server_default="Pending"),
        sa.Column("is_deleted",   sa.Boolean,     server_default=sa.false()),
    )
    op.create_index("ix_orders_id",          "orders", ["id"])
    op.create_index("ix_orders_customer_id", "orders", ["customer_id"])

    # ------------------------------------------------------------------
    # order_items
    # ------------------------------------------------------------------
    op.create_table(
        "order_items",
        sa.Column("id",         sa.Integer, primary_key=True),
        sa.Column("order_id",   sa.Integer, sa.ForeignKey("orders.id"),   nullable=False),
        sa.Column("product_id", sa.Integer, sa.ForeignKey("products.id"), nullable=False),
        sa.Column("quantity",   sa.Integer, nullable=False),
        sa.Column("unit_price", sa.Float,   nullable=False),
        sa.Column("subtotal",   sa.Float,   nullable=False),
    )
    op.create_index("ix_order_items_id",       "order_items", ["id"])
    op.create_index("ix_order_items_order_id", "order_items", ["order_id"])

    # ------------------------------------------------------------------
    # payments
    # ------------------------------------------------------------------
    op.create_table(
        "payments",
        sa.Column("id",             sa.Integer,    primary_key=True),
        sa.Column("order_id",       sa.Integer,    sa.ForeignKey("orders.id"), nullable=False),
        sa.Column("amount",         sa.Float,      nullable=False),
        sa.Column("payment_method", sa.String(50), nullable=False, server_default="Cash"),
        sa.Column("payment_date",   sa.DateTime,   nullable=True),
        sa.Column("status",         sa.String(20), nullable=False, server_default="Pending"),
        sa.UniqueConstraint("order_id", name="uq_payment_order"),
    )
    op.create_index("ix_payments_id",       "payments", ["id"])
    op.create_index("ix_payments_order_id", "payments", ["order_id"], unique=True)

    # ------------------------------------------------------------------
    # reviews
    # ------------------------------------------------------------------
    op.create_table(
        "reviews",
        sa.Column("id",          sa.Integer,  primary_key=True),
        sa.Column("product_id",  sa.Integer,  sa.ForeignKey("products.id"), nullable=False),
        sa.Column("customer_id", sa.Integer,  sa.ForeignKey("users.id"),    nullable=False),
        sa.Column("order_id",    sa.Integer,  sa.ForeignKey("orders.id"),   nullable=False),
        sa.Column("rating",      sa.Integer,  nullable=False),
        sa.Column("review",      sa.Text,     nullable=True),
        sa.Column("created_at",  sa.DateTime, server_default=sa.func.now()),
        sa.UniqueConstraint("product_id", "customer_id", "order_id",
                            name="uq_review_product_customer_order"),
    )
    op.create_index("ix_reviews_id",          "reviews", ["id"])
    op.create_index("ix_reviews_product_id",  "reviews", ["product_id"])
    op.create_index("ix_reviews_customer_id", "reviews", ["customer_id"])

    # ------------------------------------------------------------------
    # notifications
    # ------------------------------------------------------------------
    op.create_table(
        "notifications",
        sa.Column("id",                sa.Integer,      primary_key=True),
        sa.Column("user_id",           sa.Integer,      sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title",             sa.String(200),  nullable=False),
        sa.Column("message",           sa.Text,         nullable=False),
        sa.Column("is_read",           sa.Boolean,      server_default=sa.false()),
        sa.Column("created_at",        sa.DateTime,     server_default=sa.func.now()),
        sa.Column("order_id",          sa.Integer,      sa.ForeignKey("orders.id"), nullable=True),
        sa.Column("notification_type", sa.String(50),   nullable=True),
    )
    op.create_index("ix_notifications_id",      "notifications", ["id"])
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])


def downgrade() -> None:
    op.drop_table("notifications")
    op.drop_table("reviews")
    op.drop_table("payments")
    op.drop_table("order_items")
    op.drop_table("orders")
    op.drop_table("inventory")
    op.drop_table("products")
    op.drop_table("categories")
    op.drop_table("users")
