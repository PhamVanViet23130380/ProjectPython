from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse, HttpResponseBadRequest
from django.urls import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver
import json
import hmac
import hashlib
from urllib.parse import urlencode

from ..models import Booking, Payment, Listing

# --- price helper (moved here from app/utils.py) ---
from decimal import Decimal, ROUND_HALF_UP
from django.conf import settings


def quantize(v: Decimal) -> Decimal:
    return v.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def calculate_total_price(listing, check_in, check_out, guests,
                          service_fee_pct=Decimal('0.20'), tax_pct=Decimal('0.10')):
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
    service_fee = quantize(subtotal * Decimal(service_fee_pct or Decimal('0.20')))

    # User only pays base price; service fee is recorded separately
    taxes = Decimal('0.00')
    total = quantize(subtotal)

    return {
        'nights': nights,
        'base': quantize(base),
        'service_fee': service_fee,
        'taxes': taxes,
        'total': total,
    }

# --- end helper ---


def _vnpay_get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


def _vnpay_build_payment_url(request, booking):
    tmn_code = getattr(settings, 'VNPAY_TMN_CODE', '')
    hash_secret = getattr(settings, 'VNPAY_HASH_SECRET', '')
    vnp_url = getattr(settings, 'VNPAY_URL', '')
    if not tmn_code or not hash_secret or not vnp_url:
        raise ValueError('VNPAY config missing')

    vnp_return = getattr(settings, 'VNPAY_RETURN_URL', '')
    if not vnp_return:
        vnp_return = request.build_absolute_uri(reverse('vnpay_return'))

    amount = int(Decimal(str(booking.base_price or '0.00')) * Decimal('100'))
    txn_ref = str(booking.booking_id)
    create_date = timezone.now().strftime('%Y%m%d%H%M%S')

    vnp_params = {
        'vnp_Version': getattr(settings, 'VNPAY_VERSION', '2.1.0'),
        'vnp_Command': 'pay',
        'vnp_TmnCode': tmn_code,
        'vnp_Amount': amount,
        'vnp_CurrCode': 'VND',
        'vnp_TxnRef': txn_ref,
        'vnp_OrderInfo': f'Booking {txn_ref}',
        'vnp_OrderType': 'other',
        'vnp_Locale': 'vn',
        'vnp_ReturnUrl': vnp_return,
        'vnp_IpAddr': _vnpay_get_client_ip(request),
        'vnp_CreateDate': create_date,
    }

    sorted_items = sorted(vnp_params.items())
    hash_data = urlencode(sorted_items, doseq=True)
    secure_hash = hmac.new(
        hash_secret.encode('utf-8'),
        hash_data.encode('utf-8'),
        hashlib.sha512
    ).hexdigest()

    query = urlencode(sorted_items, doseq=True)
    return f"{vnp_url}?{query}&vnp_SecureHash={secure_hash}"


