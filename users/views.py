from django.contrib import messages
from django.shortcuts import render, redirect
from users.forms import UserRegisterForm

from django.contrib.auth.views import LogoutView
def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f"Now you can log in!")
            return redirect("login")

    else:
        form = UserRegisterForm(request.POST)
        return render(request, "users/register.html", {"form": form})




class MyLogoutView(LogoutView):

    def get_next_page(self):
        next_page = super(MyLogoutView, self).get_next_page()
        messages.add_message(
            self.request, messages.SUCCESS,
            'You are logged out!'
        )
        return next_page