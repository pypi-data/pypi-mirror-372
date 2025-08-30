"""Admin site."""

from solo.admin import SingletonModelAdmin

from django.contrib import admin

from allianceauth.services.hooks import get_extension_logger

from eveprices.models import (
    EvePricesConfiguration,
    EveTycoonConfiguration,
    FuzzworkConfiguration,
    JaniceConfiguration,
    TypePrice,
)


class EveTycoonModelAdmin(SingletonModelAdmin):
    def get_model_perms(self, request):
        if not EvePricesConfiguration.get_solo().provider == "ET":
            return {"view": False}
        return super().get_model_perms(request)


class FuzzworkModelAdmin(SingletonModelAdmin):
    def get_model_perms(self, request):
        if not EvePricesConfiguration.get_solo().provider == "FW":
            return {"view": False}
        return super().get_model_perms(request)


class JaniceModelAdmin(SingletonModelAdmin):
    def get_model_perms(self, request):
        if not EvePricesConfiguration.get_solo().provider == "JA":
            return {"view": False}
        return super().get_model_perms(request)


# Register your models for the admin site here.

logger = get_extension_logger(__name__)

admin.site.register(EvePricesConfiguration, SingletonModelAdmin)

admin.site.register(EveTycoonConfiguration, EveTycoonModelAdmin)
admin.site.register(FuzzworkConfiguration, FuzzworkModelAdmin)
admin.site.register(JaniceConfiguration, JaniceModelAdmin)


@admin.register(TypePrice)
class TypePriceAdmin(admin.ModelAdmin):
    list_display = ["type_id", "buy_price", "split_price", "sell_price", "timestamp"]

    def has_add_permission(self, request):
        return False
