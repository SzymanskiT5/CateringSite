import json
from datetime import datetime

import pytz
import requests
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.db.models import Sum
from django.http import Http404
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import ListView, UpdateView, DeleteView, FormView, CreateView, DetailView
from django.views.generic.base import View

from checkout.exceptions import NoOrders
from checkout.forms import PurchaserInfoForm, OrderConfirmedForm, DietOrderForm
from checkout.google_api import GoogleApi
from checkout.models import DietOrder, PurchaserInfo
from djangoProject.settings import GOOGLE_MAPS_API_KEY, CATERING_PLACE_ID
from menu.models import Diet


class CartView(ListView):
    model = DietOrder
    template_name = "checkout/cart.html"
    context_object_name = "orders"

    def check_dates_up_to_date(self):
        diets = DietOrder.objects.filter(user=self.request.user).filter(is_purchased=False).order_by("-to_pay")
        for diet in diets:
            diet.check_if_order_is_up_to_date()
        return diets

    def get_queryset(self):
        diets = self.check_dates_up_to_date()
        return diets

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['to_pay'] = DietOrder.objects.filter(user=self.request.user).filter(is_purchased=False).aggregate(
            Sum('to_pay'))
        return context

    # def post(self, *args, **kwargs):
    #     if self.request.POST["checkout_button"]:
    #         diets = self.check_dates_up_to_date()
    #         diets_out_of_date = DietOrder.objects.filter(user=self.request.user).filter(is_up_to_date=False)
    #
    #
    #         if diets_out_of_date:
    #             messages.warning(self.request, "Delete or change out of date orders")
    #             return render(self.request, "checkout/cart.html", {"orders":diets} )
    #
    #
    #         if diets:
    #             return redirect("checkout")
    #
    #         messages.warning(self.request, "You order is empty")
    #         return render(self.request, "checkout/cart.html", {"orders":diets} )


class CheckoutView(UserPassesTestMixin, View):
    template_name = "checkout/checkout.html"

    def get(self, *args, **kwargs):

        instance = PurchaserInfo.objects.filter(user=self.request.user).first()
        purchaser_info_form = PurchaserInfoForm(instance=instance)
        order_confirmed_form = OrderConfirmedForm()

        return render(self.request, "checkout/checkout.html", {"title": "DjangoCatering-Checkout",
                                                               "order_confirmed_form": order_confirmed_form,
                                                               "purchaser_info_form": purchaser_info_form})

    def post(self, *args, **kwargs):
        instance = PurchaserInfo.objects.filter(user=self.request.user).first()
        purchaser_info_form = PurchaserInfoForm(self.request.POST, instance=instance)
        order_confirmed_form = OrderConfirmedForm(self.request.POST)
        purchaser_info_form.instance.user = self.request.user
        order_confirmed_form.instance.user = self.request.user

        if purchaser_info_form.is_valid() and order_confirmed_form.is_valid():
            purchaser_info_form.save()
            order_confirmed_object = order_confirmed_form.save()
            self.set_order_confirmed_to_pay(order_confirmed_object)
            self.set_diet_order_fields(order_confirmed_object)

        return redirect('cart')

    def set_order_confirmed_to_pay(self, order_confirmed_object):
        order_confirmed_object.to_pay = DietOrder.objects \
            .filter(user=self.request.user). \
            filter(is_purchased=False).aggregate(Sum('to_pay')).get('to_pay__sum')
        order_confirmed_object.save()

    def set_diet_order_fields(self, order_confirmed_object):
        orders = list((DietOrder.objects.filter(user=self.request.user).filter(is_purchased=False).all()))
        for order in orders:
            order.is_purchased = True
            order.confirmed_order = order_confirmed_object
            order.save()

    def test_func(self):
        diets = self.get_diets_and_check_up_to_date()
        diets_out_of_date = DietOrder.objects.filter(user=self.request.user).filter(is_up_to_date=False)

        if diets_out_of_date:
            messages.warning(self.request, "Delete or change out of date orders")
            return False
        if not diets:
            messages.warning(self.request, "You don't have any orders to checkout")
            return False
        return True

    def get_diets_and_check_up_to_date(self):
        diets = DietOrder.objects.filter(user=self.request.user).filter(is_purchased=False).order_by("-to_pay")
        for diet in diets:
            diet.check_if_order_is_up_to_date()
        return diets

    def handle_no_permission(self):
        return redirect('cart')


