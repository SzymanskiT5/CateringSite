from typing import Union

from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Sum
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import ListView, UpdateView, DeleteView, CreateView, DetailView

from checkout.forms import OrderCheckout, DietOrderForm, LoggedUserOrderCheckoutForm, \
    NotLoggedUserOrderCheckoutForm
from checkout.google_api import GoogleApi
from checkout.models import DietOrder
from djangoProject.settings import GOOGLE_MAPS_API_KEY
from menu.models import Diet
from django.core.mail import send_mail

from users.models import Customer


def get_cookies_and_customer_or_create_customer(request) -> Customer:
    device = request.COOKIES.get("device")
    customer = Customer.objects.get_or_create(device=device)[0]
    return customer


def get_cookies_and_customer(request) -> Customer:
    device = request.COOKIES.get("device")
    customer = Customer.objects.get(device=device)
    return customer


def check_if_user_logged_or_get_or_create_customer(request) -> Customer:
    if request.user.is_authenticated:
        return request.user.customer
    else:
        return get_cookies_and_customer_or_create_customer(request)


def check_if_user_logged_or_get_customer(request) -> Customer:
    if request.user.is_authenticated:
        return request.user.customer
    else:
        return get_cookies_and_customer(request)


class CartView(ListView):
    model = DietOrder
    template_name = "checkout/cart.html"
    context_object_name = "orders"

    def check_dates_up_to_date(self) -> None:
        customer = check_if_user_logged_or_get_or_create_customer(self.request)
        diets = DietOrder.objects.filter(customer=customer).filter(is_purchased=False).order_by(
            "-to_pay")

        for diet in diets:
            diet.check_if_order_is_up_to_date()
        return diets

    def get_queryset(self) -> None:
        diets = self.check_dates_up_to_date()
        return diets

    def get_context_data(self, **kwargs) -> None:
        context = super().get_context_data(**kwargs)

        customer = check_if_user_logged_or_get_or_create_customer(self.request)

        context['to_pay'] = DietOrder.objects.filter(customer=customer).filter(
            is_purchased=False).aggregate(
            Sum('to_pay'))

        return context


class CheckoutView(UserPassesTestMixin, CreateView):
    model = OrderCheckout
    template_name = "checkout/checkout.html"

    def get_form_class(self):

        if self.request.user.is_authenticated:
            return LoggedUserOrderCheckoutForm

        return NotLoggedUserOrderCheckoutForm

    def get(self, *args, **kwargs) -> HttpResponse:


        instance = check_if_user_logged_or_get_or_create_customer(self.request)
        form = self.get_form_class()
        form = form(instance=instance)
        return render(self.request, "checkout/checkout.html", {"title": "DjangoCatering-Checkout",
                                                               "form": form})

    def form_valid(self, form) -> HttpResponse:
        checkout_order = form.save(commit=False)
        customer = check_if_user_logged_or_get_or_create_customer(self.request)
        checkout_order.customer = customer

        if not self.request.user.is_authenticated:
            customer.email = form.instance.email
            customer.save()

        self.set_order_checkout_to_pay(checkout_order)
        self.set_diet_order_confirmed_order(checkout_order)
        self.set_diet_order_is_purchased_to_true()
        checkout_order.save()
        messages.success(self.request, "Diet is ordered!")
        return super().form_valid(form)

    def form_invalid(self, form) -> HttpResponse:
        return render(self.request, "checkout/checkout.html",
                      {'form': form})

    def get_success_url(self) -> str:
        return reverse('cart')

    def set_diet_order_confirmed_order(self, checkout_order) -> None:
        customer = check_if_user_logged_or_get_or_create_customer(self.request)
        DietOrder.objects \
            .filter(customer=customer). \
            filter(is_purchased=False).filter(is_up_to_date=True).update(confirmed_order=checkout_order)

    def set_order_checkout_to_pay(self, order_confirmed_object) -> None:
        customer = check_if_user_logged_or_get_or_create_customer(self.request)

        order_confirmed_object.to_pay = DietOrder.objects \
            .filter(customer=customer). \
            filter(is_purchased=False).aggregate(Sum('to_pay')).get('to_pay__sum')

        order_confirmed_object.save()

    def set_diet_order_is_purchased_to_true(self) -> None:
        customer = check_if_user_logged_or_get_or_create_customer(self.request)

        DietOrder.objects.filter(customer=customer).filter(is_purchased=False).update(
                is_purchased=True)

    def test_func(self) -> bool:
        diets = self.get_diets_and_check_up_to_date()
        customer = check_if_user_logged_or_get_or_create_customer(self.request)
        diets_out_of_date = DietOrder.objects.filter(customer=customer).filter(
                is_up_to_date=False)


        if diets_out_of_date:
            messages.warning(self.request, "Delete or change out of date orders")
            return False

        if not diets:
            messages.warning(self.request, "You don't have any orders to checkout")
            return False

        return True

    def get_diets_and_check_up_to_date(self) -> None:
        customer = check_if_user_logged_or_get_or_create_customer(self.request)
        diets = DietOrder.objects.filter(customer=customer).filter(is_purchased=False)

        for diet in diets:
            diet.check_if_order_is_up_to_date()
        return diets

    def handle_no_permission(self) -> HttpResponse:
        return redirect('cart')