@login_required
def payment_start(request, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)

    if booking.listing.host_id == request.user.id:
        messages.error(request, 'B\u1ea1n kh\u00f4ng th\u1ec3 \u0111\u1eb7t ph\u00f2ng c\u1ee7a ch\u00ednh m\u00ecnh')
        return redirect('chitietnoio', listing_id=booking.listing.listing_id)

    if request.user.is_staff or request.user.is_superuser:
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            return JsonResponse({'error': 'B\u1ea1n \u0111ang l\u00e0 Admin v\u00e0 kh\u00f4ng th\u1ec3 \u0111\u1eb7t \u0111\u01b0\u1ee3c ph\u00f2ng.'}, status=403)
        messages.error(request, 'B\u1ea1n \u0111ang l\u00e0 Admin v\u00e0 kh\u00f4ng th\u1ec3 \u0111\u1eb7t \u0111\u01b0\u1ee3c ph\u00f2ng.')
        return redirect('home')
    if booking.booking_status != 'pending':
        messages.error(request, 'Booking không ở trạng thái chờ thanh toán.')
        return redirect('booking_detail', booking_id=booking_id)

    if request.method == 'POST':
        # Simulate payment success (mock)
        payment = Payment.objects.create(
            booking=booking,
            method='card',
            amount=booking.base_price,
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
                'total': booking.base_price,
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
    if booking.booking_status != 'cancelled':
        booking.booking_status = 'cancelled'
        booking.save(update_fields=['booking_status'])
    payment = Payment.objects.filter(booking=booking).order_by('-paid_at', '-payment_id').first()
    if payment and payment.status != 'cancelled':
        payment.status = 'cancelled'
        payment.save(update_fields=['status'])
    messages.info(request, 'Thanh toan bi huy.')
    return render(request, 'app/pages/payment_failed.html', {'booking': booking})

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

    if listing.host_id == request.user.id:
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            return JsonResponse({'error': 'B\u1ea1n kh\u00f4ng th\u1ec3 \u0111\u1eb7t ph\u00f2ng c\u1ee7a ch\u00ednh m\u00ecnh'}, status=403)
        messages.error(request, 'B\u1ea1n kh\u00f4ng th\u1ec3 \u0111\u1eb7t ph\u00f2ng c\u1ee7a ch\u00ednh m\u00ecnh')
        return redirect('chitietnoio', listing_id=listing.listing_id)

    if request.user.is_staff or request.user.is_superuser:
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            return JsonResponse({'error': 'B\u1ea1n \u0111ang l\u00e0 Admin v\u00e0 kh\u00f4ng th\u1ec3 \u0111\u1eb7t \u0111\u01b0\u1ee3c ph\u00f2ng.'}, status=403)
        messages.error(request, 'B\u1ea1n \u0111ang l\u00e0 Admin v\u00e0 kh\u00f4ng th\u1ec3 \u0111\u1eb7t \u0111\u01b0\u1ee3c ph\u00f2ng.')
        return redirect('chitietnoio', listing_id=listing.listing_id)
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
            booking.base_price = price_data['base']
            booking.service_fee = price_data['service_fee']
            booking.note = note
            booking.save(update_fields=[
                'check_in', 'check_out', 'guests',
                'base_price', 'service_fee', 'note'
            ])
        else:
            booking = Booking.objects.create(
                user=request.user,
                listing=listing,
                check_in=checkin,
                check_out=checkout,
                guests=guests,
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
                payment.amount = booking.base_price
                payment.status = 'paid'
                payment.paid_at = timezone.now()
                payment.transaction_id = payment.transaction_id or txn_id
                payment.save(update_fields=['method', 'amount', 'status', 'paid_at', 'transaction_id'])
        else:
            payment = Payment.objects.create(
                booking=booking,
                method='card',
                amount=booking.base_price,
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


@login_required
def vnpay_create(request, booking_id):
    """Create VNPay sandbox payment URL for a pending booking."""
    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)

    if booking.listing.host_id == request.user.id:
        messages.error(request, 'B\u1ea1n kh\u00f4ng th\u1ec3 \u0111\u1eb7t ph\u00f2ng c\u1ee7a ch\u00ednh m\u00ecnh')
        return redirect('chitietnoio', listing_id=booking.listing.listing_id)

    if request.user.is_staff or request.user.is_superuser:
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            return JsonResponse({'error': 'B\u1ea1n \u0111ang l\u00e0 Admin v\u00e0 kh\u00f4ng th\u1ec3 \u0111\u1eb7t \u0111\u01b0\u1ee3c ph\u00f2ng.'}, status=403)
        messages.error(request, 'B\u1ea1n \u0111ang l\u00e0 Admin v\u00e0 kh\u00f4ng th\u1ec3 \u0111\u1eb7t \u0111\u01b0\u1ee3c ph\u00f2ng.')
        return redirect('home')
    if booking.booking_status != 'pending':
        msg = 'Booking is not pending.'
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            return JsonResponse({'error': msg}, status=400)
        messages.error(request, msg)
        return redirect('booking_success', booking_id=booking.booking_id)

    try:
        payment_url = _vnpay_build_payment_url(request, booking)
    except Exception as exc:
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            return JsonResponse({'error': str(exc)}, status=400)
        messages.error(request, 'Unable to create VNPay URL.')
        return redirect('booking_detail', booking_id=booking.booking_id)

    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        return JsonResponse({'payment_url': payment_url})
    return redirect(payment_url)


def _vnpay_verify_request(params):
    params = dict(params)
    secure_hash = params.pop('vnp_SecureHash', None)
    params.pop('vnp_SecureHashType', None)
    if not secure_hash:
        return False
    hash_secret = getattr(settings, 'VNPAY_HASH_SECRET', '')
    if not hash_secret:
        return False
    sorted_items = sorted(params.items())
    hash_data = urlencode(sorted_items, doseq=True)
    expected = hmac.new(
        hash_secret.encode('utf-8'),
        hash_data.encode('utf-8'),
        hashlib.sha512
    ).hexdigest()
    return secure_hash == expected


def vnpay_return(request):
    """Handle VNPay return URL and update booking/payment on success."""
    params = request.GET.dict()
    if not params:
        return HttpResponseBadRequest('Missing VNPay params')

    if not _vnpay_verify_request(params):
        messages.error(request, 'Invalid VNPay signature.')
        return redirect('home')

    txn_ref = params.get('vnp_TxnRef')
    resp_code = params.get('vnp_ResponseCode')
    amount = params.get('vnp_Amount')
    txn_no = params.get('vnp_TransactionNo', '')

    booking = get_object_or_404(Booking, booking_id=txn_ref)
    expected_amount = int(Decimal(str(booking.base_price or '0.00')) * Decimal('100'))
    if str(expected_amount) != str(amount):
        messages.error(request, 'Invalid VNPay amount.')
        return redirect('home')

    if resp_code != '00':
        if booking.booking_status != 'cancelled':
            booking.booking_status = 'cancelled'
            booking.save(update_fields=['booking_status'])
        payment = Payment.objects.filter(booking=booking).order_by('-paid_at', '-payment_id').first()
        if payment and payment.status != 'cancelled':
            payment.status = 'cancelled'
            payment.save(update_fields=['status'])
        messages.error(request, 'Payment failed or cancelled.') 
        return redirect('payment_cancel', booking_id=booking.booking_id)

    payment = Payment.objects.filter(booking=booking).first()
    if payment is None:
        payment = Payment.objects.create(
            booking=booking,
            method='vnpay',
            amount=booking.base_price,
            status='paid',
            paid_at=timezone.now(),
            transaction_id=txn_no or None,
        )
    else:
        payment.method = 'vnpay'
        payment.amount = booking.base_price
        payment.status = 'paid'
        payment.paid_at = timezone.now()
        payment.transaction_id = txn_no or payment.transaction_id
        payment.save()

    if booking.booking_status != 'confirmed':
        booking.booking_status = 'confirmed'
        booking.save(update_fields=['booking_status'])

    return redirect('booking_success', booking_id=booking.booking_id)


def vnpay_ipn(request):
    """VNPay IPN endpoint (server-to-server)."""
    params = request.GET.dict()
    if not params:
        return JsonResponse({'RspCode': '99', 'Message': 'Missing params'})

    if not _vnpay_verify_request(params):
        return JsonResponse({'RspCode': '97', 'Message': 'Invalid signature'})

    txn_ref = params.get('vnp_TxnRef')
    resp_code = params.get('vnp_ResponseCode')
    amount = params.get('vnp_Amount')
    txn_no = params.get('vnp_TransactionNo', '')

    booking = Booking.objects.filter(booking_id=txn_ref).first()
    if not booking:
        return JsonResponse({'RspCode': '01', 'Message': 'Order not found'})

    expected_amount = int(Decimal(str(booking.base_price or '0.00')) * Decimal('100'))
    if str(expected_amount) != str(amount):
        return JsonResponse({'RspCode': '04', 'Message': 'Invalid amount'})

    if resp_code == '00':
        payment = Payment.objects.filter(booking=booking).first()
        if payment is None:
            payment = Payment.objects.create(
                booking=booking,
                method='vnpay',
                amount=booking.base_price,
                status='paid',
                paid_at=timezone.now(),
                transaction_id=txn_no or None,
            )
        else:
            payment.method = 'vnpay'
            payment.amount = booking.base_price
            payment.status = 'paid'
            payment.paid_at = timezone.now()
            payment.transaction_id = txn_no or payment.transaction_id
            payment.save()
        if booking.booking_status != 'confirmed':
            booking.booking_status = 'confirmed'
            booking.save(update_fields=['booking_status'])
        return JsonResponse({'RspCode': '00', 'Message': 'Confirm Success'})

    return JsonResponse({'RspCode': '00', 'Message': 'Confirm Success'})
