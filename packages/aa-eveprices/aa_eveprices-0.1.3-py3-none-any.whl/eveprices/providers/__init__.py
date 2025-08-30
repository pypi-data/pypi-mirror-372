from __future__ import annotations

from typing import TYPE_CHECKING

from solo.models import SingletonModel

from ..utils import PriceProviderEnum
from .base import AbstractPriceProvider, PriceInformation  # noqa: F401
from .evetycoon import EvetycoonPriceProvider
from .fuzzwork import FuzzworkPriceProvider
from .janice import JanicePriceProvider

if TYPE_CHECKING:
    from ..models import EvePricesConfiguration


def get_provider(
    app_config: EvePricesConfiguration, provider_config: SingletonModel
) -> AbstractPriceProvider:
    """Return the defined provider"""

    provider = app_config.provider
    match provider:
        case PriceProviderEnum.EVETYCOON.value:
            return EvetycoonPriceProvider(app_config, provider_config)
        case PriceProviderEnum.FUZZWORK.value:
            return FuzzworkPriceProvider(app_config, provider_config)
        case PriceProviderEnum.JANICE.value:
            return JanicePriceProvider(app_config, provider_config)
        case _:
            raise ValueError(f"Unexpected provider code `{provider}`")
