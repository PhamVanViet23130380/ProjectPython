from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse
from datetime import datetime
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

from .payment_views import calculate_total_price
from app.models import Listing, Booking, Payment


@login_required
def create_booking(request, listing_id):
    """Create a booking for a listing. GET shows a simple form, POST attempts creation."""



    listing = get_object_or_404(Listing, pk=listing_id , is_active=True)

    # Host cannot book their own listing
    if listing.host_id == request.user.id:
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            return JsonResponse({'error': 'B\u1ea1n kh\u00f4ng th\u1ec3 \u0111\u1eb7t ph\u00f2ng c\u1ee7a ch\u00ednh m\u00ecnh'}, status=403)
        messages.error(request, 'B\u1ea1n kh\u00f4ng th\u1ec3 \u0111\u1eb7t ph\u00f2ng c\u1ee7a ch\u00ednh m\u00ecnh')
        return redirect('chitietnoio', listing_id=listing_id)

    if request.user.is_staff or request.user.is_superuser:
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            return JsonResponse({'error': 'B\u1ea1n \u0111ang l\u00e0 Admin v\u00e0 kh\u00f4ng th\u1ec3 \u0111\u1eb7t \u0111\u01b0\u1ee3c ph\u00f2ng.'}, status=403)
        messages.error(request, 'B\u1ea1n \u0111ang l\u00e0 Admin v\u00e0 kh\u00f4ng th\u1ec3 \u0111\u1eb7t \u0111\u01b0\u1ee3c ph\u00f2ng.')
        return redirect('chitietnoio', listing_id=listing_id)

    if request.user.is_staff or request.user.is_superuser:
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            return JsonResponse({'error': 'B\u1ea1n \u0111ang l\u00e0m Admin v\u00e0 kh\u00f4ng \u0111\u01b0\u1ee3c ph\u00e9p \u0111\u1eb7t ph\u00f2ng'}, status=403)
        messages.error(request, 'B\u1ea1n \u0111ang l\u00e0m Admin v\u00e0 kh\u00f4ng \u0111\u01b0\u1ee3c ph\u00e9p \u0111\u1eb7t ph\u00f2ng')
        return redirect('chitietnoio', listing_id=listing_id)
    



    if request.method == 'POST':
        checkin_raw = request.POST.get('checkin')
        checkout_raw = request.POST.get('checkout')
        guests_raw = request.POST.get('guests')
        note = request.POST.get('note', '').strip()  # Lấy ghi chú từ textarea

        try:
            checkin = datetime.strptime(checkin_raw, '%Y-%m-%d').date()
            checkout = datetime.strptime(checkout_raw, '%Y-%m-%d').date()
        except Exception:
            messages.error(request, 'Ngày không hợp lệ (định dạng YYYY-MM-DD)')
            return redirect('chitietnoio', listing_id=listing_id)

        # Validation 1: Check listing is still active
        if not listing.is_active:
            messages.error(request, 'Chỗ ở này hiện không còn hoạt động')
            return redirect('home')

        # Validation 2: Check check-in date must be from today onwards
        from datetime import date
        today = date.today()
        if checkin < today:
            messages.error(request, 'Ngày nhận phòng phải từ hôm nay trở đi')
            return redirect('chitietnoio', listing_id=listing_id)

        if checkout <= checkin:
            messages.error(request, 'Ngày trả phải lớn hơn ngày nhận')
            return redirect('chitietnoio', listing_id=listing_id)


        if listing.available_from and listing.available_to and listing.available_from > listing.available_to:
            messages.error(request, 'Khoang thoi gian cho thue khong hop le')
            return redirect('chitietnoio', listing_id=listing_id)

        if listing.available_from and checkin < listing.available_from:
            messages.error(request, 'Ngay nhan phong phai tu ngay bat dau cho thue')
            return redirect('chitietnoio', listing_id=listing_id)

        if listing.available_to and checkout > listing.available_to:
            messages.error(request, 'Ngay tra phong khong duoc sau ngay ket thuc cho thue')
            return redirect('chitietnoio', listing_id=listing_id)

        # Validation 3: Check number of guests doesn't exceed max_adults
        try:
            guests = int(guests_raw) if guests_raw else 1
        except Exception:
            guests = 1

        if guests > listing.max_adults:
            messages.error(request, f'Số khách không được vượt quá {listing.max_adults} người')
            return redirect('chitietnoio', listing_id=listing_id)

        if guests < 1:
            messages.error(request, 'Số khách phải ít nhất 1 người')
            return redirect('chitietnoio', listing_id=listing_id)

        # calculate price breakdown using helper (returns Decimal values)
        try:
            price_data = calculate_total_price(listing, checkin, checkout, guests=guests)
        except Exception:
            price_data = None

        try:
            # Use a DB transaction + select_for_update to avoid race conditions
            with transaction.atomic():
                # Lock existing bookings for this listing to prevent concurrent inserts
                # Exclude bookings from current user to allow them to make multiple bookings
                # Consider ALL existing bookings (including current user's), except cancelled
                existing = Booking.objects.select_for_update().filter(listing=listing)
                # Check overlap with non-cancelled bookings
                overlap = []
                for other in existing:
                    if other.booking_status == 'pending' and other.user_id == request.user.id:
                        continue
                    if getattr(other, 'booking_status', None) == 'cancelled':
                        continue
                    # Check overlap: booking overlaps if it's NOT (ends before OR starts after)
                    # Allow same-day checkout and checkin: checkout at 12:00, checkin at 14:00
                    if not (other.check_out <= checkin or other.check_in >= checkout):
                        overlap.append(other)

                if overlap:
                    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
                        return JsonResponse({'error': 'Khoảng thời gian này đã có người đặt. Vui lòng chọn ngày khác.'}, status=409)
                    messages.error(request, 'Khoảng thời gian này đã có người đặt. Vui lòng chọn ngày khác.')
                    return redirect('chitietnoio', listing_id=listing.listing_id)

                # create booking in pending state; confirm after payment succeeds
                # persist breakdown fields when available
                base_price = price_data.get('base') if isinstance(price_data, dict) else None
                service_fee_val = price_data.get('service_fee') if isinstance(price_data, dict) else None

                booking = Booking.objects.filter(
                    user=request.user,
                    listing=listing,
                    booking_status='pending'
                ).order_by('-created_at').first()

                if booking:
                    booking.check_in = checkin
                    booking.check_out = checkout
                    booking.guests = guests
                    booking.base_price = base_price
                    booking.service_fee = service_fee_val
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
                        base_price=base_price,
                        service_fee=service_fee_val,
                        booking_status='pending',  # pending until payment
                        note=note,  # host note
                    )

                # KHÔNG tạo Payment và KHÔNG gửi email ở đây
                # Sẽ tạo Payment và gửi email khi user click "Thanh toán" trong popup

            # Trả về booking_id để hiển thị popup xác nhận
            # KHÔNG redirect đến booking_success ngay
            if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'booking_id': str(booking.booking_id),
                    'message': 'Vui lòng xác nhận thanh toán'
                })

            # Nếu không phải AJAX, redirect về trang thanh toán
            return redirect('payment_start', booking_id=booking.booking_id)
        except Exception as exc:
            messages.error(request, f'Lỗi khi tạo booking: {exc}')
            return redirect('chitietnoio', listing_id=listing_id)

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

    return render(request, 'app/pages/booking_detail.html', {'booking': booking})


