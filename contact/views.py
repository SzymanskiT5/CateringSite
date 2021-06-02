from django.http import HttpResponse
from django.shortcuts import render

def contact(request):

    html = "<html><body> CONTACT TEST </body></html>"
    return HttpResponse(html)
