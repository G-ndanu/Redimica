from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile  # Import the Profile model

# Signal to create or update profile after user is saved
@receiver(post_save, sender=User)
def create_or_update_profile(sender, instance, created, **kwargs):
    if created:  # Create a profile only if the user is new
        Profile.objects.create(user=instance, role='patient')  # Default to 'patient' for new users
    else:
        instance.profile.save()  # If the user is updated, save the profile as well