class DietOrderView(CreateView):
    template_name = "checkout/diet_order.html"
    form_class = DietOrderForm

    def form_valid(self, form):
        order = form.save(commit=False)
        place_id = GoogleApi.get_place_id(order.address, order.address_info)
        order.distance = GoogleApi.calculate_distance_between_order_and_catering(place_id)
        if order.distance < 10:
            self.handle_order_information(order)
            messages.success(self.request, "Diet added to your cart!")
            return super().form_valid(form)

        messages.warning(self.request, "We don't delivery to this destination, it's more than 10 km")
        return render(self.request, "checkout/diet_order.html",
                      {'form': self.form_class(self.request.POST), "api_key": GOOGLE_MAPS_API_KEY})

    def handle_order_information(self, order):
        order.user = self.request.user
        len_of_holidays_days = order.calculate_holidays_days_between_dates()
        len_of_weekend_days = order.calculate_weekend_days()
        order.calculate_days_between_dates(len_of_holidays_days, len_of_weekend_days)
        diet_object = Diet.objects.filter(name=order.name).first()
        order.diet_cost_per_day = diet_object.price
        order.calculate_diet_cost()
        order.calculate_extra_costs_for_delivery_per_day()
        order.calculate_delivery_cost()
        order.calculate_whole_price()
        order.save()

    def form_invalid(self, form):
        return render(self.request, "checkout/diet_order.html",
                      {'form': self.form_class(self.request.POST), "api_key": GOOGLE_MAPS_API_KEY})

    def get(self, *args, **kwargs):
        return render(self.request, "checkout/diet_order.html",
                      {'form': self.form_class(), "api_key": GOOGLE_MAPS_API_KEY})

    def get_success_url(self):
        return reverse("cart")


class OrderUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView, DietOrderView):  # SPRAWDZIC LOGIN REQUIRED
    model = DietOrder
    form_class = DietOrderForm
    template_name = "checkout/diet_order.html"

    def get(self, *args, **kwargs):
        return render(self.request, "checkout/diet_order.html",
                      {'form': self.form_class(instance=self.get_object()), "api_key": GOOGLE_MAPS_API_KEY})


## update nie dziala
    def form_valid(self, form):
        order = self.get_object()
        order_changed = form.save(commit=False)
        place_id = GoogleApi.get_place_id(order_changed.address, order_changed.address_info)
        order.distance = GoogleApi.calculate_distance_between_order_and_catering(place_id)

        if order.distance < 10:
            self.replace_order_information(order, order_changed)
            messages.success(self.request, "Diet added to your cart!")
            return super().form_valid(form)

        messages.warning(self.request, "We don't delivery to this destination, it's more than 10 km")
        return render(self.request, "checkout/diet_order.html",
                      {'form': self.form_class(self.request.POST), "api_key": GOOGLE_MAPS_API_KEY})

    def replace_order_information(self, order, order_changed):
        order_changed.user = self.request.user
        len_of_holidays_days = order_changed.calculate_holidays_days_between_dates()
        len_of_weekend_days = order_changed.calculate_weekend_days()
        order_changed.calculate_days_between_dates(len_of_holidays_days, len_of_weekend_days)
        diet_object = Diet.objects.filter(name=order_changed.name).first()
        order_changed.diet_cost_per_day = diet_object.price
        order_changed.calculate_diet_cost()
        order_changed.calculate_extra_costs_for_delivery_per_day()
        order_changed.calculate_delivery_cost()
        order_changed.calculate_whole_price()
        order.save(order_changed)

    def test_func(self):
        order = self.get_object()
        if not self.request.user == order.user:
            raise Http404("Page not Found")
        return True


class OrderDeleteView(DeleteView):
    model = DietOrder

    def get_success_url(self):
        return reverse('cart')
