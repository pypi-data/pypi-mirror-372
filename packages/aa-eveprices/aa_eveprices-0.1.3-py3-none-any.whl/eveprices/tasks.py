"""Tasks."""

from celery import shared_task

from allianceauth.services.hooks import get_extension_logger

from eveprices.hooks import get_type_ids_to_preload_set
from eveprices.models import EvePricesConfiguration, TypePrice

logger = get_extension_logger(__name__)


@shared_task
def update_prices():
    """
    Will query all ids defined in `PricesToPreloadListHook` and update the price for these specific ids.
    """
    logger.info("Updating price information from hooks")
    price_provider = EvePricesConfiguration.get_provider()

    type_ids = get_type_ids_to_preload_set()
    logger.debug(type_ids)

    price_information = price_provider.query_types_prices(type_ids)
    logger.debug(price_information)

    TypePrice.objects.bulk_update_from_price_info(price_information)
