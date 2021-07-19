from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import FormView

from .forms import ContactForm
from .models import Contact


class ContactView(FormView):
    form_class = ContactForm
    model = Contact
    def get(self, request, *args, **kwargs) -> HttpResponse:
        return render(request, "contact/contact.html", {"title": "Contact"})

    def form_valid(self, form) -> HttpResponse:
        form.save()
        messages.success(self.request, f"Thank you. We will response as soon as possible!")
        return super().form_valid(form)

    def form_invalid(self, form) -> HttpResponse:
        return render(self.request, "contact/contact.html",
                      {'form': self.form_class(self.request.POST), "title": "DjangoCatering-Contact"})

    def get_success_url(self) -> str:
        return reverse("contact")


