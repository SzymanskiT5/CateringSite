import datetime
from django import forms
from django.contrib.auth.models import User
from django.utils import timezone
from checkout.models import DietOrder, OrderCheckout
import re
from djangoProject.settings import POLISH_POST_CODE_REGEX, HOLIDAYS_POLAND


class NotLoggedUserOrderCheckoutForm(forms.ModelForm):
    PAYMENT_CHOICE = (
        ("Przelewy24", "Przelewy24"),
        ("Transfer", "Transfer"),
    )
    payment_method = forms.ChoiceField(choices=PAYMENT_CHOICE)
    telephone = forms.NumberInput()
    email = forms.EmailField()

    def clean(self) -> dict:
        super().clean()
        post_code = self.cleaned_data.get("post_code")
        email = self.cleaned_data.get("email")
        if not re.match(POLISH_POST_CODE_REGEX, post_code):
            self._errors["post_code"] = self.error_class(["Invalid postcode format"])

        user = User.objects.filter(email=email)
        if user:
            self._errors["email"] = self.error_class(["There is logged user with this email, please log in"])

        return self.cleaned_data

    class Meta:
        model = OrderCheckout

        fields = ["email", "surname", "name", "telephone", "address", "address_info", "locality", "state", "post_code",
                  "payment_method", "note"]


class LoggedUserOrderCheckoutForm(forms.ModelForm):
    PAYMENT_CHOICE = (
        ("Przelewy24", "Przelewy24"),
        ("Transfer", "Transfer"),
    )
    payment_method = forms.ChoiceField(choices=PAYMENT_CHOICE)
    telephone = forms.NumberInput()

    def clean(self) -> dict:
        super().clean()
        post_code = self.cleaned_data.get("post_code")
        if not re.match(POLISH_POST_CODE_REGEX, post_code):
            self._errors["post_code"] = self.error_class(["Invalid postcode format"])
        return self.cleaned_data

    class Meta:
        model = OrderCheckout

        fields = ["surname", "name", "telephone", "address", "address_info", "locality", "state", "post_code",
                  "payment_method", "note"]


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
    def validate_dates(self):

        date_of_start = self.cleaned_data.get("date_of_start")
        date_of_end = self.cleaned_data.get("date_of_end")
        if date_of_start < timezone.now().date() or date_of_start - timezone.now().date() <= datetime.timedelta(days=3):
            self._errors['date_of_start'] = self.error_class([
                'Date cannot be from past!\n'
                'Date must starts in 3 days ahead!'])

        if date_of_start in HOLIDAYS_POLAND or date_of_start.weekday() in range(5, 7):

            while date_of_start in HOLIDAYS_POLAND or date_of_start.weekday() in range(5, 7):
                date_of_start = date_of_start + datetime.timedelta(days=1)

            self._errors['date_of_start'] = self.error_class([
                f"It's holiday day or weekend, the closest termin is {date_of_start} "])

        if date_of_end in HOLIDAYS_POLAND or date_of_start.weekday() in range(5, 7):
            while date_of_end in HOLIDAYS_POLAND or date_of_start.weekday() in range(5, 7):
                date_of_end = date_of_end + datetime.timedelta(days=1)

            self._errors['date_of_end'] = self.error_class([
                f"It's holiday day, the closest termin is {date_of_end} "])

        if date_of_end < date_of_start:
            self._errors["date_of_end"] = self.error_class(["End of diet cannot be earlier than start"])



    def validate_post_code(self):
        post_code = self.cleaned_data.get("post_code")
        if not re.match(POLISH_POST_CODE_REGEX, post_code):
            self._errors["post_code"] = self.error_class(["Invalid postcode format"])

    def clean(self) -> dict:
        super().clean()
        self.validate_dates()
        self.validate_post_code()
        return self.cleaned_data

    class Meta:
        model = DietOrder

        fields = ["name", "megabytes", "date_of_start", "date_of_end", "address", "address_info", "locality", "state",
                  "post_code"]
        widgets = {
            'date_of_start': DateInput(),
            'date_of_end': DateInput(),
        }
