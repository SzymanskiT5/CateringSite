import datetime
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
from menu.models import Diet
from checkout.exceptions import OrderDateInPast, OrderDateNotMinimumThreeDays


class DietOrder(models.Model):
    name = models.ForeignKey(Diet, on_delete=models.PROTECT)
    megabytes = models.IntegerField()
    days = models.IntegerField(null=True)
    price = models.FloatField(null=True)
    date_of_start = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    date_of_end = models.DateField()

    def whole_price(self, price_per_day):
        self.price = self.days * price_per_day

    def end_of_the_order(self):
        end = self.date_of_start + datetime.timedelta(days=self.days)
        self.date_of_end = end

    def check_if_date_is_past(self):
        if self.date_of_start < timezone.now():
            raise OrderDateInPast

    def check_if_date_is_three_days_ahead(self):
        if self.date_of_start - timezone.now() <= datetime.timedelta(days=3):
            raise OrderDateNotMinimumThreeDays

    def get_absolute_url(self):
        return reverse("cart", kwargs={"pk": self.pk, "user": self.user})

    def __str__(self):
        return f"{self.date_of_start}"

