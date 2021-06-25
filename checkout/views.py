import json
from datetime import datetime, timezone

import requests
from django.utils import timezone as djangozone
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import FormView, ListView, UpdateView, DeleteView
from django.views.generic.base import View
from requests import Response

from djangoProject.settings import GOOGLE_MAPS_API_KEY, CATERING_PLACE_ID
from menu.models import Diet
from checkout.exceptions import OrderDateInPast, OrderDateNotMinimumThreeDays, TooLongDistance
from checkout.forms import DietOrderForm
from checkout.models import DietOrder
from django.db.models import Sum
import pytz


class CartView(ListView):
    model = DietOrder
    template_name = "checkout/cart.html"
    context_object_name = "orders"

    def get_queryset(self):
        return DietOrder.objects.filter(user=self.request.user).order_by("-to_pay")

    def get_context_data(self, **kwargs):
        context = super(CartView, self).get_context_data(**kwargs)
        context['total_price'] = DietOrder.objects.filter(user=self.request.user).aggregate(Sum('to_pay'))

        return context


class DietOrderView(View):
    model = DietOrder
    template_name = "checkout/diet_order.html"

    def handle_order_validation(self, order):
        try:
            order.calculate_extra_costs_for_delivery_per_day()
            order.calculate_delivery_cost()
            order.calculate_whole_price()

            order.check_if_date_is_past()
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

    def create_date_time_from_request(self):
        day_of_start = self.request.POST.get("date_of_start_day")
        month_of_start = self.request.POST.get("date_of_start_month")
        year_of_start = self.request.POST.get("date_of_start_year")
        date_of_start = datetime.fromisoformat(year_of_start + "-" + month_of_start + "-" + day_of_start)
        date_of_start = pytz.utc.localize(date_of_start)
        return date_of_start

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

    def create_order_object(self):
        name = self.request.POST.get("name")
        days = int(self.request.POST.get("days"))
        megabytes = self.request.POST.get("megabytes")
        address = self.request.POST.get("ship-address")
        address_info = self.request.POST.get("address_info")
        locality = self.request.POST.get("locality")
        state = self.request.POST.get("state")
        post_code = self.request.POST.get("post_code")
        date_of_start = self.create_date_time_from_request()
        diet_object = Diet.objects.filter(name=name).first()
        price_per_day = diet_object.price
        current_user = self.request.user
        place_id = self.get_place_id(address, address_info)
        distance = self.calculate_distance_between_order_and_catering(place_id)
        order = DietOrder(name=diet_object,
                          megabytes=megabytes,
                          days=days,
                          date_of_start=date_of_start,
                          user=current_user,
                          address=address,
                          address_info=address_info,
                          locality=locality,
                          state=state,
                          post_code=post_code,
                          distance=distance,
                          diet_cost_per_day=price_per_day,
                          )
        order.end_of_the_order()
        order.calculate_diet_cost()


        return order




    def get(self, request, *args, **kwargs):
        return render(request, "checkout/diet_order.html", {"title": "DjangoCatering-Order", "api_key":GOOGLE_MAPS_API_KEY})

    def post(self, request, *args, **kwargs):
        order = self.create_order_object()
        return self.handle_order_validation(order)


class OrderUpdateView(DietOrderView, UpdateView):
    model = DietOrder
    # template_name = "checkout/diet_order_update.html"


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
        return render(request, "checkout/diet_order_update.html", {"title": "Change Order","api_key":GOOGLE_MAPS_API_KEY,"order":self.get_object()})



    def post(self, request, *args, **kwargs):
        new_order = self.update_order()
        return self.handle_order_validation(new_order)


class OrderDeleteView(DeleteView):
    model = DietOrder

    def get_success_url(self):
        return reverse('cart')
