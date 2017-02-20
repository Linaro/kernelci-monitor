import logging

from django.core.management.base import BaseCommand
from monitor.tasks import monitor_boots
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, **kwargs):
        # create a celery task immediately
        logging.info("Starting monitor_boots task")
        monitor_boots.delay()
