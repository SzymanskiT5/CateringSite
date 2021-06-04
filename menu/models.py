from django.db import models

class Diet(models.Model):
    name = models.CharField(30)
    image = models.ImageField(upload_to='profile_pics')
    description = models.TextField()
    calories = models.IntegerField()

    def __str__(self):
        return self.name