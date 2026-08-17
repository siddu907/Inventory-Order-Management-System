"""add coupons and order coupon fields

Revision ID: 003
Revises: 002
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create coupons table
    op.create_table(
        'coupons',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('discount_percent', sa.Float(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('usage_limit', sa.Integer(), nullable=True),
        sa.Column('used_count', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_coupons_id'), 'coupons', ['id'], unique=False)
    op.create_index(op.f('ix_coupons_code'), 'coupons', ['code'], unique=True)

    # Add coupon fields to orders table
    op.add_column('orders', sa.Column('coupon_id', sa.Integer(), nullable=True))
    op.add_column('orders', sa.Column('coupon_code', sa.String(), nullable=True))
    op.add_column('orders', sa.Column('discount_amount', sa.Float(), nullable=False, server_default='0.0'))
    
    # Create foreign key constraint
    op.create_foreign_key(
        'fk_orders_coupon_id_coupons',
        'orders', 'coupons',
        ['coupon_id'], ['id']
    )


def downgrade() -> None:
    # Drop foreign key constraint
    op.drop_constraint('fk_orders_coupon_id_coupons', 'orders', type_='foreignkey')
    
    # Remove coupon fields from orders table
    op.drop_column('orders', 'discount_amount')
    op.drop_column('orders', 'coupon_code')
    op.drop_column('orders', 'coupon_id')
    
    # Drop coupons table
    op.drop_index(op.f('ix_coupons_code'), table_name='coupons')
    op.drop_index(op.f('ix_coupons_id'), table_name='coupons')
    op.drop_table('coupons')