class DietOrderView(CreateView):
    template_name = "checkout/diet_order.html"
    form_class = DietOrderForm

    def form_valid(self, form) -> HttpResponse:
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

    def set_user_or_device_customer(self, order) -> None:
        customer = check_if_user_logged_or_get_or_create_customer(self.request)
        order.customer = customer

    def handle_order_information(self, order) -> None:
        self.set_user_or_device_customer(order)
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

    def form_invalid(self, form) -> HttpResponse:
        return render(self.request, "checkout/diet_order.html",
                      {'form': self.form_class(self.request.POST), "api_key": GOOGLE_MAPS_API_KEY})

    def get(self, *args, **kwargs) -> HttpResponse:
        return render(self.request, "checkout/diet_order.html",
                      {'form': self.form_class(), "api_key": GOOGLE_MAPS_API_KEY})

    def get_success_url(self) -> HttpResponse:
        return reverse("cart")


class OrderUpdateView(UserPassesTestMixin, UpdateView, DietOrderView):
    model = DietOrder
    form_class = DietOrderForm
    template_name = "checkout/diet_order.html"

    def get(self, *args, **kwargs) -> HttpResponse:
        return render(self.request, "checkout/diet_order.html",
                      {'form': self.form_class(instance=self.get_object()), "api_key": GOOGLE_MAPS_API_KEY})

    def form_valid(self, form) -> HttpResponse:
        order_old = self.get_object()
        order = form.save(commit=False)
        place_id = GoogleApi.get_place_id(order.address, order.address_info)
        order.distance = GoogleApi.calculate_distance_between_order_and_catering(place_id)

        if order.distance < 10:
            self.handle_order_information(order)
            order_old.delete()
            return super().form_valid(form)

        messages.warning(self.request, "We don't delivery to this destination, it's more than 10 km")
        return render(self.request, "checkout/diet_order.html",
                      {'form': self.form_class(self.request.POST), "api_key": GOOGLE_MAPS_API_KEY})

    def test_func(self) -> bool:
        order = self.get_object()
        customer = check_if_user_logged_or_get_customer(self.request)
        if not order.customer == customer:
            raise Http404("Page not found")
        return True



class OrderDeleteView(DeleteView):
    model = DietOrder

    def get_success_url(self) -> HttpResponse:
        return reverse('cart')

    def test_func(self) -> bool:
        order = self.get_object()
        customer = check_if_user_logged_or_get_customer(self.request)
        if not order.customer == customer:
            raise Http404("Page not found")
        return True


class MyOrdersHistory(ListView):
    model = OrderCheckout
    template_name = "checkout/orders_history.html"
    context_object_name = "checkouts"

    def get_queryset(self) -> Union[OrderCheckout, Exception]:
        if not self.request.user.is_authenticated:
            raise Http404("Page not found")

        return OrderCheckout.objects.filter(customer=self.request.user.customer).order_by("date_of_purchase")




class MyOrdersHistoryDetail(DetailView):
    model = OrderCheckout
    template_name = "checkout/detailed_orders_history.html"
    context_object_name = "checkout"

    def test_func(self) -> Union[bool, Exception]:
        checkout = self.get_object()
        if self.request.user.is_authenticated:
            if self.request.user.customer == checkout.customer:
                return True

        raise Http404("Page not found")




