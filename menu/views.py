from django.views.generic import DetailView, ListView
from menu.models import Diet, DietExample


class MenuListView(ListView):
    model = Diet
    template_name = "menu/offer.html"
    context_object_name = "diets"


class MenuDetailView(DetailView):
    model = Diet
    context_object_name = "diet"
    template_name = "menu/offer_details.html"
    slug_url_kwarg = 'dietname'
    slug_field = 'slug'


class DietExampleDetail(DetailView):
    model = DietExample
    context_object_name = "dietexample"
    template_name = "menu/example_diet_table.html"

