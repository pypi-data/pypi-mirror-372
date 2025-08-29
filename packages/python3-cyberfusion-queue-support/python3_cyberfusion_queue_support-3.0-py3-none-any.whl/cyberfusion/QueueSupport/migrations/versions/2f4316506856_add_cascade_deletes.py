"""Add cascade deletes

Revision ID: 2f4316506856
Revises: 03d4e411c575
Create Date: 2025-08-28 16:31:42.976092

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "2f4316506856"
down_revision = "03d4e411c575"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("queue_item_outcomes", schema=None) as batch_op:
        batch_op.drop_constraint(
            "fk_queue_item_outcomes_queue_process_id_queue_processes",
            type_="foreignkey",
        )
        batch_op.drop_constraint(
            "fk_queue_item_outcomes_queue_item_id_queue_items", type_="foreignkey"
        )
        batch_op.create_foreign_key(
            batch_op.f("fk_queue_item_outcomes_queue_item_id_queue_items"),
            "queue_items",
            ["queue_item_id"],
            ["id"],
            ondelete="CASCADE",
        )
        batch_op.create_foreign_key(
            batch_op.f("fk_queue_item_outcomes_queue_process_id_queue_processes"),
            "queue_processes",
            ["queue_process_id"],
            ["id"],
            ondelete="CASCADE",
        )

    with op.batch_alter_table("queue_items", schema=None) as batch_op:
        batch_op.drop_constraint("fk_queue_items_queue_id_queues", type_="foreignkey")
        batch_op.create_foreign_key(
            batch_op.f("fk_queue_items_queue_id_queues"),
            "queues",
            ["queue_id"],
            ["id"],
            ondelete="CASCADE",
        )

    with op.batch_alter_table("queue_processes", schema=None) as batch_op:
        batch_op.drop_constraint(
            "fk_queue_processes_queue_id_queues", type_="foreignkey"
        )
        batch_op.create_foreign_key(
            batch_op.f("fk_queue_processes_queue_id_queues"),
            "queues",
            ["queue_id"],
            ["id"],
            ondelete="CASCADE",
        )


def downgrade() -> None:
    pass
