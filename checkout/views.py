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
    model = DietOrder

    def handle_order(self, order, price_per_day):
        order.end_of_the_order()
        order.whole_price(price_per_day)

    def handle_date_validation(self, order):
        try:
            order.check_if_date_is_past()
            order.check_if_date_is_three_days_ahead()


        except OrderDateInPast:
            messages.warning(self.request, "Diet cannot be from past!")
            return render(self.request, "checkout/diet_order.html")

        except OrderDateNotMinimumThreeDays:
            messages.warning(self.request, "Diet can start 3 days ahead from today!")
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
        return render(request, "checkout/diet_order.html", {"title": "DjangoCatering-Order"})

    def post(self, request, *args, **kwargs):
        order = self.create_order_object()
        self.handle_date_validation(order)
        return self.save_order(order)



class OrderUpdateView(DietOrderView, UpdateView):
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
        diet_object = Diet.objects.filter(name=name).first()
        order.name = diet_object

        order.price_per_day = diet_object.price
        return order


    def post(self, request, *args, **kwargs):
        new_order = self.update_order()
        self.handle_date_validation(new_order)
        return self.save_order(new_order)




class OrderDeleteView(DeleteView):
    model = DietOrder

    def get_success_url(self):
        return reverse('cart')