@login_required
def cancel_booking(request, booking_id):
    """Hủy đặt phòng"""
    # Lấy booking object
    try:
        booking = get_object_or_404(Booking, pk=booking_id)
    except Exception as e:
        messages.error(request, 'Không tìm thấy đơn đặt phòng')
        return redirect('user_booking_history')
    
    # Kiểm tra quyền
    if booking.user_id != request.user.id:
        messages.error(request, 'Bạn không có quyền hủy booking này')
        return redirect('user_booking_history')

    # Chỉ xử lý POST request
    if request.method == 'POST':
        # Kiểm tra booking đã bị hủy chưa
        if booking.booking_status == 'cancelled':
            messages.warning(request, 'Đơn đặt phòng này đã được hủy trước đó')
            return redirect('user_booking_history')

        # Không cho hủy khi đang ở hoặc đã hoàn thành
        if booking.booking_status in ['in_progress', 'completed']:
            messages.error(request, 'Không thể hủy khi đang ở hoặc đã hoàn thành.')
            return redirect('user_booking_history')

        # Không cho hủy khi đã đến ngày nhận phòng
        try:
            from django.utils import timezone
            today = timezone.localdate()
            if booking.check_in and booking.check_in <= today:
                messages.error(request, 'Không thể hủy khi đã đến ngày nhận phòng.')
                return redirect('user_booking_history')
        except Exception:
            pass
        
        # Hủy booking và xử lý hoàn tiền
        try:
            with transaction.atomic():
                # Cập nhật trạng thái booking
                booking.booking_status = 'cancelled'
                booking.save(update_fields=['booking_status'])
                
                # Xử lý hoàn tiền (nếu có payment)
                refund_amount = 0
                try:
                    payment = booking.payment
                    if payment and payment.status == 'paid':
                        # Cập nhật trạng thái thanh toán thành 'refunded'
                        payment.status = 'refunded'
                        payment.save(update_fields=['status'])
                        refund_amount = payment.amount
                except Payment.DoesNotExist:
                    pass  # Không có payment record
                
                # Verify the save worked
                booking.refresh_from_db()
                
                if booking.booking_status == 'cancelled':
                    # Gửi email thông báo hủy đặt phòng
                    try:
                        send_cancellation_email(request, booking, refund_amount)
                    except Exception as email_error:
                        # Không cho email lỗi làm fail toàn bộ hủy booking
                        print(f"Lỗi khi gửi email hủy: {email_error}")
                    
                    if refund_amount > 0:
                        messages.success(request, f'Đã hủy đặt phòng thành công. Số tiền ₫{int(refund_amount):,} sẽ được hoàn lại trong 5-7 ngày làm việc.'.replace(',', '.'))
                    else:
                        messages.success(request, 'Đã hủy đặt phòng thành công')
                else:
                    messages.error(request, 'Lỗi: Không thể cập nhật trạng thái booking')
                
        except Exception as exc:
            messages.error(request, f'Lỗi khi hủy đặt phòng: {exc}')

    # Redirect về trang lịch sử với filter cancelled
    from django.http import HttpResponseRedirect
    from django.urls import reverse
    redirect_url = reverse('user_booking_history') + '?filter=cancelled'
    return HttpResponseRedirect(redirect_url)


