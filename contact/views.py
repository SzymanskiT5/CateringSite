from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.generic import View

from .forms import ContactForm


class ContactView(View):

    def get(self, request, *args, **kwargs):
        return render(request, "contact/contact.html", {"title": "DjangoCatering-Contact"})

    def post(self, request, *args, **kwargs):
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f"Thank you. We will response as soon as possible!")
            return redirect("catering-contact")

        messages.warning(request, "Fill correctly all fields!")
        return render(request, "contact/contact.html", {"title": "DjangoCatering-Contact"})

