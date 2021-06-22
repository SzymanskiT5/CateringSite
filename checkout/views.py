from datetime import datetime, timezone
from django.utils import timezone as djangozone
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import FormView, ListView, UpdateView, DeleteView
from django.views.generic.base import View

from menu.models import Diet
from checkout.exceptions import OrderDateInPast, OrderDateNotMinimumThreeDays
from checkout.forms import DietOrderForm
from checkout.models import DietOrder
from django.db.models import Sum
import pytz

class CartView(ListView):
    model = DietOrder
    template_name = "checkout/cart.html"
    context_object_name = "orders"

    def get_queryset(self):
        return DietOrder.objects.filter(user=self.request.user).order_by("-price")

    def get_context_data(self, **kwargs):
        context = super(CartView, self).get_context_data(**kwargs)
        context['total_price'] = DietOrder.objects.filter(user=self.request.user).aggregate(Sum('price'))

        return context


class DietOrderView(View):

    def handle_order(self, order, price_per_day):
        order.end_of_the_order()
        order.whole_price(price_per_day)

    def handle_date_validation(self, order):
        try:
            order.check_if_date_is_past()
            order.check_if_date_is_three_days_ahead()
            return self.save_order(order)

        except OrderDateInPast:
            messages.warning(self.request, "Diet cannot be from past!")
            return render(self.request, "checkout/maps.html")

        except OrderDateNotMinimumThreeDays:
            messages.warning(self.request, "Diet can start 3 days ahead from today!")
            return render(self.request, "checkout/maps.html")

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

        order = DietOrder(name=diet_object,
                          megabytes=megabytes,
                          days=days,
                          date_of_start=date_of_start,
                          user=current_user,
                          address=address,
                          address_info=address_info,
                          locality=locality,
                          state=state,
                          post_code=post_code)
        self.handle_order(order, price_per_day)
        return order

    def get(self, request, *args, **kwargs):
        return render(request, "checkout/maps.html", {"title": "DjangoCatering-Order"})

    def post(self, request, *args, **kwargs):
        order = self.create_order_object()
        return self.handle_date_validation(order)


class OrderUpdateView(DietOrderView, UpdateView):
    template_name = "checkout/diet_order_update.html"

    def set_new_values_to_diet(self, name, days, megabytes, date_of_start, address,
                               address_info, locality, state, post_code):
        new_order = self.object
        new_order.name = name
        new_order.days = days
        new_order.megabytes = megabytes
        new_order.date_of_start = date_of_start
        new_order.address = address
        new_order.address_info = address_info
        new_order.locality = locality
        new_order.state = state
        new_order.post_code = post_code
        return new_order

    def form_valid(self, form):
        name = form.cleaned_data.get("name")
        days = form.cleaned_data.get("days")
        megabytes = form.cleaned_data.get("megabytes")
        date_of_start = form.cleaned_data.get("date_of_start")
        diet_object = Diet.objects.filter(name=name).first()
        price_per_day = diet_object.price
        address = self.request.POST.get("ship-address")
        address_info = self.request.POST.get("address_info")
        locality = self.request.POST.get("state")
        state = self.request.POST.get("state")
        post_code = self.request.POST.get("post_code")
        new_order = self.set_new_values_to_diet(name, days, megabytes, date_of_start,
                                                address, address_info, locality, state, post_code)
        return self.handle_date_validation(new_order, form, price_per_day)


class OrderDeleteView(DeleteView):
    model = DietOrder

    def get_success_url(self):
        return reverse('cart')
