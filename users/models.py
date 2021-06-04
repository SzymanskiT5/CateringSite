from django.utils import timezone

from django.db import models

class Contact(models.Model):

    email = models.EmailField()
    subject = models.CharField(max_length=30)
    message = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)

