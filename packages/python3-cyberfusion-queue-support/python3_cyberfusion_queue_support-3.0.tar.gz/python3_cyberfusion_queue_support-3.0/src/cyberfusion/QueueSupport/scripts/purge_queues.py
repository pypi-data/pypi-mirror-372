import datetime

from cyberfusion.QueueSupport.database import make_database_session, Queue
from cyberfusion.QueueSupport.settings import settings


def main() -> None:
    database_session = make_database_session()

    purge_before_date = datetime.datetime.now() - datetime.timedelta(
        days=settings.queue_purge_days
    )

    queues = (
        database_session.query(Queue).filter(Queue.created_at < purge_before_date).all()
    )

    for queue in queues:
        database_session.delete(queue)

    database_session.commit()
