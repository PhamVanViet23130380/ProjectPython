from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse
from django.urls import reverse
import json

from ..models import Booking, Payment, Listing

# --- price helper (moved here from app/utils.py) ---
from decimal import Decimal, ROUND_HALF_UP
from django.conf import settings


def quantize(v: Decimal) -> Decimal:
    return v.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def calculate_total_price(listing, check_in, check_out, guests,
                          service_fee_pct=Decimal('0.10'), tax_pct=Decimal('0.10')):
    """Return a dict with price breakdown (Decimal values).

    - listing: Listing instance (must have `price_per_night`).
    - check_in, check_out: date objects
    - guests: int
    """
    if check_out <= check_in:
        raise ValueError('check_out must be after check_in')

    nights = (check_out - check_in).days
    price_per_night = Decimal(str(getattr(listing, 'price_per_night', '0.00')))
    base = price_per_night * nights

    subtotal = base

    # If a fixed service fee is configured in settings, use it as a flat amount (assumed VND)
    if getattr(settings, 'SERVICE_FEE_FIXED', None):
        try:
            fixed = Decimal(str(settings.SERVICE_FEE_FIXED))
            service_fee = quantize(fixed)
        except Exception:
            # fallback to percentage if parsing fails
            service_fee = quantize(subtotal * Decimal(service_fee_pct or Decimal('0.10')))
    else:
        service_fee = quantize(subtotal * Decimal(service_fee_pct or Decimal('0.10')))

    # No taxes per product decision — total is subtotal + service_fee
    taxes = Decimal('0.00')
    total = quantize(subtotal + service_fee)

    return {
        'nights': nights,
        'base': quantize(base),
        'service_fee': service_fee,
        'taxes': taxes,
        'total': total,
    }

# --- end helper ---


@login_required
def payment_start(request, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)
    if booking.booking_status != 'pending':
        messages.error(request, 'Booking không ở trạng thái chờ thanh toán.')
        return redirect('booking_detail', booking_id=booking_id)

    if request.method == 'POST':
        # Simulate payment success (mock)
        payment = Payment.objects.create(
            booking=booking,
            method='card',
            amount=booking.total_price,
            status='paid',
            paid_at=timezone.now(),
            transaction_id=f"TXN-{booking.booking_id}-{int(timezone.now().timestamp())}",
        )
        booking.booking_status = 'confirmed'
        booking.save()
        
        # Gửi email xác nhận đặt phòng SAU KHI thanh toán thành công
        try:
            from .book_view import send_booking_confirmation_email
            from datetime import datetime
            
            # Tính price_data để gửi email
            price_data = {
                'base': booking.base_price,
                'service_fee': booking.service_fee,
                'total': booking.total_price,
            }
            
            send_booking_confirmation_email(
                request, 
                booking, 
                booking.listing, 
                booking.check_in, 
                booking.check_out, 
                booking.guests, 
                price_data
            )
        except Exception as email_error:
            # Không cho email lỗi làm fail toàn bộ thanh toán
            print(f"Lỗi khi gửi email xác nhận: {email_error}")
        
        messages.success(request, 'Thanh toán thành công. Đơn đã được xác nhận.')
        return redirect('booking_success', booking_id=booking.booking_id)

    return render(request, 'app/pages/payment_start.html', {'booking': booking})


@login_required
def payment_success(request, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id)
    return render(request, 'app/pages/payment_success.html', {'booking': booking})


@login_required
def payment_cancel(request, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)
    messages.info(request, 'Thanh toán bị huỷ.')
    return render(request, 'app/pages/payment_failed.html', {'booking': booking})


# --- payment signal handler (moved from app/signals.py) ---
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=Payment)
def payment_post_save(sender, instance, created, **kwargs):
    """When a Payment is saved with status 'paid', mark the related Booking as confirmed.

    This ensures payments created via admin or other code paths still update booking status.
    """
    try:
        if instance and instance.status == 'paid':
            booking = instance.booking
            if booking.booking_status != 'confirmed':
                booking.booking_status = 'confirmed'
                booking.save()
    except Exception:
        # avoid raising in signal; admin save should still succeed
        pass

# --- end signal handler ---


