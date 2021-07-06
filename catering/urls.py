from django.urls import path
from . import views
urlpatterns = [
    path('', views.home, name="catering-home"),
    path('about/', views.about, name="catering-about"),



]
