from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect

from django.views.generic import DetailView, ListView
from django.views.generic.base import View

from menu.models import Diet, DietExample
from .forms import DietOrderForm


class MenuListView(ListView):
    model = Diet
    template_name = "menu/offer.html"
    context_object_name = "diets"


class MenuDetailView(DetailView):
    model = Diet
    context_object_name = "diet"
    template_name = "menu/offer_details.html"
    pk_url_kwarg = "dietid"
    slug_url_kwarg = 'slug'
    query_pk_and_slug = True


class DietExampleDetail(DetailView):
    model = DietExample
    context_object_name = "dietexample"
    template_name = "menu/example_diet_table.html"


class DietOrderView(View):

    def get(self, request, *args, **kwargs):
        form = DietOrderForm()
        return render(request, "menu/diet_order.html", {"title": "DjangoCatering"})

    def post(self, request, *args, **kwargs):
        form = DietOrderForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f"Diet added to cart!")
            return redirect("offer_detail")

        messages.warning(request, "Fill correctly all fields!")
        return render(request, "contact/contact.html", {"title": "DjangoCatering"})
