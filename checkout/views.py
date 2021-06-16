import datetime
import sys

from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import request
from django.shortcuts import render, get_object_or_404
from django.views.generic import FormView, ListView

from menu.models import Diet
from checkout.exceptions import OrderDateInPast, OrderDateNotMinimumThreeDays
from checkout.forms import DietOrderForm
from checkout.models import DietOrder
from django.db.models import Sum


class CartView(ListView):
    model = DietOrder
    template_name = "checkout/cart.html"
    context_object_name = "orders"

    def get_queryset(self):
        return DietOrder.objects.filter(user=self.request.user).order_by("-price")

    def get_context_data(self, **kwargs):
        context = super(CartView, self).get_context_data(**kwargs)
        # total_price_query = DietOrder.objects.filter(user=self.request)
        context['total_price'] = DietOrder.objects.filter(user=self.request.user).aggregate(Sum('price'))

        return context


class DietOrderView(FormView):
    model = DietOrder
    template_name = "checkout/diet_order.html"
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
