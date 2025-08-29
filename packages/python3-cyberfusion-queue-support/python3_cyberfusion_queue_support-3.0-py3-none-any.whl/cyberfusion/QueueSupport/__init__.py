"""Classes for queue."""

import logging
from dataclasses import dataclass
from typing import List
import traceback

from cyberfusion.QueueSupport.database import (
    Queue as QueueModel,
    QueueItem,
    make_database_session,
    QueueItemOutcome,
    QueueProcess,
)
from cyberfusion.QueueSupport.enums import QueueProcessStatus

from cyberfusion.QueueSupport.interfaces import OutcomeInterface
from cyberfusion.QueueSupport.items import _Item

logger = logging.getLogger(__name__)


@dataclass
class QueueItemMapping:
    """Queue item mapping."""

    item: _Item
    database_object: QueueItem


class Queue:
    """Represents queue."""

    def __init__(self) -> None:
        """Set attributes."""
        self.item_mappings: List[QueueItemMapping] = []

        self._database_session = make_database_session()

        object_ = QueueModel()

        self._database_session.add(object_)
        self._database_session.commit()

        self.queue_database_object = object_

    def add(self, item: _Item, *, run_duplicate_last: bool = True) -> None:
        """Add item to queue."""
        deduplicated = False

        existing_items_indexes = [
            index
            for index, item_mapping in enumerate(self.item_mappings)
            if item_mapping.item == item
        ]

        if existing_items_indexes:
            if run_duplicate_last:
                for existing_item_index in existing_items_indexes:
                    self.item_mappings[
                        existing_item_index
                    ].database_object.deduplicated = True
            else:
                deduplicated = True

        object_ = QueueItem(
            queue=self.queue_database_object,
            type=item.__class__.__name__,
            reference=item.reference,
            hide_outcomes=item.hide_outcomes,
            fail_silently=item.fail_silently,
            deduplicated=deduplicated,
            attributes=item,
            traceback=None,
        )

        self._database_session.add(object_)

        self.item_mappings.append(QueueItemMapping(item, object_))

    def process(self, preview: bool) -> tuple[QueueProcess, list[OutcomeInterface]]:
        """Process items."""
        logger.debug("Processing items")

        process_object = QueueProcess(
            queue_id=self.queue_database_object.id, preview=preview, status=None
        )

        self._database_session.add(process_object)

        outcomes = []

        for item_mapping in [
            item_mapping
            for item_mapping in self.item_mappings
            if not item_mapping.database_object.deduplicated
        ]:
            logger.debug(
                "Processing item with ID '%s'", item_mapping.database_object.id
            )

            item_outcomes = []

            if preview:
                if not item_mapping.item.hide_outcomes:
                    item_outcomes.extend(item_mapping.item.outcomes)
            else:
                try:
                    logger.debug(
                        "Fulfilling item with ID '%s'", item_mapping.database_object.id
                    )

                    if item_mapping.item.hide_outcomes:
                        item_mapping.item.fulfill()
                    else:
                        item_outcomes.extend(item_mapping.item.fulfill())

                    logger.debug(
                        "Fulfilled item with ID '%s'", item_mapping.database_object.id
                    )
                except Exception as e:
                    logger.exception(e)

                    item_mapping.database_object.traceback = traceback.format_exc()

                    self._database_session.add(item_mapping.database_object)

                    if item_mapping.database_object.fail_silently:
                        process_object.status = QueueProcessStatus.WARNING
                    else:
                        process_object.status = QueueProcessStatus.FATAL

                        break

            outcomes.extend(item_outcomes)

            for outcome in item_outcomes:
                self._database_session.add(
                    QueueItemOutcome(
                        queue_item=item_mapping.database_object,
                        queue_process=process_object,
                        type=outcome.__class__.__name__,
                        attributes=outcome,
                        string=str(outcome),
                    )
                )

            logger.debug("Processed item with ID '%s'", item_mapping.database_object.id)

        logger.debug("Processed items")

        if not process_object.status:
            process_object.status = QueueProcessStatus.SUCCESS

        self._database_session.add(process_object)

        self._database_session.commit()

        return process_object, outcomes
