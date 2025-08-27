"""Add string to queue_item_outcomes

Revision ID: 9ae29b5db790
Revises: 571e55ab5ed5
Create Date: 2025-06-06 20:11:43.675998

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9ae29b5db790"
down_revision = "571e55ab5ed5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "queue_item_outcomes",
        sa.Column("string", sa.String(length=255), nullable=False),
    )


def downgrade() -> None:
    op.drop_column("queue_item_outcomes", "string")
