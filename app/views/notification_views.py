from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from app.models import Notification


@login_required
def notification_list(request):
    """Hiển thị tất cả thông báo của user"""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:50]
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    
    return render(request, 'app/notifications/list.html', {
        'notifications': notifications,
        'unread_count': unread_count,
    })


@login_required
def notification_api(request):
    """API lấy thông báo cho dropdown"""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:10]
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    
    data = {
        'unread_count': unread_count,
        'notifications': [
            {
                'id': n.id,
                'type': n.notification_type,
                'title': n.title,
                'message': n.message[:100] + '...' if len(n.message) > 100 else n.message,
                'is_read': n.is_read,
                'created_at': n.created_at.strftime('%d/%m/%Y %H:%M'),
                'listing_id': n.listing_id,
                'booking_id': n.booking_id,
            }
            for n in notifications
        ]
    }
    
    return JsonResponse(data)


@login_required
@require_POST
def mark_as_read(request, notification_id):
    """Đánh dấu thông báo đã đọc"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save(update_fields=['is_read'])
    
    return JsonResponse({'success': True})


@login_required
@require_POST
def mark_all_as_read(request):
    """Đánh dấu tất cả thông báo đã đọc"""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    
    return JsonResponse({'success': True})


# --- HELPER FUNCTIONS để tạo thông báo ---

def create_notification(user, notification_type, title, message, listing=None, booking=None):
    """Helper function để tạo thông báo mới"""
    return Notification.objects.create(
        user=user,
        notification_type=notification_type,
        title=title,
        message=message,
        listing=listing,
        booking=booking,
    )


def notify_listing_approved(listing):
    """Thông báo khi chỗ ở được admin duyệt"""
    create_notification(
        user=listing.host,
        notification_type='listing_approved',
        title='🎉 Chỗ ở đã được duyệt!',
        message=f'Chỗ ở "{listing.title}" của bạn đã được admin phê duyệt và đang hiển thị trên hệ thống. Chúc bạn đón nhiều khách!',
        listing=listing,
    )


def notify_listing_rejected(listing, reason=''):
    """Thông báo khi chỗ ở bị từ chối"""
    msg = f'Chỗ ở "{listing.title}" của bạn chưa được duyệt.'
    if reason:
        msg += f' Lý do: {reason}'
    
    create_notification(
        user=listing.host,
        notification_type='listing_rejected',
        title='❌ Chỗ ở chưa được duyệt',
        message=msg,
        listing=listing,
    )


def notify_new_booking(booking):
    """Thông báo cho host khi có khách đặt phòng mới"""
    create_notification(
        user=booking.listing.host,
        notification_type='new_booking',
        title='📦 Có đặt phòng mới!',
        message=f'Khách {booking.user.full_name or booking.user.email} đã đặt phòng "{booking.listing.title}" từ {booking.check_in.strftime("%d/%m/%Y")} đến {booking.check_out.strftime("%d/%m/%Y")}.',
        listing=booking.listing,
        booking=booking,
    )


def notify_booking_confirmed(booking):
    """Thông báo khi booking được xác nhận"""
    # Thông báo cho khách
    create_notification(
        user=booking.user,
        notification_type='booking_confirmed',
        title='✅ Đặt phòng đã được xác nhận!',
        message=f'Đặt phòng "{booking.listing.title}" của bạn đã được xác nhận. Ngày nhận phòng: {booking.check_in.strftime("%d/%m/%Y")}.',
        listing=booking.listing,
        booking=booking,
    )
    
    # Thông báo cho host
    create_notification(
        user=booking.listing.host,
        notification_type='booking_confirmed',
        title='✅ Đã xác nhận đặt phòng',
        message=f'Bạn đã xác nhận đặt phòng của khách {booking.user.full_name or booking.user.email} cho "{booking.listing.title}".',
        listing=booking.listing,
        booking=booking,
    )


def notify_booking_cancelled(booking, cancelled_by='guest'):
    """Thông báo khi booking bị hủy"""
    if cancelled_by == 'guest':
        # Thông báo cho host
        create_notification(
            user=booking.listing.host,
            notification_type='booking_cancelled',
            title='❌ Khách đã hủy đặt phòng',
            message=f'Khách {booking.user.full_name or booking.user.email} đã hủy đặt phòng "{booking.listing.title}" ({booking.check_in.strftime("%d/%m/%Y")} - {booking.check_out.strftime("%d/%m/%Y")}).',
            listing=booking.listing,
            booking=booking,
        )
    else:
        # Thông báo cho khách
        create_notification(
            user=booking.user,
            notification_type='booking_cancelled',
            title='❌ Đặt phòng đã bị hủy',
            message=f'Đặt phòng "{booking.listing.title}" của bạn đã bị hủy bởi chủ nhà.',
            listing=booking.listing,
            booking=booking,
        )


def notify_guest_checkin(booking):
    """Thông báo khi khách nhận phòng"""
    create_notification(
        user=booking.listing.host,
        notification_type='guest_checkin',
        title='🏠 Khách đã nhận phòng',
        message=f'Khách {booking.user.full_name or booking.user.email} đã nhận phòng "{booking.listing.title}". Ngày trả phòng: {booking.check_out.strftime("%d/%m/%Y")}.',
        listing=booking.listing,
        booking=booking,
    )


def notify_guest_checkout(booking):
    """Thông báo khi khách trả phòng"""
    create_notification(
        user=booking.listing.host,
        notification_type='guest_checkout',
        title='👋 Khách đã trả phòng',
        message=f'Khách {booking.user.full_name or booking.user.email} đã trả phòng "{booking.listing.title}".',
        listing=booking.listing,
        booking=booking,
    )


def notify_booking_completed(booking):
    """Thông báo khi hoàn thành lượt thuê"""
    # Thông báo cho host
    create_notification(
        user=booking.listing.host,
        notification_type='booking_completed',
        title='🎊 Hoàn thành lượt thuê!',
        message=f'Lượt thuê phòng "{booking.listing.title}" bởi khách {booking.user.full_name or booking.user.email} đã hoàn thành. Cảm ơn bạn đã sử dụng dịch vụ!',
        listing=booking.listing,
        booking=booking,
    )
    
    # Thông báo cho khách
    create_notification(
        user=booking.user,
        notification_type='booking_completed',
        title='🎊 Chuyến đi hoàn thành!',
        message=f'Chuyến đi tại "{booking.listing.title}" của bạn đã hoàn thành. Hãy để lại đánh giá cho chủ nhà nhé!',
        listing=booking.listing,
        booking=booking,
    )


def notify_payment_received(booking, amount):
    """Thông báo khi host nhận thanh toán"""
    create_notification(
        user=booking.listing.host,
        notification_type='payment_received',
        title='💰 Nhận thanh toán',
        message=f'Bạn đã nhận thanh toán {int(amount):,}đ từ đặt phòng "{booking.listing.title}".'.replace(',', '.'),
        listing=booking.listing,
        booking=booking,
    )


def notify_review_received(review):
    """Thông báo khi host nhận đánh giá mới"""
    create_notification(
        user=review.listing.host,
        notification_type='review_received',
        title='⭐ Đánh giá mới',
        message=f'Khách {review.user.full_name or review.user.email} đã đánh giá {review.rating} sao cho "{review.listing.title}": "{review.comment[:50]}..."' if len(review.comment) > 50 else f'Khách {review.user.full_name or review.user.email} đã đánh giá {review.rating} sao cho "{review.listing.title}": "{review.comment}"',
        listing=review.listing,
    )