@login_required


@login_required
def host_bookings(request):
    """List bookings for listings owned by current user (host)."""
    qs = Booking.objects.filter(listing__host=request.user).order_by('-check_in')
    return render(request, 'app/pages/host_bookings.html', {'bookings': qs})


def send_booking_confirmation_email(request, booking, listing, checkin, checkout, guests, price_data):
    """Send booking confirmation email to the guest."""
    try:
        nights = (checkout - checkin).days

        def format_price(price):
            if price is None:
                return "0"
            return f"{int(price):,}".replace(",", ".")

        context = {
            'user_name': booking.user.get_full_name() or booking.user.username,
            'listing_title': listing.title,
            'listing_image': listing.images.first().image_url if listing.images.exists() else '',
            'booking_id': booking.booking_id,
            'check_in': checkin.strftime('%d/%m/%Y'),
            'check_out': checkout.strftime('%d/%m/%Y'),
            'nights': nights,
            'guests': guests,
            'base_price': format_price(price_data.get('base')),
            'total_price': format_price(price_data.get('base')),
            'booking_url': request.build_absolute_uri(reverse('booking_success', args=[booking.booking_id])),
            'booking_history_url': request.build_absolute_uri(reverse('user_booking_history')),
        }

        html_message = render_to_string('app/emails/booking_confirmation.html', context)
        plain_message = strip_tags(html_message)

        send_mail(
            subject=f'Xac nhan dat phong #{booking.booking_id} - Home Nest',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.user.email],
            html_message=html_message,
            fail_silently=False,
        )

        return True
    except Exception as e:
        print(f"Email confirmation error: {e}")
        raise


def send_cancellation_email(request, booking, refund_amount=0):
    """Send booking cancellation email to the guest."""
    try:
        nights = (booking.check_out - booking.check_in).days

        def format_price(price):
            if price is None:
                return "0"
            return f"{int(price):,}".replace(",", ".")

        context = {
            'user_name': booking.user.get_full_name() or booking.user.username,
            'listing_title': booking.listing.title,
            'listing_image': booking.listing.images.first().image_url if booking.listing.images.exists() else '',
            'booking_id': booking.booking_id,
            'check_in': booking.check_in.strftime('%d/%m/%Y'),
            'check_out': booking.check_out.strftime('%d/%m/%Y'),
            'nights': nights,
            'total_price': format_price(booking.base_price),
            'refund_amount': format_price(refund_amount),
            'has_refund': refund_amount > 0,
            'booking_history_url': request.build_absolute_uri(reverse('user_booking_history')),
            'home_url': request.build_absolute_uri(reverse('home')),
        }

        html_message = render_to_string('app/emails/booking_cancellation.html', context)
        plain_message = strip_tags(html_message)

        send_mail(
            subject=f'Xac nhan huy dat phong #{booking.booking_id} - Home Nest',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.user.email],
            html_message=html_message,
            fail_silently=False,
        )

        return True
    except Exception as e:
        print(f"Email cancellation error: {e}")
        raise
