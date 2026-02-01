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
    except Exception:
        pass

    # Ensure confirmation email is sent after successful payment
    if payment and getattr(payment, 'status', None) == 'paid':
        sent_key = f'booking_email_sent_{booking.booking_id}'
        if not request.session.get(sent_key):
            try:
                from .book_view import send_booking_confirmation_email
                price_data = {
                    'base': booking.base_price,
                    'service_fee': booking.service_fee,
                    'total': booking.base_price,
                }
                send_booking_confirmation_email(
                    request,
                    booking,
                    booking.listing,
                    booking.check_in,
                    booking.check_out,
                    booking.guests,
                    price_data,
                )
                request.session[sent_key] = True
            except Exception as exc:
                # Avoid failing the success page if email fails
                print('Booking confirmation email error:', exc)
    
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
