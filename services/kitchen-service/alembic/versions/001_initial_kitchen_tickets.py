"""Initial kitchen_tickets and ticket_items tables.

Revision ID: 001
Revises:
Create Date: 2025-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "kitchen_tickets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("restaurant_id", sa.String(64), nullable=False),
        sa.Column("table_label", sa.String(64), nullable=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="NEW"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_kitchen_tickets_tenant_id", "kitchen_tickets", ["tenant_id"], unique=False)
    op.create_index("ix_kitchen_tickets_order_id", "kitchen_tickets", ["order_id"], unique=False)

    op.create_table(
        "ticket_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ticket_id", sa.Integer(), nullable=False),
        sa.Column("menu_item_id", sa.Integer(), nullable=False),
        sa.Column("menu_item_name", sa.String(255), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("notes", sa.String(512), nullable=True),
        sa.ForeignKeyConstraint(["ticket_id"], ["kitchen_tickets.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ticket_items_ticket_id", "ticket_items", ["ticket_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_ticket_items_ticket_id", table_name="ticket_items")
    op.drop_table("ticket_items")
    op.drop_index("ix_kitchen_tickets_order_id", table_name="kitchen_tickets")
    op.drop_index("ix_kitchen_tickets_tenant_id", table_name="kitchen_tickets")
    op.drop_table("kitchen_tickets")
