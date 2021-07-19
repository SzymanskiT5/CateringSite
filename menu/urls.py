from django.urls import path
from menu.views import MenuDetailView, MenuListView

urlpatterns = [
    path('', MenuListView.as_view(), name="offer"),
    path("<slug:dietname>/", MenuDetailView.as_view(), name="offer_detail"),

]
