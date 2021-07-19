import datetime
from django.db import models
from django.urls import reverse
from django.utils import timezone

from djangoProject.settings import HOLIDAYS_POLAND
from menu.models import Diet
from users.models import Customer


class OrderCheckout(models.Model):
    email = models.EmailField()
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    date_of_purchase = models.DateTimeField(default=timezone.now)
    payment_method = models.TextField()
    to_pay = models.FloatField(null=True)
    surname = models.CharField(max_length=15)
    name = models.CharField(max_length=20)
    telephone = models.CharField(max_length=15)
    address = models.CharField(max_length=100)
    address_info = models.CharField(max_length=50)
    locality = models.CharField(max_length=25)
    state = models.CharField(max_length=25)
    post_code = models.CharField(max_length=6)
    note = models.TextField()

    def __str__(self) -> str:
        return f"{self.email} {self.customer} {self.date_of_purchase}, {self.payment_method}"

    def get_absolute_url(self) -> str:
        return reverse("order_history", kwargs={"user": self.customer, "pk": self.pk, })


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
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    date_of_end = models.DateField()
    address = models.CharField(max_length=100)
    address_info = models.CharField(max_length=50)
    locality = models.CharField(max_length=25)
    state = models.CharField(max_length=25)
    post_code = models.CharField(max_length=8)
    distance = models.FloatField()
    is_purchased = models.BooleanField(default=False)
    is_up_to_date = models.BooleanField(default=True)
    confirmed_order = models.ForeignKey(OrderCheckout, on_delete=models.CASCADE, null=True)

    def calculate_whole_price(self) -> None:
        self.to_pay = self.diet_cost + self.delivery_cost

    def calculate_diet_cost(self) -> None:
        self.diet_cost = self.days * self.diet_cost_per_day

    def calculate_delivery_cost(self) -> None:
        self.delivery_cost = self.delivery_cost_per_day * self.days

    def calculate_holidays_days_between_dates(self) -> int:
        dates_list = [self.date_of_start + datetime.timedelta(days=x) for x in
                      range(0, (self.date_of_end - self.date_of_start).days)]

        days_to_avoid = 0
        for day in dates_list:
            if day in HOLIDAYS_POLAND:
                days_to_avoid += 1

        return days_to_avoid

    def calculate_weekend_days(self) -> int:
        dates_list = [self.date_of_start + datetime.timedelta(days=x) for x in
                      range(0, (self.date_of_end - self.date_of_start).days)]
        days_to_avoid = 0
        for date in dates_list:
            if date.weekday() in range(5, 7) and date.weekday() not in HOLIDAYS_POLAND:
                days_to_avoid += 1

        return days_to_avoid

    def calculate_days_between_dates(self, holidays_days, weekend_days) -> None:
        """ days + 1 because, catering includes last day, not only difference between days"""
        days = (self.date_of_end - self.date_of_start).days - holidays_days - weekend_days
        self.days = days + 1

    def calculate_extra_costs_for_delivery_per_day(self) -> None:
        if 10 > self.distance > 5:
            self.delivery_cost_per_day = 5
        else:
            self.delivery_cost_per_day = 0

    def check_if_order_is_up_to_date(self) -> None:
        if self.date_of_start - timezone.now().date() <= datetime.timedelta(days=3):

            self.is_up_to_date = False


    def get_absolute_url(self) -> str:
        return reverse("cart", kwargs={"pk": self.pk, "user": self.customer})

    def __str__(self) -> str:
        return f"STARTS: {self.date_of_start} ENDS: {self.date_of_end}, {self.address}, {self.address_info}"


class RegistrationPrzelewy24(models.Model):
    merchantID = models.IntegerField(default=11111)
    posID = models.IntegerField(default=11111)
    sessionId = models.CharField(max_length=100, default="test7")
    amount = models.IntegerField(default=1)
    currency = models.CharField(max_length=3, default="PLN")
    description = models.CharField(max_length=1024, default="test order")
    email = models.EmailField(max_length=50, default="john.doe@example.com")
    client = models.CharField(max_length=40, null=True)
    address = models.CharField(max_length=80, null=True)
    zip = models.CharField(max_length=10, null=True)
    city = models.CharField(max_length=50, null=True)
    country = models.CharField(max_length=2, default="PL")
    phone = models.CharField(max_length=12, null=True)
    language = models.CharField(max_length=2, default="pl")
    method = models.IntegerField(null=True)
    urlReturn = models.URLField(default="http://127.0.0.1:8000/cart")
    urlStatus = models.CharField(max_length=250),
    timeLimit = models.IntegerField(default=5, null=True)
    channel = models.IntegerField(default=16, null=True)
    waitForResult = models.BooleanField(null=True)
    regulationAccept = models.BooleanField(default=False)
    shipping = models.IntegerField(models.IntegerField, null=True)
    transferLabel = models.CharField(max_length=20, null=True)
    mobileLib = models.IntegerField(default=1, null=True)
    sdkVersion = models.CharField(max_length=10, null=True)
    sign = models.CharField(max_length=100, default="596af9bc39271b4cfdab45937")
    encoding = models.CharField(max_length=15, null=True)
    methodRefId = models.CharField(max_length=250)
