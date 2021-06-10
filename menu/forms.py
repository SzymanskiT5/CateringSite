from django import forms
from .models import DietOrder

MEGABYTES_CHOICE = (
    ("1", 1000),
    ("2", 1500),
    ("3", 2000),
    ("4", 2500),
    ("5", 3000),
    ("5", 3500),
)


class DietOrderForm(forms.ModelForm):
    megabytes = forms.ChoiceField(choices=MEGABYTES_CHOICE)
    date_of_start = forms.DateTimeField()
    days = forms.IntegerField

    class Meta:
        model = DietOrder
        fields = ["megabytes", ]
