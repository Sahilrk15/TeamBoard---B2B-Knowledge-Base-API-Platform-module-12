import secrets

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from api.models import Company


@receiver(post_save, sender=User)
def create_company_profile(sender, instance, created, **kwargs):
    # `created` is True only on the initial INSERT, so this fires once
    # per new User and never again on later saves/updates.
    if created:
        Company.objects.create(
            user=instance,
            company_name=instance.email,  # placeholder, overwritten by the register view
            api_key=secrets.token_urlsafe(32)
        )
