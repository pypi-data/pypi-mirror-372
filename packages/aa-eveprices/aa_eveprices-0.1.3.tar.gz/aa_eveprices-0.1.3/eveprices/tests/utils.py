from typing import Iterable

from eveprices.providers import AbstractPriceProvider, PriceInformation


class MockPriceProvider(AbstractPriceProvider):
    """Mock provider to be used in tests"""

    def __init__(self):
        super().__init__(None, None)

    @property
    def name(self) -> str:
        return "Mock Provider"

    def query_types_prices(self, type_ids: Iterable[int]) -> list[PriceInformation]:
        return [self.query_type_price(type_id) for type_id in type_ids]

    def query_type_price(self, type_id: int) -> PriceInformation:
        return PriceInformation(type_id, 100 + type_id, 200 + type_id, 300 + type_id)
