import datetime

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
from menu.models import Diet
from checkout.exceptions import OrderDateInPast, OrderDateNotMinimumThreeDays, TooLongDistance


class DietOrder(models.Model):
    name = models.ForeignKey(Diet, on_delete=models.PROTECT)
    megabytes = models.IntegerField()
    days = models.IntegerField()
    to_pay = models.FloatField(null=True)
    delivery_cost = models.FloatField(null=True)
    diet_cost = models.FloatField(null=True)
    delivery_cost_per_day = models.FloatField(null=True)
    diet_cost_per_day = models.FloatField()
    date_of_start = models.DateTimeField(default = timezone.now)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    date_of_end = models.DateTimeField(null=True)
    address = models.TextField()
    address_info = models.TextField()
    locality = models.TextField()
    state = models.TextField()
    post_code = models.TextField()
    distance = models.FloatField()
    is_finished = models.BooleanField(default=False)


    def calculate_whole_price(self):
        self.to_pay = self.diet_cost + self.delivery_cost

    def calculate_diet_cost(self):
        self.diet_cost = self.days * self.diet_cost_per_day

    def calculate_delivery_cost(self):
        self.delivery_cost = self.delivery_cost_per_day * self.days

    def end_of_the_order(self):
        end = self.date_of_start + datetime.timedelta(days=self.days)
        self.date_of_end = end

    def check_if_date_is_past(self):
        if self.date_of_start < timezone.now():
            raise OrderDateInPast

    def check_if_date_is_three_days_ahead(self):
        if self.date_of_start - timezone.now() <= datetime.timedelta(days=3):
            raise OrderDateNotMinimumThreeDays

    def calculate_extra_costs_for_delivery_per_day(self):
        if self.distance > 10:
            raise TooLongDistance
        elif 10 > self.distance > 5:
            self.delivery_cost_per_day = 5
        else:
            self.delivery_cost_per_day = 0



    def get_absolute_url(self):
        return reverse("cart", kwargs={"pk": self.pk, "user": self.user})

    def __str__(self):
        return f"{self.date_of_start}"

