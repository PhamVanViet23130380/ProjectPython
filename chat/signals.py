from django.db.models.signals import post_save
from django.dispatch import receiver
from app.models import Booking
from chat.models import Conversation

@receiver(post_save, sender=Booking)
def create_conversation_when_booking(sender, instance, created, **kwargs):
    if not created:
        return

    Conversation.objects.get_or_create(
        booking=instance,                 # 🔥 QUAN TRỌNG
        host=instance.listing.host,
        guest=instance.user,
    )
