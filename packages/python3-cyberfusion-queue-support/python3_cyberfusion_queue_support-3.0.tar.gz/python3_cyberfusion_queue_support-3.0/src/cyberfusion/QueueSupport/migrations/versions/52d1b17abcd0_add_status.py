"""Add status

Revision ID: 52d1b17abcd0
Revises: 8023b9eecdd1
Create Date: 2025-08-28 11:48:46.168058

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "52d1b17abcd0"
down_revision = "8023b9eecdd1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "queue_processes",
        sa.Column(
            "status",
            sa.Enum("SUCCESS", "FATAL", "WARNING", name="queueprocessstatus"),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("queue_processes", "status")
