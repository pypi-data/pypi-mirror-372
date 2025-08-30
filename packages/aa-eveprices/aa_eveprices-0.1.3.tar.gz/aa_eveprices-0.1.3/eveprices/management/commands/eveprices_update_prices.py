from django.core.management.base import BaseCommand

from allianceauth.services.hooks import get_extension_logger

from eveprices.tasks import update_prices

logger = get_extension_logger(__name__)


class Command(BaseCommand):
    help = "Update all eveprices"

    def handle(self, *args, **options):
        logger.info("Starting price update from management command")
        update_prices.delay()
