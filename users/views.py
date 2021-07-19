from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect

from django.views.generic.base import View
from users.forms import UserRegisterForm, MyPasswordResetForm
from django.contrib.auth.views import LogoutView, PasswordResetView

class RegisterView(View):

    def post(self, request, *args, **kwargs) -> HttpResponse:
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f"Now you can log in!")
            return redirect("login")

        return render(request, "users/register.html", {"form": form})

    def get(self, request, *args, **kwargs) -> HttpResponse:
        if request.user.is_authenticated:
            return redirect("/")
        form = UserRegisterForm
        return render(request, "users/register.html", {"form": form, "title":"Register"})


class MyLogoutView(LogoutView):

    def get_next_page(self) -> HttpResponse:
        next_page = super(MyLogoutView, self).get_next_page()
        messages.add_message(
            self.request, messages.SUCCESS,
            'You are logged out!'
        )
        return next_page


class MyPasswordResetView(PasswordResetView):
    form_class = MyPasswordResetForm



