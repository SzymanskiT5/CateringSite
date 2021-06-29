from django.urls import path, include

from menu.views import MenuDetailView, MenuListView

urlpatterns = [
    path('', MenuListView.as_view(), name="offer"),
    path("<slug:dietname>/", MenuDetailView.as_view(), name="offer_detail"),
    # path("test/", DietOrderView.as_view(), name="test")
]
