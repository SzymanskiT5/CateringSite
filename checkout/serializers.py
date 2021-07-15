from .models import RegistrationPrzelewy24
from rest_framework import serializers


class RegistrationPrzelewy24Serializer(serializers.ModelSerializer):
    class Meta:
        model = RegistrationPrzelewy24
        fields = '__all__'
