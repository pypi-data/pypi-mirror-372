"""Add traceback to queue_items

Revision ID: 8023b9eecdd1
Revises: 9ae29b5db790
Create Date: 2025-06-07 12:32:49.485214

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "8023b9eecdd1"
down_revision = "9ae29b5db790"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("queue_items", sa.Column("traceback", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("queue_items", "traceback")
