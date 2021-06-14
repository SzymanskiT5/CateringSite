from django import forms
from django.forms import ModelForm, SelectDateWidget

from shoppingcart.models import DietOrder

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
    # price_per_day=forms.FloatField(disabled=True)
    date_of_start = forms.DateField( widget=forms.SelectDateWidget())
    # user = forms.FloatField(disabled=True)
    # day_of_end = forms.DateField(disabled=True)

    class Meta:
        model = DietOrder
        fields = ["name","megabytes", "days","date_of_start" ]
