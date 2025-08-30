"""Fuzzwork provider"""

from typing import Iterable

from allianceauth.services.hooks import get_extension_logger

from ..utils import FuzzworkPriceKind
from . import requests
from .base import AbstractPriceProvider, PriceInformation

logger = get_extension_logger(__name__)

BASE_FUZZWORK_URL = "https://market.fuzzwork.co.uk"


class FuzzworkPriceProvider(AbstractPriceProvider):
    """
    Price provider with the fuzzwork API
    https://market.fuzzwork.co.uk/api/
    """

    def query_types_prices(self, type_ids: Iterable[int]) -> list[PriceInformation]:
        logger.info("Fuzzwork provider requesting prices for %s", type_ids)
        r = requests.get(
            f"{BASE_FUZZWORK_URL}/aggregates/?region=10000002&types={','.join(map(str, type_ids))}",
        )

        price_type_key = self.get_price_type()
        res = []
        for type_id in type_ids:
            # TODO specify the weightedAverage from settings
            res.append(
                PriceInformation(
                    type_id,
                    round(float(r.json()[str(type_id)]["buy"][price_type_key]), 2),
                    None,
                    round(float(r.json()[str(type_id)]["sell"][price_type_key]), 2),
                )
            )

        return res

    def query_type_price(self, type_id: int) -> PriceInformation:
        return self.query_types_prices([type_id])[0]

    def get_price_type(self) -> str:
        """Key associated with the user's desired price kind"""
        match self._provider_config.price_kind:
            case FuzzworkPriceKind.WEIGHTED:
                return "weightedAverage"
            case FuzzworkPriceKind.MEDIAN:
                return "median"
            case FuzzworkPriceKind.PERCENTILE:
                return "percentile"
            case _:
                raise ValueError(
                    f"Unexpected input {self._provider_config.price_kind} when checking Fuzzwork price type"
                )

    @property
    def name(self) -> str:
        return "Fuzzwork"
