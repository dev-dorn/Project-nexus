from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, UserActivity

@receiver(post_save, sender=User)
def create_user_activity(sender, instance, created, **kwargs):
    if created:
        UserActivity.objects.create(
            user=instance,
            activity_type='account_created',
            description='User account was created'
        )