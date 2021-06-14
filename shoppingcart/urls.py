from django.urls import path
from .views import cart, DietOrderView

urlpatterns = [
    path("", cart, name="cart"),
    path("add_product/", DietOrderView.as_view(), name="add_product")

]