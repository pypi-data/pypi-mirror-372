"""EveTycoon provider"""

from typing import Iterable

from allianceauth.services.hooks import get_extension_logger

from eveprices.providers import AbstractPriceProvider
from eveprices.providers.base import PriceInformation

from . import requests

logger = get_extension_logger(__name__)

BASE_EVETYCOON_URL = "https://evetycoon.com"


class EvetycoonPriceProvider(AbstractPriceProvider):
    """
    Price provider with the EveTycoon API
    https://evetycoon.com/docs
    """

    def query_types_prices(self, type_ids: Iterable[int]) -> list[PriceInformation]:
        logger.info("EveTycoon provider requesting prices for %s", type_ids)

        return [self.query_type_price(type_id) for type_id in type_ids]

    def query_type_price(self, type_id: int) -> PriceInformation:
        """Query a single type from the API"""
        r = requests.get(
            f"{BASE_EVETYCOON_URL}/api/v1/market/stats/10000002/{type_id}",
        )

        return PriceInformation(
            type_id,
            round(float(r.json()["buyAvgFivePercent"]), 2),
            None,
            round(float(r.json()["sellAvgFivePercent"]), 2),
        )

    @property
    def name(self) -> str:
        return "EveTycoon"
