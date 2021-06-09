from PIL import Image
from django.db import models
from django.urls import reverse


class Diet(models.Model):
    name = models.CharField(max_length=30)
    image = models.ImageField(upload_to='diet_images')
    description = models.TextField()

    # calories = models.IntegerField()

    def __str__(self):
        return self.name

    def save(self):
        super().save()

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
    diet = models.ForeignKey(Diet, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.diet} Example"