@login_required
def create_booking_and_pay(request, listing_id):
    """Create a booking and mark it paid only when user clicks 'Thanh toán' in the popup.

    Expects POST with: checkin, checkout, guests, note
    Returns redirect to booking_success or JSON with redirect when called via AJAX.
    """
    listing = get_object_or_404(Listing, pk=listing_id)
    if request.method != 'POST':
        messages.error(request, 'Phương thức không hợp lệ.')
        return redirect('chitietnoio', listing_id=listing.listing_id)

    # Parse inputs
    checkin_raw = request.POST.get('checkin')
    checkout_raw = request.POST.get('checkout')
    guests_raw = request.POST.get('guests')
    note = request.POST.get('note', '').strip()

    try:
        from datetime import datetime, date
        checkin = datetime.strptime(checkin_raw, '%Y-%m-%d').date()
        checkout = datetime.strptime(checkout_raw, '%Y-%m-%d').date()
        # basic validations
        if not listing.is_active:
            raise ValueError('Chỗ ở này hiện không còn hoạt động')
        today = date.today()
        if checkin < today:
            raise ValueError('Ngày nhận phòng phải từ hôm nay trở đi')
        if checkout <= checkin:
            raise ValueError('Ngày trả phải lớn hơn ngày nhận')

        if listing.available_from and listing.available_to and listing.available_from > listing.available_to:
            raise ValueError('Khoang thoi gian cho thue khong hop le')

        if listing.available_from and checkin < listing.available_from:
            raise ValueError('Ngay nhan phong phai tu ngay bat dau cho thue')

        if listing.available_to and checkout > listing.available_to:
            raise ValueError('Ngay tra phong khong duoc sau ngay ket thuc cho thue')

    except Exception as e:
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            return JsonResponse({'error': str(e)}, status=400)
        messages.error(request, f'Ngày không hợp lệ: {e}')
        return redirect('chitietnoio', listing_id=listing.listing_id)

    try:
        guests = int(guests_raw or '1')
    except Exception:
        guests = 1
    if guests > getattr(listing, 'max_adults', 1):
        err = f'Số khách không được vượt quá {listing.max_adults} người'
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            return JsonResponse({'error': err}, status=400)
        messages.error(request, err)
        return redirect('chitietnoio', listing_id=listing.listing_id)

    # Price breakdown
    price_data = calculate_total_price(listing, checkin, checkout, guests)

    from django.db import transaction
    with transaction.atomic():
        # Lock existing bookings for this listing
        existing = Booking.objects.select_for_update().filter(
            listing=listing
        ).exclude(booking_status='cancelled')

        conflict = False
        for other in existing:
            if other.booking_status == 'pending' and other.user_id == request.user.id:
                # allow reusing the user's pending booking
                continue
            if not (other.check_out <= checkin or other.check_in >= checkout):
                conflict = True
                break

        if conflict:
            msg = 'Khoang thoi gian nay da co nguoi dat. Vui long chon ngay khac.'
            if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
                return JsonResponse({'error': msg}, status=409)
            messages.error(request, msg)
            return redirect('chitietnoio', listing_id=listing.listing_id)

        # Reuse existing pending booking for this user+listing when possible
        booking = Booking.objects.select_for_update().filter(
            user=request.user,
            listing=listing,
            booking_status='pending'
        ).order_by('-created_at').first()

        if booking:
            booking.check_in = checkin
            booking.check_out = checkout
            booking.guests = guests
            booking.total_price = price_data['total']
            booking.base_price = price_data['base']
            booking.service_fee = price_data['service_fee']
            booking.note = note
            booking.save(update_fields=[
                'check_in', 'check_out', 'guests', 'total_price',
                'base_price', 'service_fee', 'note'
            ])
        else:
            booking = Booking.objects.create(
                user=request.user,
                listing=listing,
                check_in=checkin,
                check_out=checkout,
                guests=guests,
                total_price=price_data['total'],
                base_price=price_data['base'],
                service_fee=price_data['service_fee'],
                booking_status='pending',
                note=note,
            )

        payment = Payment.objects.filter(booking=booking).first()
        txn_id = f"TXN-{booking.booking_id}-{int(timezone.now().timestamp())}"
        if payment:
            if payment.status != 'paid':
                payment.method = 'card'
                payment.amount = booking.total_price
                payment.status = 'paid'
                payment.paid_at = timezone.now()
                payment.transaction_id = payment.transaction_id or txn_id
                payment.save(update_fields=['method', 'amount', 'status', 'paid_at', 'transaction_id'])
        else:
            payment = Payment.objects.create(
                booking=booking,
                method='card',
                amount=booking.total_price,
                status='paid',
                paid_at=timezone.now(),
                transaction_id=txn_id,
            )

        if booking.booking_status != 'confirmed':
            booking.booking_status = 'confirmed'
            booking.save(update_fields=['booking_status'])

    # Send confirmation email after successful payment
    try:
        from .book_view import send_booking_confirmation_email
        send_booking_confirmation_email(
            request,
            booking,
            listing,
            checkin,
            checkout,
            guests,
            price_data,
        )
    except Exception as e:
        # Do not fail the flow because of email errors
        print('Email error:', e)

    # Redirect
    redirect_url = reverse('booking_success', args=[booking.booking_id])

    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        return JsonResponse({'redirect': redirect_url})
    return redirect(redirect_url)
