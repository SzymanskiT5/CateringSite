from django.contrib import admin
from checkout.models import DietOrder, PurchaserInfo, OrderCheckout

admin.site.register(DietOrder)
admin.site.register(PurchaserInfo)
admin.site.register(OrderCheckout)

