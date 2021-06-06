from django.shortcuts import render
from django.views.generic import DetailView, ListView

from menu.models import Diet



class MenuListView(ListView):
    model=Diet
    template_name = "menu/offer.html"
    context_object_name = "diets"


class MenuDetailView(DetailView):
    model = Diet
