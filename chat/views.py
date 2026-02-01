import json

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.db import transaction
from django.db.models import Count, Q, Max

from app.models import Booking, Listing
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
    booking = get_object_or_404(Booking, booking_id=booking_id)

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


@login_required
def get_unread_count(request):
    """Lấy tổng số tin nhắn chưa đọc của user hiện tại"""
    user = request.user
    
    # Đếm tin nhắn chưa đọc từ tất cả conversations mà user tham gia
    unread_count = Message.objects.filter(
        Q(conversation__host=user) | Q(conversation__guest=user),
        is_read=False
    ).exclude(sender=user).count()
    
    return JsonResponse({'unread_count': unread_count})


@login_required
def get_conversations(request):
    """Lấy danh sách conversations với số tin nhắn chưa đọc"""
    user = request.user
    
    # Lấy tất cả conversations mà user tham gia
    conversations = Conversation.objects.filter(
        Q(host=user) | Q(guest=user)
    ).select_related('host', 'guest', 'booking', 'booking__listing').annotate(
        unread_count=Count(
            'messages',
            filter=Q(messages__is_read=False) & ~Q(messages__sender=user)
        ),
        last_message_time=Max('messages__created_at')
    ).order_by('-last_message_time')
    
    data = []
    for conv in conversations:
        # Xác định người chat cùng
        other_user = conv.guest if conv.host == user else conv.host
        
        # Lấy tin nhắn cuối cùng
        last_msg = conv.messages.order_by('-created_at').first()
        
        # Xác định listing title
        if conv.booking:
            listing_title = conv.booking.listing.title
        else:
            listing_title = 'Hỏi đáp'
        
        data.append({
            'id': conv.id,
            'other_user_name': other_user.full_name or other_user.username,
            'other_user_avatar': other_user.avatar.url if other_user.avatar else None,
            'listing_title': listing_title,
            'unread_count': conv.unread_count,
            'last_message': last_msg.content[:50] if last_msg else '',
            'last_message_time': last_msg.created_at.isoformat() if last_msg else None,
        })
    
    return JsonResponse({'conversations': data})


@login_required
def open_chat_for_listing(request, listing_id):
    """Mở chat trực tiếp với host của một listing (không cần booking)"""
    listing = get_object_or_404(Listing, listing_id=listing_id)
    
    # Không cho phép host tự chat với chính mình
    if request.user == listing.host:
        return JsonResponse({'error': 'Bạn không thể nhắn tin cho chính mình'}, status=400)
    
    with transaction.atomic():
        # Tìm conversation bất kỳ giữa guest và host này (ưu tiên conversation có tin nhắn gần nhất)
        conversation = Conversation.objects.filter(
            host=listing.host,
            guest=request.user
        ).order_by('-created_at').first()
        
        # Nếu chưa có conversation nào, tạo mới
        if not conversation:
            conversation = Conversation.objects.create(
                host=listing.host,
                guest=request.user,
                booking=None
            )
    
    return JsonResponse({
        'conversation_id': conversation.id,
        'other_user_name': listing.host.full_name or listing.host.username
    })
