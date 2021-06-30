import datetime

from django import forms
from django.utils import timezone

from checkout.models import DietOrder, PurchaserInfo, OrderConfirmed

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


class DateInput(forms.DateInput):
    input_type = 'date'


class DietOrderForm(forms.ModelForm):
    MEGABYTES_CHOICE = (
        ("1000", 1000),
        ("1500", 1500),
        ("2000", 2000),
        ("2500", 2500),
        ("3000", 3000),
        ("3500", 3500),
    )

    megabytes = forms.ChoiceField(choices=MEGABYTES_CHOICE)

    class Meta:
        model = DietOrder

        fields = ["name", "megabytes", "date_of_start", "date_of_end", "address", "address_info", "locality", "state",
                  "post_code"]
        widgets = {
            'date_of_start': DateInput(),
            'date_of_end': DateInput(),
        }



    def clean(self):
        super().clean()
        date_of_start = self.cleaned_data.get("date_of_start")

        if date_of_start < timezone.now().date():
            self._errors['date_of_start'] = self.error_class([
                'Date cannot be from past!'])

        elif date_of_start - timezone.now().date() <= datetime.timedelta(days=3):
            self._errors['date_of_start'] = self.error_class([
                'Date must starts in 3 days ahead!'])




        return self.cleaned_data