from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from app.models import Booking


@login_required
@never_cache
def user_booking_history(request):
    """Hiển thị lịch sử đặt phòng của user."""
    # Lấy tham số lọc từ query string (mặc định là 'active')
    filter_type = request.GET.get('filter', 'active')
    
    # Đếm số lượng booking theo từng loại
    total_bookings = Booking.objects.filter(user=request.user).count()
    cancelled_bookings = Booking.objects.filter(user=request.user, booking_status='cancelled').count()
    active_bookings = Booking.objects.filter(user=request.user).exclude(booking_status='cancelled').count()
    
    # Lấy booking của user dựa theo bộ lọc
    if filter_type == 'cancelled':
        # Chỉ hiển thị booking đã hủy
        bookings = Booking.objects.filter(
            user=request.user,
            booking_status='cancelled'
        ).select_related('listing').order_by('-created_at')
    elif filter_type == 'all':
        # Hiển thị tất cả
        bookings = Booking.objects.filter(user=request.user).select_related('listing').order_by('-created_at')
    else:
        # Mặc định: chỉ hiển thị booking đang hoạt động (chưa hủy)
        bookings = Booking.objects.filter(
            user=request.user
        ).exclude(
            booking_status='cancelled'
        ).select_related('listing').order_by('-created_at')
    
    # Tính số đêm cho mỗi booking
    for booking in bookings:
        booking.nights = (booking.check_out - booking.check_in).days
        
        # Lấy ảnh chính của listing
        main_image = booking.listing.images.filter(is_main=True).first()
        if not main_image:
            main_image = booking.listing.images.first()
        booking.listing.main_image = main_image.image_url if main_image else ''
    
    context = {
        'bookings': bookings,
        'filter_type': filter_type,
        'total_bookings': total_bookings,
        'cancelled_count': cancelled_bookings,
        'active_count': active_bookings,
    }
    
    return render(request, 'app/user/user_booking_history.html', context)
