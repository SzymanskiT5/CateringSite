from django.http import HttpResponse
from django.shortcuts import render

def contact(request):
    return render(request, "contact/contact.html", {"title": "DjangoCatering"})
