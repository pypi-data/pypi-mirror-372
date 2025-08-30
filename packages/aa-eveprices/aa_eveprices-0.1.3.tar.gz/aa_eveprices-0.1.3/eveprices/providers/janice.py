"""Janice price provider"""

from typing import Iterable

from allianceauth.services.hooks import get_extension_logger

from eveprices.providers import AbstractPriceProvider
from eveprices.providers.base import PriceInformation
from eveprices.utils import JanicePriceKind

from . import requests

logger = get_extension_logger(__name__)

BASE_JANICE_URL = "https://janice.e-351.com"


class MissingApiKey(Exception):
    """Raised when a call is attempted without an API key entered"""


class JanicePriceProvider(AbstractPriceProvider):
    """
    Price provider for the Janice API
    https://janice.e-351.com/api/rest/docs/index.html
    """

    def query_types_prices(self, type_ids: Iterable[int]) -> list[PriceInformation]:
        logger.info("Janice provider requesting prices for %s", type_ids)

        if not type_ids:
            return []

        r = requests.post(
            f"{BASE_JANICE_URL}/api/rest/v2/pricer",
            headers={
                "X-ApiKey": self.get_api_key(),
            },
            data="\n".join(map(str, type_ids)),
        )

        price_key_extra = self.get_price_type_key()
        res = []
        for type_info in r.json():
            res.append(
                PriceInformation(
                    type_info["itemType"]["eid"],
                    round(
                        type_info["immediatePrices"][f"buyPrice{price_key_extra}"], 2
                    ),
                    round(
                        type_info["immediatePrices"][f"splitPrice{price_key_extra}"], 2
                    ),
                    round(
                        type_info["immediatePrices"][f"sellPrice{price_key_extra}"], 2
                    ),
                )
            )

        return res

    def query_type_price(self, type_id: int) -> PriceInformation:
        return self.query_types_prices([type_id])[0]

    def get_price_type_key(self) -> str:
        """Key associated wit the user's desired price kind"""
        match self._provider_config.price_kind:
            case JanicePriceKind.IMMEDIATE.value:
                return ""
            case JanicePriceKind.MEDIAN_5_DAYS.value:
                return "5DayMedian"
            case JanicePriceKind.MEDIAN_30_DAYS.value:
                return "30DayMedian"
            case _:
                raise ValueError(
                    f"Unexpected input {self._provider_config.price_kind} when checking Janice price type"
                )

    def get_api_key(self) -> str:
        """Recover the provider's api key"""
        api_key = self._provider_config.api_key
        if not api_key:
            raise MissingApiKey("No API key for Janice found")
        return api_key

    @property
    def name(self) -> str:
        return "Janice"
