import json
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.db.models import Sum
from django.http import Http404
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import ListView, UpdateView, DeleteView, FormView, CreateView, DetailView
from django.views.generic.base import View
import users
from checkout.forms import OrderCheckout, DietOrderForm, OrderCheckoutForm
from checkout.google_api import GoogleApi
from checkout.models import DietOrder, PurchaserInfo
from djangoProject.settings import GOOGLE_MAPS_API_KEY, CATERING_PLACE_ID
from menu.models import Diet
from django.core.mail import send_mail

from users.models import Customer


class CartView(ListView):
    model = DietOrder
    template_name = "checkout/cart.html"
    context_object_name = "orders"

    def check_dates_up_to_date(self):
        try:
            diets = DietOrder.objects.filter(customer=self.request.user.customer).filter(is_purchased=False).order_by(
                "-to_pay")

        except:
            device = self.request.COOKIES.get("device")
            customer = Customer.objects.get_or_create(device=device)
            customer = customer[0]
            diets = DietOrder.objects.filter(customer=customer).filter(is_purchased=False).order_by(
                "-to_pay")

        for diet in diets:
            diet.check_if_order_is_up_to_date()
        return diets

    def get_queryset(self):
        diets = self.check_dates_up_to_date()
        return diets

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['to_pay'] = DietOrder.objects.filter(customer=self.request.user.customer).filter(
                is_purchased=False).aggregate(
                Sum('to_pay'))

        except:
            device = self.request.COOKIES.get("device")
            customer = Customer.objects.get_or_create(device=device)
            customer = customer[0]
            context['to_pay'] = DietOrder.objects.filter(customer=customer).filter(
                is_purchased=False).aggregate(
                Sum('to_pay'))

        return context


class CheckoutView(UserPassesTestMixin, CreateView):
    model = OrderCheckout
    template_name = "checkout/checkout.html"
    form_class = OrderCheckoutForm

    def check_if_user_authenticated_and_handle_email_field(self, form):
        if self.request.user.is_authenticated:
            del form.fields["email"]

    def get(self, *args, **kwargs):
        try:
            instance = OrderCheckout.objects.filter(customer=self.request.user.customer).first()

        except:
            device = self.request.COOKIES.get("device")
            instance = Customer.objects.get(device=device)

        form = self.form_class(instance=instance)
        self.check_if_user_authenticated_and_handle_email_field(form)

        return render(self.request, "checkout/checkout.html", {"title": "DjangoCatering-Checkout",
                                                               "form": form})

    def form_valid(self, form):
        checkout_order = form.save(commit=False)
        try:
            checkout_order.customer = self.request.user.customer
        except:
            device = self.request.COOKIES.get("device")
            customer_object = Customer.objects.get(device=device)
            customer_object.email = form.instance.email
            customer_object.save()
            checkout_order.customer = customer_object


        self.set_order_checkout_to_pay(checkout_order)
        self.set_diet_order_confirmed_order(checkout_order)
        self.set_diet_order_is_purchased_to_true()
        checkout_order.save()
        messages.success(self.request, "Diet is ordered!")
        return super().form_valid(form)

    def form_invalid(self, form):
        return render(self.request, "checkout/diet_order.html",
                      {'form': self.form_class(self.request.POST)})

    def get_success_url(self):
        return reverse('cart')

    def set_diet_order_confirmed_order(self, checkout_order):
        try:
            DietOrder.objects \
                .filter(customer=self.request.user.customer). \
                filter(is_purchased=False).filter(is_up_to_date=True).update(confirmed_order=checkout_order)
        except:
            device = self.request.COOKIES.get("device")
            customer = Customer.objects.get(device=device)

            DietOrder.objects \
                .filter(customer=customer) \
                .filter(is_purchased=False).filter(is_up_to_date=True).update(confirmed_order=checkout_order)

    def set_order_checkout_to_pay(self, order_confirmed_object):
        try:
            order_confirmed_object.to_pay = DietOrder.objects \
                .filter(customer=self.request.user.customer). \
                filter(is_purchased=False).aggregate(Sum('to_pay')).get('to_pay__sum')
            order_confirmed_object.save()
        except:
            device = self.request.COOKIES.get("device")
            customer = Customer.objects.get(device=device)
            order_confirmed_object.to_pay = DietOrder.objects \
                .filter(customer=customer). \
                filter(is_purchased=False).aggregate(Sum('to_pay')).get('to_pay__sum')
            order_confirmed_object.save()


    def set_diet_order_is_purchased_to_true(self):
        try:
            DietOrder.objects.filter(customer=self.request.user.customer).filter(is_purchased=False).update(
                is_purchased=True)

        except:
            device = self.request.COOKIES.get("device")
            customer = Customer.objects.get(device=device)
            DietOrder.objects.filter(customer=customer).filter(is_purchased=False).update(
                is_purchased=True)

    def test_func(self):
        diets = self.get_diets_and_check_up_to_date()

        try:
            diets_out_of_date = DietOrder.objects.filter(customer=self.request.user.customer).filter(
                is_up_to_date=False)
        except:
            device = self.request.COOKIES.get("device")
            customer = Customer.objects.get(device=device)
            diets_out_of_date = DietOrder.objects.filter(customer=customer).filter(
                is_up_to_date=False)

        if diets_out_of_date:
            messages.warning(self.request, "Delete or change out of date orders")
            return False

        if not diets:
            messages.warning(self.request, "You don't have any orders to checkout")
            return False

        return True

    def get_diets_and_check_up_to_date(self):
        try:
            diets = DietOrder.objects.filter(customer=self.request.user.customer).filter(is_purchased=False)
        except:
            device = self.request.COOKIES.get("device")
            customer = Customer.objects.get(device=device)
            diets = DietOrder.objects.filter(customer=customer).filter(is_purchased=False)

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

    def set_user_or_device_customer(self, order):
        try:
            order.customer = self.request.user.customer
        except:
            device = self.request.COOKIES.get("device")
            customer = Customer.objects.get_or_create(device=device)
            order.customer = customer[0]

    def handle_order_information(self, order):
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

    def form_invalid(self, form):
        return render(self.request, "checkout/diet_order.html",
                      {'form': self.form_class(self.request.POST), "api_key": GOOGLE_MAPS_API_KEY})

    def get(self, *args, **kwargs):
        return render(self.request, "checkout/diet_order.html",
                      {'form': self.form_class(), "api_key": GOOGLE_MAPS_API_KEY})

    def get_success_url(self):
        return reverse("cart")


class OrderUpdateView(UserPassesTestMixin, UpdateView, DietOrderView):
    model = DietOrder
    form_class = DietOrderForm
    template_name = "checkout/diet_order.html"

    def get(self, *args, **kwargs):
        return render(self.request, "checkout/diet_order.html",
                      {'form': self.form_class(instance=self.get_object()), "api_key": GOOGLE_MAPS_API_KEY})

    def form_valid(self, form):
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

    def test_func(self):
        order = self.get_object()

        try:
            self.request.user.customer == order.customer

        except AttributeError:
            device = self.request.COOKIES.get("device")

            try:
                Customer.objects.get(device=device)

            except:
                raise Http404("Page not found")

        return True


class OrderDeleteView(DeleteView):
    model = DietOrder

    def get_success_url(self):
        return reverse('cart')

    def test_func(self):
        order = self.get_object()

        try:
            self.request.user.customer == order.customer

        except AttributeError:
            device = self.request.COOKIES.get("device")

            try:
                Customer.objects.get(device=device)

            except:
                raise Http404("Page not found")

        return True
