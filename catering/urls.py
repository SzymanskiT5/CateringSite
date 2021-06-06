from django.urls import path
from . import views
from menu import views as menu_views
urlpatterns = [
    path('', views.home, name="catering-home"),
    path('about/', views.about, name="catering-about"),



]
