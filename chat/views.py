import json

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.db import transaction

from app.models import Booking
from .models import Conversation, Message


@login_required
def get_messages(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)

    # Chặn người lạ
    if request.user not in [conversation.host, conversation.guest]:
        return JsonResponse({'error': 'Forbidden'}, status=403)

    messages = (
        Message.objects
        .filter(conversation=conversation)
        .select_related('sender')
        .order_by('created_at')
    )

    # Mark read các tin của người kia
    Message.objects.filter(
        conversation=conversation
    ).exclude(sender=request.user).update(is_read=True)

    data = [
        {
            'id': msg.id,
            'sender': msg.sender.username,
            'content': msg.content,
            'created_at': msg.created_at.isoformat(),
            'is_me': msg.sender == request.user
        }
        for msg in messages
    ]

    return JsonResponse({'messages': data})



@login_required
@csrf_exempt
@require_POST
def send_message(request):
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    conversation_id = body.get('conversation_id')
    content = body.get('content', '').strip()

    if not conversation_id or not content:
        return JsonResponse({'error': 'Missing data'}, status=400)

    conversation = get_object_or_404(Conversation, id=conversation_id)

    if request.user not in [conversation.host, conversation.guest]:
        return JsonResponse({'error': 'Forbidden'}, status=403)

    msg = Message.objects.create(
        conversation=conversation,
        sender=request.user,
        content=content
    )

    return JsonResponse({
        'id': msg.id,
        'sender': msg.sender.username,
        'content': msg.content,
        'created_at': msg.created_at.isoformat(),
        'is_me': True
    })



@login_required
def open_chat_for_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    # Chỉ host hoặc guest mới được chat
    if request.user not in [booking.user, booking.listing.host]:
        return JsonResponse({'error': 'Forbidden'}, status=403)

    # Tạo conversation an toàn (chống tạo trùng)
    with transaction.atomic():
        conversation, created = Conversation.objects.get_or_create(
            booking=booking,
            defaults={
                'host': booking.listing.host,
                'guest': booking.user
            }
        )

    # Xác định người bên kia để frontend hiển thị
    other_user = (
        booking.listing.host
        if request.user == booking.user
        else booking.user
    )

    return JsonResponse({
        'conversation_id': conversation.id,
        'other_user_name': other_user.full_name or other_user.username
    })
