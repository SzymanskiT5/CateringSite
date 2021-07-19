from typing import Union
from django.core.mail import EmailMessage
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Sum
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import ListView, UpdateView, DeleteView, CreateView, DetailView
from checkout.forms import OrderCheckout, DietOrderForm, LoggedUserOrderCheckoutForm, \
    NotLoggedUserOrderCheckoutForm
from checkout.google_api import GoogleApi
from checkout.models import DietOrder, RegistrationPrzelewy24
from djangoProject.settings import GOOGLE_MAPS_API_KEY, ACCOUNT_NUMBER
from menu.models import Diet
import requests
from users.models import Customer
from .serializers import RegistrationPrzelewy24Serializer



def get_or_create_customer_by_cookies(request) -> Customer:
    device = request.COOKIES.get("device")
    customer = Customer.objects.get_or_create(device=device)[0]
    return customer


def get_customer_by_cookies(request) -> Customer:
    device = request.COOKIES.get("device")
    customer = Customer.objects.get(device=device)
    return customer


def get_customer_or_create(request) -> Customer:
    if request.user.is_authenticated:
        return request.user.customer
    else:
        return get_or_create_customer_by_cookies(request)


def get_customer(request) -> Customer:
    if request.user.is_authenticated:
        return request.user.customer
    else:
        return get_customer_by_cookies(request)

def check_dates_up_to_date(request):
    customer = get_customer_or_create(request)
    diets = DietOrder.objects.filter(customer=customer).filter(is_purchased=False).order_by(
        "-to_pay")

    for diet in diets:
        diet.check_if_order_is_up_to_date()
        diet.save()

    return diets


class CartView(ListView):
    model = DietOrder
    template_name = "checkout/cart.html"
    context_object_name = "orders"

    def get_queryset(self) -> None:
        diets = check_dates_up_to_date(self.request)
        return diets

    def get_context_data(self, **kwargs) -> None:
        context = super().get_context_data(**kwargs)

        customer = get_customer_or_create(self.request)

        context['to_pay'] = DietOrder.objects.filter(customer=customer).filter(
            is_purchased=False).aggregate(
            Sum('to_pay'))
        context["title"] = "Cart"

        return context


class CheckoutView(UserPassesTestMixin, CreateView):
    model = OrderCheckout
    template_name = "checkout/checkout.html"

    def get_form_class(self):

        if self.request.user.is_authenticated:
            return LoggedUserOrderCheckoutForm

        return NotLoggedUserOrderCheckoutForm

    def get(self, *args, **kwargs) -> HttpResponse:
        customer = get_customer_or_create(self.request)
        instance = OrderCheckout.objects.filter(customer=customer).first()
        form = self.get_form_class()
        form = form(instance=instance)
        return render(self.request, "checkout/checkout.html", {"title": "Checkout",
                                                               "form": form})

    def form_valid(self, form) -> HttpResponse:
        checkout_order = form.save(commit=False)
        customer = get_customer_or_create(self.request)
        checkout_order.customer = customer
        email = form.instance.email
        self.set_order_checkout_to_pay(checkout_order)
        self.set_diet_order_confirmed_order(checkout_order)

        if not self.request.user.is_authenticated:
            customer.email = email
            customer.save()

        return self.check_payment_method(checkout_order)

    def check_payment_method(self, checkout_order):
        if checkout_order.payment_method == "Przelewy24":
            return self.checkout_przelewy24(checkout_order)

        return self.checkout_transfer(checkout_order)

    def checkout_przelewy24(self, checkout_order):
        """It won't work correctly because we don't have P24 account, it is just first step simulation"""

        object_przelewy24 = self.create_przelewy24_object(checkout_order)
        json_przelewy24 = RegistrationPrzelewy24Serializer(object_przelewy24)
        response = requests.post("https://secure.przelewy24.pl/api/v1/transaction/register",
                                 data=json_przelewy24.data).text
        subject = f"Order from {(checkout_order.date_of_purchase.strftime('%m/%d/%Y'))}"
        body = f"We have your order! Your payment was realised with Przelewy 24. Thank You!"
        email = EmailMessage(subject, body, to=[checkout_order.customer.email])
        email.send()
        self.set_diet_order_is_purchased_to_true()
        checkout_order.save()
        messages.success(self.request, "Diet is ordered!")
        return render(self.request, "checkout/api_view.html",
                      {"request": json_przelewy24.data, "response": {response}, "title":"API simulation"})

    def checkout_transfer(self, checkout_order):
        self.set_diet_order_is_purchased_to_true()
        checkout_order.save()
        subject = f"Order from {checkout_order.date_of_purchase.strftime('%m/%d/%Y')}"
        body = f"We have your order! Please make a transfer to {ACCOUNT_NUMBER} account. Thank You!"
        email = EmailMessage(subject, body, to=[checkout_order.customer.email])
        email.send()
        self.set_diet_order_is_purchased_to_true()
        checkout_order.save()
        messages.success(self.request, "Diet is ordered!")
        return reverse('cart')

    def create_przelewy24_object(self, checkout_order):
        registration_przelewy24 = RegistrationPrzelewy24.objects.create(
            amount=checkout_order.to_pay,
            description=(checkout_order.__str__()),
            email=checkout_order.customer.email,
            address=checkout_order.address + " " + checkout_order.address_info,
            zip=checkout_order.post_code,
            city=checkout_order.locality,
            phone=checkout_order.telephone,
            client=checkout_order.name + " " + checkout_order.surname,

        )
        return registration_przelewy24

    def form_invalid(self, form) -> HttpResponse:
        return render(self.request, "checkout/checkout.html",
                      {'form': form})

    def set_diet_order_confirmed_order(self, checkout_order) -> None:
        customer = get_customer_or_create(self.request)
        DietOrder.objects \
            .filter(customer=customer). \
            filter(is_purchased=False).filter(is_up_to_date=True).update(confirmed_order=checkout_order)

    def set_order_checkout_to_pay(self, order_confirmed_object) -> None:
        customer = get_customer_or_create(self.request)

        order_confirmed_object.to_pay = DietOrder.objects \
            .filter(customer=customer). \
            filter(is_purchased=False).aggregate(Sum('to_pay')).get('to_pay__sum')

        order_confirmed_object.save()

    def set_diet_order_is_purchased_to_true(self) -> None:
        customer = get_customer_or_create(self.request)

        DietOrder.objects.filter(customer=customer).filter(is_purchased=False).update(
            is_purchased=True)

    def test_func(self) -> bool:
        diets = check_dates_up_to_date(self.request)
        customer = get_customer_or_create(self.request)
        diets_out_of_date = DietOrder.objects.filter(customer=customer).filter(is_up_to_date=False)
        if diets_out_of_date:
            messages.warning(self.request, "Delete or change out of date orders")
            return False

        if not diets:
            messages.warning(self.request, "You don't have any orders to checkout")
            return False

        return True



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
        customer = get_customer_or_create(self.request)
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
                      {'form': self.form_class(), "api_key": GOOGLE_MAPS_API_KEY, "title": "Diet Order"})

    def get_success_url(self) -> HttpResponse:
        return reverse("cart")


