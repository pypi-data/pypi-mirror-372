"""Utility stuffs"""

from enum import Enum

from django.db import models
from django.utils.translation import gettext_lazy as _


class JanicePriceKind(models.TextChoices):
    """Different price choices that can be used in Janice"""

    IMMEDIATE = "IM", _("Immediate")
    MEDIAN_5_DAYS = "5D", _("5 days median")
    MEDIAN_30_DAYS = "30D", _("30 days median")


class FuzzworkPriceKind(models.TextChoices):
    """Different price choices that can be used"""

    WEIGHTED = "WA", _("Weighted Average")
    MEDIAN = "ME", _("Median")
    PERCENTILE = "PE", _("Percentile")


class PriceProviderEnum(Enum):
    """Different price providers defined in the application"""

    EVETYCOON = "ET"
    FUZZWORK = "FW"
    JANICE = "JA"


class PriceKindEnum(models.TextChoices):
    """Default price to be used"""

    BUY = "BU", _("Buy price")
    SPLIT = "SP", _("Split price")
    SELL = "SE", _("Sell price")
