from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from ..models import Booking, Payment


@login_required
def booking_success(request, booking_id):
    """Hiển thị trang thành công sau khi đặt phòng."""
    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)
    
    # Lấy thông tin thanh toán nếu có
    payment = None
    try:
        payment = Payment.objects.filter(booking=booking).first()
    except:
        pass
    
    # Tính số đêm
    nights = (booking.check_out - booking.check_in).days
    
    # Lấy ảnh chỗ ở
    listing_image = None
    if booking.listing.images.exists():
        listing_image = booking.listing.images.first()
    
    context = {
        'booking': booking,
        'payment': payment,
        'nights': nights,
        'listing_image': listing_image,
    }
    
    return render(request, 'app/guest/booking_success.html', context)
