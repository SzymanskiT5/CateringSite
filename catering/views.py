from django.shortcuts import render

def home(request):

    return render(request, "catering/home.html", {"title":"DjangoCatering"})



def about(request):
    return render(request, "catering/about.html", {"title": "About"})
