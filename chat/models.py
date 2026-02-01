from django.db import models
from django.conf import settings

class Conversation(models.Model):
    host = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="host_conversations"
    )
    guest = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="guest_conversations"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Đảm bảo mỗi cặp host-guest chỉ có 1 conversation
        unique_together = ('host', 'guest')


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
