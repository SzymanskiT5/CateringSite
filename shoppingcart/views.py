from django.shortcuts import render

def cart(request):
    return render(request, template_name="shoppingcart/shop.html")
