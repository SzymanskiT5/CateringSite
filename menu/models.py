import django
from PIL import Image
from django.contrib.auth import get_user_model
from django.db import models
from django.http import request
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User


class Diet(models.Model):
    name = models.CharField(max_length=30)
    image = models.ImageField(upload_to='diet_images')
    description = models.TextField()
    price = models.FloatField(default=0)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(args, kwargs)

        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)


class DietExample(models.Model):
    first_dish = models.TextField()
    second_dish = models.TextField()
    third_dish = models.TextField()
    fourth_dish = models.TextField()
    fifth_dish = models.TextField()
    diet = models.ForeignKey(Diet, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.diet} Example"

