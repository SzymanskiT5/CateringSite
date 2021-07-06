from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic.base import View
from users.forms import UserRegisterForm
from django.contrib.auth.views import LogoutView

# from users.models import Customer


class RegisterView(View):

    def post(self, request, *args, **kwargs):
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f"Now you can log in!")
            return redirect("login")

        return render(request, "users/register.html", {"form": form})

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("/")
        form = UserRegisterForm
        return render(request, "users/register.html", {"form": form})


class MyLogoutView(LogoutView):

    def get_next_page(self):
        next_page = super(MyLogoutView, self).get_next_page()
        messages.add_message(
            self.request, messages.SUCCESS,
            'You are logged out!'
        )
        return next_page
