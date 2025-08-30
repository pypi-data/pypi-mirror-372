from django.test.utils import TestCase

from eveprices.providers import PriceInformation


class TestPriceInformation(TestCase):

    def test_split_is_none(self):
        price_info = PriceInformation(1, 2, None, 4)

        self.assertEqual(3, price_info.split_price)
