from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import UserProfile
from .utils import ensure_default_badges


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    ensure_default_badges()
    if created:
        UserProfile.objects.get_or_create(user=instance)
