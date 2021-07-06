from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import View, FormView

from .forms import ContactForm
from .models import Contact


class ContactView(FormView):
    form_class = ContactForm
    model = Contact



    def get(self, request, *args, **kwargs):
        return render(request, "contact/contact.html", {"title": "DjangoCatering-Contact"})

    def form_valid(self, form):
        form.save()
        messages.success(self.request, f"Thank you. We will response as soon as possible!")
        return super().form_valid(form)


    def form_invalid(self, form):
        return render(self.request, "contact/contact.html",
                      {'form': self.form_class(self.request.POST), "title": "DjangoCatering-Contact"})

    def get_success_url(self):
        return reverse("contact")


