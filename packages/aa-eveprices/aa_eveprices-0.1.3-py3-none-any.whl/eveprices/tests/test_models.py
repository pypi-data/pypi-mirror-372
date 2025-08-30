from unittest.mock import patch

from django.test.utils import TestCase

from eveprices.models import EvePricesConfiguration, TypePrice
from eveprices.providers import PriceInformation
from eveprices.tests.utils import MockPriceProvider
from eveprices.utils import PriceKindEnum


class TestTypePrice(TestCase):

    def test_bulk_update_on_no_db(self):
        """Checks how bulk update reacts to unknown objects"""
        price_information_list = [
            PriceInformation(0, 10, 20, 30),
            PriceInformation(1, 10, 20, 30),
        ]

        TypePrice.objects.bulk_update_from_price_info(price_information_list)

        self.assertEqual(TypePrice.objects.count(), 2)

    # TODO check why the DB isn't cleared between tests
    @patch.object(EvePricesConfiguration, "get_provider")
    def test_immediate_query_no_item(self, mock_get_provider):
        """Queries an item with the immediate when the item isn't in the database"""
        mock_get_provider.return_value = MockPriceProvider()
        sell_price = TypePrice.objects.get_price_immediate(2, PriceKindEnum.SELL)

        self.assertEqual(sell_price, 302.0)
        mock_get_provider.assert_called_once()
