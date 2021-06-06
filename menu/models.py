from PIL import Image
from django.db import models

class Diet(models.Model):
    name = models.CharField(max_length=30)
    image = models.ImageField(upload_to='profile_pics')
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
