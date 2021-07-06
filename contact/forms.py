from django import forms
from .models import Contact



class ContactForm(forms.ModelForm):
    email = forms.EmailInput()

    class Meta:
        model = Contact
        fields = ["email", "subject", "message"]

