"""Base utils for price providers"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass
from typing import TYPE_CHECKING

from solo.models import SingletonModel

if TYPE_CHECKING:
    from eveprices.models import EvePricesConfiguration


@dataclass
class PriceInformation:
    """Returned price from a provider"""

    type_id: int

    buy_price: float
    split_price: float | None
    sell_price: float

    def __getattribute__(self, item):
        if item == "split_price" and not super().__getattribute__(item):
            return (self.buy_price + self.sell_price) / 2
        return super().__getattribute__(item)


class AbstractPriceProvider(ABC):
    """Abstract class that will contain the common logic to update price"""

    def __init__(
        self, app_config: EvePricesConfiguration, provider_config: SingletonModel
    ):
        self._app_config = app_config
        self._provider_config = provider_config

    @property
    @abstractmethod
    def name(self) -> str:
        """Returns the name of the provider"""

    @abstractmethod
    def query_types_prices(self, type_ids: Iterable[int]) -> list[PriceInformation]:
        """Query the price of a set of type ides from the provider"""

    @abstractmethod
    def query_type_price(self, type_id: int) -> PriceInformation:
        """Query the price of a single type id from the provider"""
