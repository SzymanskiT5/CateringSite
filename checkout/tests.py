from unittest import TestCase

from checkout.models import DietOrder
from menu.models import Diet


class DietOrderCase(TestCase):

    def setUp(self) -> None:
        diet = Diet.objects.get(name="Tester Diet")
        DietOrder.objects.create(name=diet,
                                 megabytes=1000,
                                 commit= False)

    def tearDown(self) -> None:
        DietOrder.objects.filter(email="testuser@gmail.com").delete()
