"""Set status on existing queue processes

Revision ID: 8406a0af7394
Revises: 52d1b17abcd0
Create Date: 2025-08-28 11:56:22.861704

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "8406a0af7394"
down_revision = "52d1b17abcd0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE queue_processes SET status = 'SUCCESS'")


def downgrade() -> None:
    pass
