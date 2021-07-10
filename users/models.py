from django.contrib.auth.models import User
from django.utils import timezone

from django.db import models


class Customer(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.PROTECT)
    email = models.CharField(max_length=200, null=True, blank=True)
    device = models.CharField(max_length=200, null=True, blank=True)




    def __str__(self) -> str:
        if self.user:
            name = self.user.username
        else:
            name = self.device
        return str(name)



