"""Patient signals."""

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Patient


@receiver(post_save, sender=Patient)
def send_patient_email(sender, instance, created, **kwargs):
    """Send patient invite via email."""
    # if created and not (
    #     Invite.objects.filter(email__iexact=instance.email, patient=instance)
    #     .order_by("created_at")
    #     .last()
    # ):
    #     invitation = Invite.create(email=instance.email, patient=instance)
    #
    #     request = HttpRequest()
    #     request.META["HTTP_HOST"] = "localhost:3000"  # Replace with domain if available
    #     request.META["SERVER_NAME"] = "localhost"
    #     request.META["SERVER_PORT"] = "3000"
    #     invitation.send_invitation(
    #         request, first_name=instance.first_name, last_name=instance.last_name
    #     )
