from django.db import models
from django.utils import timezone


class Contact(models.Model):
    email = models.EmailField()
    subject = models.CharField(max_length=30)
    message = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return self.subject
