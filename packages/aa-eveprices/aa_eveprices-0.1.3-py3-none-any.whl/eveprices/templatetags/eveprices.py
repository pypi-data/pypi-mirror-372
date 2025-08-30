"""
Eveprices template tags
"""

from django import template

from eveprices.models import TypePrice

register = template.Library()


@register.simple_tag
def get_type_price_immediate(type_id: int) -> str:
    """
    Returns the immediate type price for display

    Price are the raw value without any formatting
    """
    return str(TypePrice.objects.get_price_immediate(type_id))


@register.simple_tag
def get_type_price_immediate_humanize(type_id: int) -> str:
    """
    Returns the immediate type price humanized

    ex: "12.5b ISK", "8.2m ISK", ...
    """
    value = TypePrice.objects.get_price_immediate(type_id)
    power_map = {"t": 12, "b": 9, "m": 6, "k": 3, "": 0}
    if value >= 10**12:
        magnitude = "t"
    elif value >= 10**9:
        magnitude = "b"
    elif value >= 10**6:
        magnitude = "m"
    elif value >= 10**3:
        magnitude = "k"
    else:
        magnitude = ""
    result = f"{value / 10 ** power_map[magnitude]:,.1f}{magnitude} ISK"
    return result