class OrderUpdateView(UserPassesTestMixin, UpdateView, DietOrderView):
    model = DietOrder
    form_class = DietOrderForm
    template_name = "checkout/diet_order.html"

    def get(self, *args, **kwargs) -> HttpResponse:
        order = self.get_object()
        return render(self.request, "checkout/diet_order.html",
                      {'form': self.form_class(instance=self.get_object()), "api_key": GOOGLE_MAPS_API_KEY,
                       "title": f"Change {order.name}"})

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
                      {'form': self.form_class(self.request.POST), "api_key": GOOGLE_MAPS_API_KEY,
                       "title": "Order Change"})

    def test_func(self) -> bool:
        order = self.get_object()
        customer = get_customer(self.request)
        if not order.customer == customer:
            raise Http404("Page not found")
        return True

    def get_context_data(self, **kwargs) -> None:
        order = self.get_object()
        context = super().get_context_data(**kwargs)
        context["title"] = f"Change {order.name} "
        return context


class OrderDeleteView(DeleteView):
    model = DietOrder

    def get_success_url(self) -> HttpResponse:
        return reverse('cart')

    def test_func(self) -> bool:
        order = self.get_object()
        customer = get_customer(self.request)
        if not order.customer == customer:
            raise Http404("Page not found")
        return True

    def get_context_data(self, **kwargs) -> None:
        context = super().get_context_data(**kwargs)
        order = self.get_object()
        context["title"] = f"Delete {order.name}"
        return context


class MyOrdersHistory(ListView):
    model = OrderCheckout
    template_name = "checkout/orders_history.html"
    context_object_name = "checkouts"

    def get_queryset(self) -> Union[OrderCheckout, Exception]:
        if not self.request.user.is_authenticated:
            raise Http404("Page not found")

        return OrderCheckout.objects.filter(customer=self.request.user.customer).order_by("date_of_purchase")

    def get_context_data(self, **kwargs) -> None:
        context = super().get_context_data(**kwargs)
        context["title"] = f"{self.request.user} orders"
        return context


class MyOrdersHistoryDetail(DetailView):
    model = OrderCheckout
    context_object_name = "checkout"
    template_name = "checkout/detailed_orders_history.html"

    def test_func(self) -> Union[bool, Exception]:
        checkout = self.get_object()
        if self.request.user.is_authenticated:
            if self.request.user.customer == checkout.customer:
                return True

        raise Http404("Page not found")
