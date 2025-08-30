"""Models."""

from __future__ import annotations

from datetime import timedelta

from solo.models import SingletonModel

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from eveprices.utils import FuzzworkPriceKind, JanicePriceKind, PriceKindEnum

from . import providers
from .providers import PriceInformation


class EvePricesConfiguration(SingletonModel):
    """Base configuration for AA-Eveprice"""

    class Providers(models.TextChoices):
        """Possible providers"""

        EVETYCOON = "ET", "EveTycoon"
        FUZZWORK = "FW", "Fuzzwork"
        JANICE = "JA", "Janice"

    provider = models.CharField(
        max_length=2,
        choices=Providers.choices,
        default=Providers.FUZZWORK,
        help_text=_("Provider to be used to source pricing data"),
    )

    price_kind = models.CharField(
        max_length=2,
        choices=PriceKindEnum.choices,
        default=PriceKindEnum.SELL,
        help_text=_("Use buy or sell prices as a default"),
    )

    def __str__(self):
        return "Eve price base configuration"

    @classmethod
    def _get_provider_config(cls) -> SingletonModel:
        """Return the chosen provider config"""
        match cls.get_solo().provider:
            case cls.Providers.EVETYCOON:
                return EveTycoonConfiguration.get_solo()
            case cls.Providers.FUZZWORK:
                return FuzzworkConfiguration.get_solo()
            case cls.Providers.JANICE:
                return JaniceConfiguration.get_solo()
            case _:
                raise TypeError("Unexpected provider code provided")

    @classmethod
    def get_provider(cls) -> providers.AbstractPriceProvider:
        """Get the defined price provider"""
        return providers.get_provider(cls.get_solo(), cls._get_provider_config())

    @classmethod
    def get_price_kind(cls) -> PriceKindEnum:
        """Get the defined price kind"""
        return cls.get_solo().price_kind


class EveTycoonConfiguration(SingletonModel):
    """EveTycoon config"""


class FuzzworkConfiguration(SingletonModel):
    """Fuzzwork config"""

    price_kind = models.CharField(
        max_length=2,
        choices=FuzzworkPriceKind.choices,
        default=FuzzworkPriceKind.WEIGHTED,
        help_text=_(
            "Which price kind returned by Fuzzwork to use.\nSee: https://market.fuzzwork.co.uk/api/"
        ),
    )


class JaniceConfiguration(SingletonModel):
    """Janice config"""

    api_key = models.CharField(
        max_length=128,
        null=True,
        blank=True,
        help_text=_("API key provided by the Janice admin"),
    )

    price_kind = models.CharField(
        max_length=3,
        choices=JanicePriceKind.choices,
        default=JanicePriceKind.IMMEDIATE,
        help_text=_(
            "Which price kind returned by Janice to use.\nSee: https://janice.e-351.com/api/rest/docs/index.html"
        ),
    )


class TypePriceManager(models.Manager):
    """Manager for the TypePrice class"""

    def get_type_price_immediate(self, type_id: int) -> TypePrice:
        """Return  the TypePrice from database without checking timestamp"""
        try:
            type_price = self.get(type_id=type_id)
        except self.model.DoesNotExist:
            price_info = self._fetch_price_from_provider(type_id)
            type_price, _ = self.update_or_create_from_price_info(price_info)

        return type_price

    def get_price_immediate(
        self, type_id: int, price_kind: PriceKindEnum | None = None
    ) -> float:
        """
        Get the price of an item from the db.
        Only contacts a provider if the price isn't in the database.

        This method is the preferred method for ids that are part of your application known types.
        """
        if not price_kind:
            price_kind = EvePricesConfiguration.get_price_kind()

        type_price = self.get_type_price_immediate(type_id)

        return type_price.get_price_by_kind(price_kind)

    def get_or_update_type_price(
        self, type_id: int, max_hours: int = 24
    ) -> tuple[TypePrice, bool]:
        """
        Return the TypePrice for the given type_id.
        If the TypePrice hasn't been updated in at least `max_hours` it will be updated before returning
        Bool value in the return is set to true if an update was triggered
        """
        type_price = self.get_type_price_immediate(type_id)
        now = timezone.now()
        updated = False

        if type_price.timestamp + timedelta(hours=max_hours) < now:
            type_price = self._fetch_price_from_provider(type_id)
            updated = True

        return type_price, updated

    def get_or_update_price(
        self, type_id: int, price_kind: PriceKindEnum | None = None, max_hours: int = 24
    ) -> tuple[float, bool]:
        """
        Return the price of a given type.
        If the type price hasn't been updated in at least `max_hours` it will be updated before returning
        """
        if not price_kind:
            price_kind = EvePricesConfiguration.get_price_kind()

        type_price, updated = self.get_or_update_type_price(type_id, max_hours)

        return type_price.get_price_by_kind(price_kind), updated

    def _fetch_price_from_provider(self, type_id: int) -> PriceInformation:
        """Fetch the price information of a single type from the provider"""
        provider = EvePricesConfiguration.get_provider()
        return provider.query_type_price(type_id)

    def update_or_create_from_price_info(self, price_info: providers.PriceInformation):
        """Update a TypePrice with the given type information"""
        return self.update_or_create(
            buy_price=price_info.buy_price,
            split_price=price_info.split_price,
            sell_price=price_info.sell_price,
            defaults={"type_id": price_info.type_id},
        )

    def bulk_update_from_price_info(
        self, price_info_list: list[providers.PriceInformation]
    ):
        """
        Bulk update prices from the given price information list
        """

        # Creates missing objects
        for price_info in price_info_list:
            if not TypePrice.objects.filter(type_id=price_info.type_id).exists():
                TypePrice.objects.create(
                    type_id=price_info.type_id,
                    buy_price=price_info.buy_price,
                    split_price=price_info.split_price,
                    sell_price=price_info.sell_price,
                )

        # Updates all objects
        TypePrice.objects.bulk_update(
            [
                TypePrice(
                    type_id=price_info.type_id,
                    buy_price=price_info.buy_price,
                    split_price=price_info.split_price,
                    sell_price=price_info.sell_price,
                )
                for price_info in price_info_list
            ],
            ["buy_price", "split_price", "sell_price"],
        )


class TypePrice(models.Model):
    """
    Last known price of an eve model
    """

    objects = TypePriceManager()

    type_id = models.BigIntegerField(
        primary_key=True, help_text=_("ID of the eve type")
    )

    buy_price = models.FloatField()
    split_price = models.FloatField()
    sell_price = models.FloatField()

    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (
            f"Price of type {self.type_id} at {self.timestamp}"
            f"({self.buy_price}/{self.split_price}/{self.sell_price})"
        )

    def get_price_by_kind(self, price_kind: PriceKindEnum) -> float:
        """Get the price associated to the correct kind"""
        match price_kind:
            case PriceKindEnum.BUY:
                return self.buy_price
            case PriceKindEnum.SPLIT:
                return self.split_price
            case PriceKindEnum.SELL:
                return self.sell_price
