from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile
from PIL import Image
import os

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=Profile)
def save_profile(sender, instance, **kwargs):
    if instance.image and os.path.exists(instance.image.path):
        try:
            img = Image.open(instance.image.path)
            # Your image processing logic here
            img.save(instance.image.path)
        except Exception as e:
            print(f"Error processing image: {e}")