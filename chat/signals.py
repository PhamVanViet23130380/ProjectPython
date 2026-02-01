from django.db.models.signals import post_save
from django.dispatch import receiver
from app.models import Booking
from chat.models import Conversation, Message


@receiver(post_save, sender=Booking)
def create_conversation_when_booking(sender, instance, created, **kwargs):
    """
    Tự động tạo Conversation khi Booking được tạo.
    Tự động gửi tin nhắn từ note khi booking_status chuyển sang 'confirmed'.
    """
    
    # Lấy hoặc tạo conversation cho booking này
    conversation, conv_created = Conversation.objects.get_or_create(
        booking=instance,
        defaults={
            'host': instance.listing.host,
            'guest': instance.user,
        }
    )
    
    # Nếu booking vừa được confirmed và có note
    if instance.booking_status == 'confirmed' and instance.note:
        # Kiểm tra xem đã gửi tin nhắn note này chưa (tránh gửi trùng)
        note_already_sent = Message.objects.filter(
            conversation=conversation,
            sender=instance.user,
            content=instance.note
        ).exists()
        
        if not note_already_sent:
            # Tạo tin nhắn tự động từ note của khách
            Message.objects.create(
                conversation=conversation,
                sender=instance.user,  # Người gửi là khách
                content=instance.note,
                is_read=False
            )
