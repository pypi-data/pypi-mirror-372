from unittest.mock import patch

from django.test import TestCase

from eveprices.templatetags.eveprices import (
    get_type_price_immediate,
    get_type_price_immediate_humanize,
)


class TestTemplateTags(TestCase):

    @patch("eveprices.templatetags.eveprices.TypePrice.objects.get_price_immediate")
    def test_simple_immediate_tag(self, get_price_mock):
        get_price_mock.return_value = 12_500_000.0

        res = get_type_price_immediate(123)

        self.assertEqual("12500000.0", res)
        get_price_mock.assert_called_once()

    @patch("eveprices.templatetags.eveprices.TypePrice.objects.get_price_immediate")
    def test_humanize_immediate_tag(self, get_price_mock):
        get_price_mock.return_value = 12_500_000.0

        res = get_type_price_immediate_humanize(123)

        self.assertEqual("12.5m ISK", res)
        get_price_mock.assert_called_once()
