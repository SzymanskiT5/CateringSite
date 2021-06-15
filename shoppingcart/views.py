import datetime

from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import request
from django.shortcuts import render
from django.views.generic import FormView

from menu.models import Diet
from shoppingcart.exceptions import OrderDateInPast, OrderDateNotMinimumThreeDays
from shoppingcart.forms import DietOrderForm
from shoppingcart.models import DietOrder


def cart(request):
    return render(request, template_name="shoppingcart/shop.html")


class DietOrderView(FormView, UserPassesTestMixin):
    model = DietOrder
    template_name = "shoppingcart/diet_order.html"
    form_class = DietOrderForm


    def handle_order(self, order, price_per_day):
        order.end_of_the_order()
        order.whole_price(price_per_day)
        order.save()

    def handle_date_validation(self, order, form, price_per_day):

        try:
            order.check_if_date_is_past()
            order.check_if_date_is_three_days_ahead()

        except OrderDateInPast:
            messages.warning(self.request, "Diet cannot be from past!")
            return super().form_valid(form)

        except OrderDateNotMinimumThreeDays:
            messages.warning(self.request, "Diet can start 3 days ahead from today!")
            return super().form_valid(form)

        messages.success(self.request, "Diet added to your cart!")
        self.handle_order(order, price_per_day)
        return super().form_valid(form)

    def form_valid(self, form):
        name = form.cleaned_data.get("name")
        days = form.cleaned_data.get("days")
        megabytes = form.cleaned_data.get("megabytes")
        date_of_start = form.cleaned_data.get("date_of_start")
        diet_object = Diet.objects.filter(name=name).first()
        price_per_day = diet_object.price
        current_user = self.request.user
        order = DietOrder(name=name, megabytes=megabytes, days=days,
                          date_of_start=date_of_start, user=current_user)

        return self.handle_date_validation(order, form, price_per_day)



    def get_success_url(self):
        return self.request.path
