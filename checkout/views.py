from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import FormView, ListView, UpdateView, DeleteView
from django.views.generic.base import View

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
        context['total_price'] = DietOrder.objects.filter(user=self.request.user).aggregate(Sum('price'))

        return context

# def test(request):
#     if request.method == "GET":
#         return render(request, "checkout/maps.html", {"form": DietOrderForm})
#
#     else:
#         name = request.POST("name")
#         days = request.POST("days")
#         megabytes = request.POST("megabytes")
#         address = request.POST("ship-address")
#         print(address)
#         address_info = request.POST("address2")
#         locality = request.POST("locality")
#         state = request.POST("state")
#         post_code = request.POST("post_code")
#         date_of_start = request.POST("date_of_start")
#         diet_object = Diet.objects.filter(name=name).first()
#         price_per_day = diet_object.price
#         current_user = request.user
#         order = DietOrder(name=name, megabytes=megabytes, days=days,
#                           date_of_start=date_of_start, user=current_user, address=address,
#                           address_info=address_info, locality=locality, state=state, post_code=post_code)
#
#         # return self.handle_date_validation(order, form, price_per_day)



class DietOrderView(FormView):
    model = DietOrder
    template_name = "checkout/maps.html"
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
        address = self.request.POST.get("ship-address")
        address_info = self.request.POST.get("address_info")
        locality = self.request.POST.get("locality")
        state = self.request.POST.get("state")
        post_code = self.request.POST.get("post_code")
        date_of_start = form.cleaned_data.get("date_of_start")
        diet_object = Diet.objects.filter(name=name).first()
        price_per_day = diet_object.price
        current_user = self.request.user
        order = DietOrder(name=name, megabytes=megabytes, days=days,
                          date_of_start=date_of_start, user=current_user, address=address,
                          address_info=address_info, locality = locality, state= state, post_code= post_code)

        return self.handle_date_validation(order, form, price_per_day)

    def get_success_url(self):
        return reverse('cart')


class OrderUpdateView(DietOrderView, UpdateView):
    form_class = DietOrderForm
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

# class TestView(FormView):
#     model =
#     template_name = "checkout/maps.html"
#
#
#     def form_valid(self):
#         return render(request, "checkout/maps.html")
#     if request.method == "POST":
#        ship_address = form.cleaned_data.get("ship-address")
