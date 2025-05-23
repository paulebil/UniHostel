"""create all tables

Revision ID: b5c5fc5129c9
Revises: 
Create Date: 2025-04-02 14:35:35.063121

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b5c5fc5129c9'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('stripe_payments',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('payment_intent_id', sa.String(length=100), nullable=False),
    sa.Column('amount_received', sa.Float(), nullable=False),
    sa.Column('currency', sa.String(length=3), nullable=False),
    sa.Column('stripe_payment_status', sa.Enum('PENDING', 'COMPLETED', 'NOT_RECEIVED', 'FAILED', name='stripepaymentstatus'), nullable=False),
    sa.Column('transaction_id', sa.String(length=100), nullable=False),
    sa.Column('payment_method', sa.String(length=100), nullable=False),
    sa.Column('customer_id', sa.String(length=100), nullable=True),
    sa.Column('customer_email', sa.String(length=100), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('booking_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['booking_id'], ['bookings.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('payment_intent_id')
    )
    op.create_index(op.f('ix_stripe_payments_id'), 'stripe_payments', ['id'], unique=False)
    op.alter_column('rooms', 'booked_status',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('rooms', 'booked_status',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    op.drop_index(op.f('ix_stripe_payments_id'), table_name='stripe_payments')
    op.drop_table('stripe_payments')
    # ### end Alembic commands ###
