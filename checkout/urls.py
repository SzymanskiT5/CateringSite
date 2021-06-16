from django.urls import path
from .views import CartView, DietOrderView

urlpatterns = [
    path("", CartView.as_view(), name="cart"),
    path("add_product/", DietOrderView.as_view(), name="add_product")

]