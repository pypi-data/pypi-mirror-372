import responses
from responses import matchers

from django.test.utils import TestCase

from eveprices.models import EvePricesConfiguration, FuzzworkConfiguration
from eveprices.providers import FuzzworkPriceProvider, PriceInformation
from eveprices.providers.requests import get_user_agent
from eveprices.utils import FuzzworkPriceKind


class TestFuzzworkProvider(TestCase):

    @classmethod
    def setUpClass(cls):
        config = EvePricesConfiguration.get_solo()
        config.provider = EvePricesConfiguration.Providers.FUZZWORK
        config.save()

    @classmethod
    def tearDownClass(cls):
        """Ensures that the configuration doesn't stay between tests"""
        EvePricesConfiguration.get_solo().delete()

    def setUp(self):
        responses.get(
            "https://market.fuzzwork.co.uk/aggregates/?region=10000002&types=34,35",
            match=[matchers.header_matcher({"User-Agent": get_user_agent()})],
            json={
                "34": {
                    "buy": {
                        "weightedAverage": "4.02878502065",
                        "max": "5.95",
                        "min": "0.01",
                        "stddev": "1.62036217159",
                        "median": "5.0",
                        "volume": "10024734026.0",
                        "orderCount": "52",
                        "percentile": "5.50168617928",
                    },
                    "sell": {
                        "weightedAverage": "6.60015441538",
                        "max": "2201571.0",
                        "min": "5.01",
                        "stddev": "177420.733866",
                        "median": "6.38",
                        "volume": "25573930856.0",
                        "orderCount": "179",
                        "percentile": "5.92257900667",
                    },
                },
                "35": {
                    "buy": {
                        "weightedAverage": "2.95108749592",
                        "max": "9.32",
                        "min": "0.01",
                        "stddev": "2.33386568045",
                        "median": "8.08",
                        "volume": "3567567586.0",
                        "orderCount": "43",
                        "percentile": "8.93197172057",
                    },
                    "sell": {
                        "weightedAverage": "11.8397717552",
                        "max": "88.97",
                        "min": "8.9",
                        "stddev": "6.28077891535",
                        "median": "10.49",
                        "volume": "13983717157.0",
                        "orderCount": "170",
                        "percentile": "9.30539352676",
                    },
                },
            },
        )

    def tearDown(self):
        """Ensures that the config doesn't stay between tests"""
        FuzzworkConfiguration.get_solo().delete()

    def test_correct_provider(self):
        provider = EvePricesConfiguration.get_provider()
        self.assertTrue(isinstance(provider, FuzzworkPriceProvider))

    @responses.activate
    def test_query_prices(self):
        fuzzwork_config = FuzzworkConfiguration.get_solo()
        self.assertEqual(
            fuzzwork_config.price_kind, FuzzworkPriceKind.WEIGHTED
        )  # Check default
        provider = EvePricesConfiguration.get_provider()

        prices = provider.query_types_prices([34, 35])

        self.assertEqual(len(prices), 2)
        self.assertIn(PriceInformation(34, 4.03, None, 6.60), prices)
        self.assertIn(PriceInformation(35, 2.95, None, 11.84), prices)

    @responses.activate
    def test_median_prices(self):
        fuzzwork_config = FuzzworkConfiguration.get_solo()
        fuzzwork_config.price_kind = FuzzworkPriceKind.MEDIAN
        fuzzwork_config.save()
        provider = EvePricesConfiguration.get_provider()

        prices = provider.query_types_prices([34, 35])

        self.assertEqual(len(prices), 2)
        self.assertIn(PriceInformation(34, 5.0, None, 6.38), prices)
        self.assertIn(PriceInformation(35, 8.08, None, 10.49), prices)

    @responses.activate
    def test_percentile_prices(self):
        fuzzwork_config = FuzzworkConfiguration.get_solo()
        fuzzwork_config.price_kind = FuzzworkPriceKind.PERCENTILE
        fuzzwork_config.save()
        provider = EvePricesConfiguration.get_provider()

        prices = provider.query_types_prices([34, 35])

        self.assertEqual(len(prices), 2)
        self.assertIn(PriceInformation(34, 5.50, None, 5.92), prices)
        self.assertIn(PriceInformation(35, 8.93, None, 9.31), prices)
