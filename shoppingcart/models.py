import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from menu.models import Diet


class DietOrder(models.Model):
    name = models.ForeignKey(Diet, on_delete=models.PROTECT)
    megabytes = models.IntegerField()
    days = models.IntegerField(null=True)
    price = models.FloatField(null=True)
    date_of_start = models.DateField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    day_of_end = models.DateField()

    def whole_price(self, price_per_day):
        self.price =  self.days * price_per_day

    def end_of_the_order(self):
        end = self.date_of_start + datetime.timedelta(days=self.days)
        self.day_of_end = end


    def __str__(self):
        return f"{self.date_of_start}"
