from PIL import Image
from django.db import models
from django.utils.text import slugify


class Diet(models.Model):
    name = models.CharField(max_length=30)
    image = models.ImageField(upload_to='diet_images')
    description = models.TextField()
    price = models.FloatField(default=0)
    slug = models.SlugField()

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)

        super().save(*args, **kwargs)



class DietExample(models.Model):
    first_dish = models.TextField()
    second_dish = models.TextField()
    third_dish = models.TextField()
    fourth_dish = models.TextField()
    fifth_dish = models.TextField()
    diet = models.ForeignKey(Diet, on_delete=models.PROTECT)

    def __str__(self) -> str:
        return f"{self.diet} Example"




