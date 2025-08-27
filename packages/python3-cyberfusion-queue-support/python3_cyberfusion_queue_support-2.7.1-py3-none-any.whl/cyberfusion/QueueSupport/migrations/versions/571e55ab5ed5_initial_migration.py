"""Initial migration

Revision ID: 571e55ab5ed5
Revises:
Create Date: 2025-04-09 18:46:38.122919

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "571e55ab5ed5"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "queues",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_queues")),
    )

    op.create_table(
        "queue_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("queue_id", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(length=255), nullable=False),
        sa.Column("reference", sa.String(length=255), nullable=True),
        sa.Column("hide_outcomes", sa.Boolean(), nullable=False),
        sa.Column("deduplicated", sa.Boolean(), nullable=False),
        sa.Column("attributes", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(
            ["queue_id"], ["queues.id"], name=op.f("fk_queue_items_queue_id_queues")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_queue_items")),
    )

    op.create_table(
        "queue_processes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("queue_id", sa.Integer(), nullable=False),
        sa.Column("preview", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["queue_id"], ["queues.id"], name=op.f("fk_queue_processes_queue_id_queues")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_queue_processes")),
    )

    op.create_table(
        "queue_item_outcomes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("queue_item_id", sa.Integer(), nullable=False),
        sa.Column("queue_process_id", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(length=255), nullable=False),
        sa.Column("attributes", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(
            ["queue_item_id"],
            ["queue_items.id"],
            name=op.f("fk_queue_item_outcomes_queue_item_id_queue_items"),
        ),
        sa.ForeignKeyConstraint(
            ["queue_process_id"],
            ["queue_processes.id"],
            name=op.f("fk_queue_item_outcomes_queue_process_id_queue_processes"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_queue_item_outcomes")),
    )


def downgrade() -> None:
    op.drop_table("queue_item_outcomes")
    op.drop_table("queue_processes")
    op.drop_table("queue_items")
    op.drop_table("queues")
