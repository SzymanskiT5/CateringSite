from django.urls import path
from .views import CartView, DietOrderView, OrderUpdateView, OrderDeleteView, CheckoutView, MyOrdersHistory

urlpatterns = [
    path("", CartView.as_view(), name="cart"),
    path('add_product/', DietOrderView.as_view(), name="add_product"),
    path("orders_history/", MyOrdersHistory.as_view(), name="orders_history"),
    path('update/<str:user>/<int:pk>/', OrderUpdateView.as_view(), name="order_update"),
    path('delete/<str:user>/<int:pk>/', OrderDeleteView.as_view(), name="order_delete"),
    path("checkout/", CheckoutView.as_view(), name="checkout"),




]