from django.http import HttpResponse
from django.shortcuts import render


def home(request) -> HttpResponse:
    return render(request, "catering/home.html", {"title": "DjangoCatering"})


def about(request) -> HttpResponse:
    return render(request, "catering/about.html", {"title": "About"})
