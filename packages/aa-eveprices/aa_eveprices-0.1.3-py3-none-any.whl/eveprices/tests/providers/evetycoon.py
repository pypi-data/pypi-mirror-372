import responses
from responses import matchers

from django.test.utils import TestCase

from eveprices.models import EvePricesConfiguration
from eveprices.providers import EvetycoonPriceProvider, PriceInformation
from eveprices.providers.requests import get_user_agent


class TestEvetycoonProvider(TestCase):

    @classmethod
    def setUpClass(cls):
        config = EvePricesConfiguration.get_solo()
        config.provider = EvePricesConfiguration.Providers.EVETYCOON
        config.save()

        cls.provider = EvePricesConfiguration.get_provider()

    def test_correct_provider(self):
        self.assertTrue(isinstance(self.provider, EvetycoonPriceProvider))

    @responses.activate
    def test_query_price(self):
        responses.get(
            "https://evetycoon.com/api/v1/market/stats/10000002/44992",
            match=[matchers.header_matcher({"User-Agent": get_user_agent()})],
            json={
                "buyVolume": 215581,
                "sellVolume": 831898,
                "buyOrders": 203,
                "sellOrders": 451,
                "buyOutliers": 117,
                "sellOutliers": 3,
                "buyThreshold": 248100.0,
                "sellThreshold": 2.592e7,
                "buyAvgFivePercent": 2477927.729845069,
                "sellAvgFivePercent": 2598726.2134294575,
            },
        )

        priceinfo = self.provider.query_types_prices([44992])

        self.assertIn(
            PriceInformation(44992, 2_477_927.73, None, 2_598_726.21), priceinfo
        )
