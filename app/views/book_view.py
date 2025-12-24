from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import datetime


@login_required
def create_booking(request, listing_id):
    """Create a booking for a listing. GET shows a simple form, POST attempts creation."""
    try:
        from .models import Listing, Booking
    except Exception:
        messages.error(request, 'Models unavailable')
        return redirect('home')

    listing = get_object_or_404(Listing, pk=listing_id)

    if request.method == 'POST':
        checkin_raw = request.POST.get('checkin')
        checkout_raw = request.POST.get('checkout')
        guests_raw = request.POST.get('guests')

        try:
            checkin = datetime.strptime(checkin_raw, '%Y-%m-%d').date()
            checkout = datetime.strptime(checkout_raw, '%Y-%m-%d').date()
        except Exception:
            messages.error(request, 'Ngày không hợp lệ (định dạng YYYY-MM-DD)')
            return redirect('listing_detail', listing_id=listing_id)

        if checkout <= checkin:
            messages.error(request, 'Ngày trả phải lớn hơn ngày nhận')
            return redirect('listing_detail', listing_id=listing_id)

        nights = (checkout - checkin).days
        price_per_night = getattr(listing, 'price_per_night', None)
        try:
            total_price = float(price_per_night) * nights if price_per_night is not None else None
        except Exception:
            total_price = None

        try:
            guests = int(guests_raw) if guests_raw else 1
        except Exception:
            guests = 1

        try:
            booking = Booking.objects.create(
                user=request.user,
                listing=listing,
                checkin=checkin,
                checkout=checkout,
                guests=guests,
                total_price=total_price,
            )
            messages.success(request, 'Đặt phòng thành công')
            return redirect('booking_detail', booking_id=getattr(booking, 'pk', booking.id))
        except Exception as exc:
            messages.error(request, f'Lỗi khi tạo booking: {exc}')
            return redirect('listing_detail', listing_id=listing_id)

    # GET: render a simple booking form template (create if missing)
    return render(request, 'app/pages/create_booking.html', {'listing': listing})


def _user_can_view_booking(user, booking):
    try:
        if booking.user_id == getattr(user, 'id', None):
            return True
        # host can view if user is listing host
        if hasattr(booking, 'listing') and getattr(booking.listing, 'host_id', None) == getattr(user, 'id', None):
            return True
    except Exception:
        return False
    return False


@login_required
def booking_detail(request, booking_id):
    try:
        from .models import Booking
    except Exception:
        return render(request, 'app/pages/booking_detail.html', {'error': 'Booking model unavailable'})

    booking = get_object_or_404(Booking, pk=booking_id)
    if not _user_can_view_booking(request.user, booking):
        messages.error(request, 'Bạn không có quyền xem booking này')
        return redirect('home')

    return render(request, 'app/pages/booking_detail.html', {'booking': booking})


@login_required
def cancel_booking(request, booking_id):
    try:
        from .models import Booking
    except Exception:
        messages.error(request, 'Booking model unavailable')
        return redirect('home')

    booking = get_object_or_404(Booking, pk=booking_id)
    if not _user_can_view_booking(request.user, booking):
        messages.error(request, 'Bạn không có quyền hủy booking này')
        return redirect('home')

    if request.method == 'POST':
        # try to set a cancel/status field if present, otherwise delete
        try:
            if hasattr(booking, 'status'):
                booking.status = 'cancelled'
                booking.save()
            else:
                booking.delete()
            messages.success(request, 'Booking đã được hủy')
        except Exception as exc:
            messages.error(request, f'Lỗi khi hủy booking: {exc}')

    return redirect('user_bookings')


@login_required
def host_bookings(request):
    """List bookings for listings owned by current user (host)."""
    try:
        from .models import Booking
    except Exception:
        return render(request, 'app/pages/host_bookings.html', {'error': 'Booking model unavailable'})

    qs = Booking.objects.filter(listing__host=request.user).order_by('-checkin')
    return render(request, 'app/pages/host_bookings.html', {'bookings': qs})
