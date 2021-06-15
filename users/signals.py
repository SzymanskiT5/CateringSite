from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from shoppingcart.models import Cart


@receiver(post_save, sender=User)
def create_cart(sender, instance, created, **kwargs):
    if created:
        Cart.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_cart(sender, instance, created, **kwargs):
    instance.cart.save()