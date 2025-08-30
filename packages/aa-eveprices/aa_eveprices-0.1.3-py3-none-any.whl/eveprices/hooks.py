"""Hook definition"""

from dataclasses import dataclass
from typing import Iterable

from allianceauth.hooks import get_hooks
from allianceauth.services.hooks import get_extension_logger

logger = get_extension_logger(__name__)


@dataclass
class PricesToPreloadListHook:
    """
    A hook for your application to declare the type ids you will be working with.
    The price of these type ids will be updated automatically at regular intervals.
    """

    type_ids: Iterable[int]


def get_type_ids_to_preload_set() -> set[int]:
    """
    Loads all known hooks and return a single set with all the type ids mentioned in these hooks
    """

    ids = set()

    hooks: list[PricesToPreloadListHook] = [
        fn() for fn in get_hooks("price_preload_hook")
    ]

    for hook in hooks:
        logger.debug(hook)

        ids |= set(hook.type_ids)

    return ids
