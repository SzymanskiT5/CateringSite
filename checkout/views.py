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
from django.views.generic import ListView, UpdateView, DeleteView, FormView, CreateView
from django.views.generic.base import View

from checkout.exceptions import OrderDateInPast, OrderDateNotMinimumThreeDays, TooLongDistance
from checkout.forms import PurchaserInfoForm, OrderConfirmedForm, DietOrderForm
from checkout.models import DietOrder, PurchaserInfo
from djangoProject.settings import GOOGLE_MAPS_API_KEY, CATERING_PLACE_ID
from menu.models import Diet


class CartView(ListView):
    model = DietOrder
    template_name = "checkout/cart.html"
    context_object_name = "orders"

    def get_queryset(self):
        return DietOrder.objects.filter(user=self.request.user).filter(is_purchased=False).order_by("-to_pay")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_price'] = DietOrder.objects.filter(user=self.request.user).filter(is_purchased=False).aggregate(
            Sum('to_pay'))

        return context



class OrderUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = DietOrder

    def update_order(self):
        order = self.get_object()
        name = self.request.POST.get("name")
        order.days = int(self.request.POST.get("days"))
        order.megabytes = self.request.POST.get("megabytes")
        order.address = self.request.POST.get("ship-address")
        order.address_info = self.request.POST.get("address_info")
        order.locality = self.request.POST.get("locality")
        order.state = self.request.POST.get("state")
        order.post_code = self.request.POST.get("post_code")
        order.date_of_start = self.create_date_time_from_request()
        place_id = self.get_place_id(order.address, order.address_info)
        distance = self.calculate_distance_between_order_and_catering(place_id)
        diet_object = Diet.objects.filter(name=name).first()
        order.name = diet_object
        order.diet_cost_per_day = diet_object.price
        order.distance = distance
        order.end_of_the_order()
        order.calculate_diet_cost()

        return order

    def get(self, request, *args, **kwargs):
        return render(request, "checkout/diet_order_update.html",
                      {"title": "Change Order", "api_key": GOOGLE_MAPS_API_KEY, "order": self.get_object()})

    def post(self, request, *args, **kwargs):
        new_order = self.update_order()
        return self.handle_order_validation(new_order)

    def test_func(self):
        order = self.get_object()
        if not self.request.user == order.user:
            raise Http404("Page not Found")
        return True


class OrderDeleteView(DeleteView):
    model = DietOrder

    def get_success_url(self):
        return reverse('cart')


class CheckoutView(View):
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


class DietOrderView(CreateView):
    template_name = "checkout/diet_order.html"
    form_class = DietOrderForm

    def get_place_id(self, address, address_info):
        parameteres = {"input": address + " " + address_info, "key": GOOGLE_MAPS_API_KEY}
        localization_api_call = requests.get("https://maps.googleapis.com/maps/api/place/autocomplete/json",
                                             params=parameteres).text
        json_object = json.loads(localization_api_call)
        place_id = json_object["predictions"][0]["place_id"]
        return place_id

    def calculate_distance_between_order_and_catering(self, place_id):
        parameters = {"origin": f"place_id:{CATERING_PLACE_ID}", "destination": f"place_id:{place_id}",
                      "key": f"{GOOGLE_MAPS_API_KEY}"}
        distance_api_call = requests.get("https://maps.googleapis.com/maps/api/directions/json?",
                                         params=parameters).text
        json_object = json.loads(distance_api_call)
        distance = json_object['routes'][0]['legs'][0]['distance']['value']
        distance = int(distance) / 1000
        return distance

    def handle_order_validation(self, order):
        try:
            order.calculate_extra_costs_for_delivery_per_day()
            order.calculate_delivery_cost()
            order.calculate_whole_price()

            # order.check_if_date_is_past()
            order.check_if_date_is_three_days_ahead()
            return self.save_order(order)

        except OrderDateInPast:
            messages.warning(self.request, "Diet cannot be from past!")
            return render(self.request, "checkout/diet_order.html")

        except OrderDateNotMinimumThreeDays:
            messages.warning(self.request, "Diet can start 3 days ahead from today!")
            return render(self.request, "checkout/diet_order.html")

        except TooLongDistance:
            messages.warning(self.request, "We don't delivery to this destination, it's more than 10 km")
            return render(self.request, "checkout/diet_order.html")

    def save_order(self, order):
        order.save()
        messages.success(self.request, "Diet added to your cart!")
        return redirect("cart")

    def form_valid(self, form):

        order = form.save(commit=False)
        order.user = self.request.user
        order.calculate_days_between_dates()

        diet_object = Diet.objects.filter(name=order.name).first()
        order.diet_cost_per_day = diet_object.price

        place_id = self.get_place_id(order.address, order.address_info)
        order.distance = self.calculate_distance_between_order_and_catering(place_id)

        order.calculate_diet_cost()

        return self.handle_order_validation(order)


    def form_invalid(self, form):
        return render(self.request, "checkout/diet_order.html", {'form': self.form_class(self.request.POST)})

    def get_context_data(self, **kwargs):
        context = super(DietOrderView, self).get_context_data(**kwargs)
        context['api_key'] = GOOGLE_MAPS_API_KEY
        return context


