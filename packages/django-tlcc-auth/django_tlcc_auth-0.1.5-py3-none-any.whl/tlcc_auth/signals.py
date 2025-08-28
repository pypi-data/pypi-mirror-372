from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserProfile

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance, created, **kwargs): #userprofile maken bij user aanmaken
    if created:
        UserProfile.objects.get_or_create(user=instance)
