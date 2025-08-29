"""Add fail_silently

Revision ID: 03d4e411c575
Revises: 8406a0af7394
Create Date: 2025-08-27 00:44:17.788937

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "03d4e411c575"
down_revision = "8406a0af7394"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "queue_items",
        sa.Column(
            "fail_silently", sa.Boolean(), server_default=sa.text("0"), nullable=False
        ),
    )


def downgrade() -> None:
    op.drop_column("queue_items", "fail_silently")
