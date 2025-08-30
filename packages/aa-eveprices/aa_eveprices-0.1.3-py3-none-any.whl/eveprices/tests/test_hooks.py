from django.test import TestCase

from allianceauth import hooks

from eveprices.hooks import PricesToPreloadListHook, get_type_ids_to_preload_set


@hooks.register("price_preload_hook")
def register_price_preload_list_1():
    return PricesToPreloadListHook([35, 36])


@hooks.register("price_preload_hook")
def register_price_preload_list_2():
    return PricesToPreloadListHook({36, 37})


class TestHook(TestCase):

    def test_get_hooks(self):
        ids = get_type_ids_to_preload_set()

        self.assertEqual(len(ids), 3)
        self.assertIn(35, ids)
        self.assertIn(36, ids)
        self.assertIn(37, ids)
