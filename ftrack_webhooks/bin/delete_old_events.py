from ftrack_webhooks.services.events import EventService
from ftrack_webhooks.app import create_app
from logging import getLogger

logger = getLogger(__name__)

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        logger.info("purging old event logs.")
        EventService().delete_old_events()
        logger.info("purged old event logs.")
