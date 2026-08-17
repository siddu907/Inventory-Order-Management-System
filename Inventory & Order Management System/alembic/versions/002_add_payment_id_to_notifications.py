"""add payment_id to notifications

Revision ID: 002
Revises: 001
Create Date: 2026-08-14 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Add payment_id column to notifications table
    op.add_column('notifications', sa.Column('payment_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_notifications_payment_id', 'notifications', 'payments', ['payment_id'], ['id'])


def downgrade():
    # Remove foreign key and payment_id column
    op.drop_constraint('fk_notifications_payment_id', 'notifications', type_='foreignkey')
    op.drop_column('notifications', 'payment_id')
