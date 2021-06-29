from django import forms
from django.forms import ModelForm, SelectDateWidget

from checkout.models import DietOrder, PurchaserInfo, OrderConfirmed

MEGABYTES_CHOICE = (
    ("1000", 1000),
    ("1500", 1500),
    ("2000", 2000),
    ("2500", 2500),
    ("3000", 3000),
    ("3500", 3500),
)


class DietOrderForm(forms.ModelForm, SelectDateWidget):
    megabytes = forms.ChoiceField(choices=MEGABYTES_CHOICE)
    days = forms.IntegerField(min_value=1)
    date_of_start = forms.DateTimeField(widget=forms.SelectDateWidget())

    class Meta:
        model = DietOrder
        fields = ["name", "megabytes", "days", "date_of_start", "address", "address_info", "locality", "state",
                  "post_code"]


class PurchaserInfoForm(forms.ModelForm):
    telephone = forms.NumberInput()

    class Meta:
        model = PurchaserInfo
        fields = ["surname", "name", "telephone", "address", "address_info", "locality", "state", "post_code"]


class OrderConfirmedForm(forms.ModelForm):
    PAYMENT_CHOICE = (
        ("Przelewy24", "Przelewy24"),
        ("Transfer", "Transfer"),
    )
    payment_method = forms.ChoiceField(choices=PAYMENT_CHOICE)

    class Meta:
        model = OrderConfirmed
        fields = ["payment_method"]
