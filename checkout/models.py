import datetime

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
from menu.models import Diet
from checkout.exceptions import OrderDateInPast, OrderDateNotMinimumThreeDays, TooLongDistance


class OrderConfirmed(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    date_of_purchase = models.DateTimeField(default=timezone.now)
    payment_method = models.TextField()
    to_pay = models.FloatField(null=True)

    def __str__(self):
        return f"{self.user} {self.date_of_purchase}, {self.payment_method}"


class DietOrder(models.Model):
    name = models.ForeignKey(Diet, on_delete=models.PROTECT)
    megabytes = models.IntegerField()
    days = models.IntegerField()
    to_pay = models.FloatField()
    delivery_cost = models.FloatField()
    diet_cost = models.FloatField()
    delivery_cost_per_day = models.FloatField()
    diet_cost_per_day = models.FloatField()
    date_of_start = models.DateField()
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    date_of_end = models.DateField()
    address = models.CharField(max_length=100)
    address_info = models.CharField(max_length=50)
    locality = models.CharField(max_length=25)
    state = models.CharField(max_length=25)
    post_code = models.CharField(max_length=8)
    distance = models.FloatField()
    is_purchased = models.BooleanField(default=False)
    confirmed_order = models.ForeignKey(OrderConfirmed, on_delete=models.CASCADE, null=True)

    def calculate_whole_price(self):
        self.to_pay = self.diet_cost + self.delivery_cost

    def calculate_diet_cost(self):
        self.diet_cost = self.days * self.diet_cost_per_day

    def calculate_delivery_cost(self):
        self.delivery_cost = self.delivery_cost_per_day * self.days

    # def end_of_the_order(self):
    #     end = self.date_of_start + datetime.timedelta(days=self.days)
    #     self.date_of_end = end

    # def check_if_date_is_past(self):
    #     if self.date_of_start < timezone.now().date():
    #         raise OrderDateInPast

    # def check_if_date_is_three_days_ahead(self):
    #     if self.date_of_start - timezone.now().date() <= datetime.timedelta(days=3):
    #         raise OrderDateNotMinimumThreeDays


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
        return f"STARTS: {self.date_of_start} ENDS: {self.date_of_end}, {self.address}, {self.address_info}"




class PurchaserInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    surname = models.CharField(max_length=15)
    name = models.CharField(max_length=20)
    telephone = models.CharField(max_length=15)
    address = models.TextField()
    address_info = models.TextField()
    locality = models.TextField()
    state = models.TextField()
    post_code = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.surname} {self.name} "
