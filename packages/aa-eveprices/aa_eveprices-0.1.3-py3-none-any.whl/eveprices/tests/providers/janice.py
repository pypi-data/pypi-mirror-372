import responses
from responses import matchers

from django.test.utils import TestCase

from eveprices.models import EvePricesConfiguration, JaniceConfiguration
from eveprices.providers import JanicePriceProvider, PriceInformation
from eveprices.providers.janice import MissingApiKey
from eveprices.providers.requests import get_user_agent
from eveprices.utils import JanicePriceKind


class TestJanicePriceProvider(TestCase):

    @classmethod
    def setUpClass(cls):
        config = EvePricesConfiguration.get_solo()
        config.provider = EvePricesConfiguration.Providers.JANICE
        config.save()

    @classmethod
    def tearDownClass(cls):
        """Deletes remaining config"""
        EvePricesConfiguration.get_solo().delete()

    def setUp(self):
        responses.post(
            "https://janice.e-351.com/api/rest/v2/pricer",
            match=[
                matchers.body_matcher("34\n35"),
                matchers.header_matcher(
                    {"X-ApiKey": "bad api key", "User-Agent": get_user_agent()}
                ),
            ],
            json=[
                {
                    "date": "2025-08-08T00:00:00Z",
                    "market": {"id": 2, "name": "Jita 4-4"},
                    "buyOrderCount": 44,
                    "buyVolume": 15630062172,
                    "sellOrderCount": 113,
                    "sellVolume": 21277134995,
                    "immediatePrices": {
                        "buyPrice": 3.78,
                        "splitPrice": 3.86,
                        "sellPrice": 3.94,
                        "buyPrice5DayMedian": 3.75,
                        "splitPrice5DayMedian": 3.81,
                        "sellPrice5DayMedian": 3.9,
                        "buyPrice30DayMedian": 3.8093333333333335,
                        "splitPrice30DayMedian": 3.86,
                        "sellPrice30DayMedian": 3.91,
                    },
                    "top5AveragePrices": {
                        "buyPrice": 3.6878518374363267,
                        "splitPrice": 3.8182079121390653,
                        "sellPrice": 3.948563986841804,
                        "buyPrice5DayMedian": 3.6878518374363267,
                        "splitPrice5DayMedian": 3.813676156365989,
                        "sellPrice5DayMedian": 3.9240064180367535,
                        "buyPrice30DayMedian": 3.7832391820754268,
                        "splitPrice30DayMedian": 3.865428197010191,
                        "sellPrice30DayMedian": 3.948755934636251,
                    },
                    "itemType": {
                        "eid": 34,
                        "name": "Tritanium",
                        "volume": 0.01,
                        "packagedVolume": 0.01,
                    },
                },
                {
                    "date": "2025-08-08T00:00:00Z",
                    "market": {"id": 2, "name": "Jita 4-4"},
                    "buyOrderCount": 43,
                    "buyVolume": 3049453577,
                    "sellOrderCount": 98,
                    "sellVolume": 1814598488,
                    "immediatePrices": {
                        "buyPrice": 26.82,
                        "splitPrice": 28.355,
                        "sellPrice": 29.89,
                        "buyPrice5DayMedian": 28.238,
                        "splitPrice5DayMedian": 29.55,
                        "sellPrice5DayMedian": 30.48,
                        "buyPrice30DayMedian": 29.172666666666665,
                        "splitPrice30DayMedian": 29.735,
                        "sellPrice30DayMedian": 30.58,
                    },
                    "top5AveragePrices": {
                        "buyPrice": 26.82,
                        "splitPrice": 28.35933027387965,
                        "sellPrice": 29.898660547759302,
                        "buyPrice5DayMedian": 28.51691708868854,
                        "splitPrice5DayMedian": 29.55588007863716,
                        "sellPrice5DayMedian": 30.486093901199027,
                        "buyPrice30DayMedian": 29.166597699704756,
                        "splitPrice30DayMedian": 29.71190994046051,
                        "sellPrice30DayMedian": 30.720739264318212,
                    },
                    "itemType": {
                        "eid": 35,
                        "name": "Pyerite",
                        "volume": 0.01,
                        "packagedVolume": 0.01,
                    },
                },
            ],
        )

        janice_config = JaniceConfiguration.get_solo()
        janice_config.api_key = "bad api key"
        janice_config.save()

    def tearDown(self):
        """Delete remaining Janice config"""
        JaniceConfiguration.get_solo().delete()

    def test_correct_provider(self):
        provider = EvePricesConfiguration.get_provider()
        self.assertTrue(isinstance(provider, JanicePriceProvider))

    @responses.activate
    def test_query_prices(self):
        provider = EvePricesConfiguration.get_provider()
        priceinfo = provider.query_types_prices([34, 35])

        self.assertIn(PriceInformation(34, 3.78, 3.86, 3.94), priceinfo)
        self.assertIn(PriceInformation(35, 26.82, 28.36, 29.89), priceinfo)

    @responses.activate
    def test_5d_median(self):
        janice_config = JaniceConfiguration.get_solo()
        janice_config.price_kind = JanicePriceKind.MEDIAN_5_DAYS
        janice_config.save()

        provider = EvePricesConfiguration.get_provider()

        priceinfo = provider.query_types_prices([34, 35])

        self.assertIn(PriceInformation(34, 3.75, 3.81, 3.9), priceinfo)
        self.assertIn(PriceInformation(35, 28.24, 29.55, 30.48), priceinfo)

    @responses.activate
    def test_30d_median(self):
        janice_config = JaniceConfiguration.get_solo()
        janice_config.price_kind = JanicePriceKind.MEDIAN_30_DAYS
        janice_config.save()
        provider = EvePricesConfiguration.get_provider()

        priceinfo = provider.query_types_prices([34, 35])

        self.assertIn(PriceInformation(34, 3.81, 3.86, 3.91), priceinfo)
        self.assertIn(PriceInformation(35, 29.17, round(29.735, 2), 30.58), priceinfo)

    def test_no_api(self):
        JaniceConfiguration.get_solo().delete()

        provider = EvePricesConfiguration.get_provider()
        self.assertRaises(MissingApiKey, provider.query_types_prices, [34, 34])

    @responses.activate
    def test_empty_body(self):
        responses.post(
            "https://janice.e-351.com/api/rest/v2/pricer",
            match=[
                matchers.header_matcher(
                    {"X-ApiKey": "bad api key", "User-Agent": get_user_agent()}
                ),
            ],
            status=400,
        )

        provider = EvePricesConfiguration.get_provider()

        provider.query_types_prices(set())
