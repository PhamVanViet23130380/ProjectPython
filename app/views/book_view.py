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


    try:
        from .models import Listing, Booking
    except Exception:
        messages.error(request, 'Models unavailable')
        return redirect('home')

    listing = get_object_or_404(Listing, pk=listing_id , is_active=True)

    # ❌ Host không được tự book phòng của mình
    if listing.host_id == request.user.id:
        messages.error(request, 'Bạn không thể đặt phòng của chính mình')
        return redirect('listing_detail', listing_id=listing_id)
    



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
            return redirect('listing_detail', listing_id=listing_id)

        # Validation 1: Check listing is still active
        if not listing.is_active:
            messages.error(request, 'Chỗ ở này hiện không còn hoạt động')
            return redirect('home')

        # Validation 2: Check check-in date must be from today onwards
        from datetime import date
        today = date.today()
        if checkin < today:
            messages.error(request, 'Ngày nhận phòng phải từ hôm nay trở đi')
            return redirect('listing_detail', listing_id=listing_id)

        if checkout <= checkin:
            messages.error(request, 'Ngày trả phải lớn hơn ngày nhận')
            return redirect('listing_detail', listing_id=listing_id)

        # Validation 3: Check number of guests doesn't exceed max_adults
        try:
            guests = int(guests_raw) if guests_raw else 1
        except Exception:
            guests = 1

        if guests > listing.max_adults:
            messages.error(request, f'Số khách không được vượt quá {listing.max_adults} người')
            return redirect('listing_detail', listing_id=listing_id)

        if guests < 1:
            messages.error(request, 'Số khách phải ít nhất 1 người')
            return redirect('listing_detail', listing_id=listing_id)

        # calculate price breakdown using helper (returns Decimal values)
        try:
            price_data = calculate_total_price(listing, checkin, checkout, guests=guests)
            total_price = price_data.get('total')
        except Exception:
            total_price = None

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
                    return redirect('chitietnoio')

                # create booking in pending state; confirm after payment succeeds
                # persist breakdown fields when available
                base_price = price_data.get('base') if isinstance(price_data, dict) else None
                service_fee_val = price_data.get('service_fee') if isinstance(price_data, dict) else None
                cleaning_fee_val = price_data.get('cleaning_fee') if isinstance(price_data, dict) else None

                booking = Booking.objects.create(
                    user=request.user,
                    listing=listing,
                    check_in=checkin,
                    check_out=checkout,
                    guests=guests,
                    total_price=total_price,
                    base_price=base_price,
                    service_fee=service_fee_val,
                    cleaning_fee=cleaning_fee_val,
                    booking_status='pending',  # Đặt status là pending, chờ thanh toán
                    note=note,  # Lưu ghi chú cho host
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
def host_bookings(request):
    """List bookings for listings owned by current user (host)."""
    try:
        from .models import Booking
    except Exception:
        return render(request, 'app/pages/host_bookings.html', {'error': 'Booking model unavailable'})

    qs = Booking.objects.filter(listing__host=request.user).order_by('-check_in')
    return render(request, 'app/pages/host_bookings.html', {'bookings': qs})


def send_booking_confirmation_email(request, booking, listing, checkin, checkout, guests, price_data):
    """
    Gửi email xác nhận đặt phòng cho khách hàng
    """
    try:
        # Tính số đêm
        nights = (checkout - checkin).days
        
        # Format giá tiền
        def format_price(price):
            if price is None:
                return "0"
            return f"{int(price):,}".replace(",", ".")
        
        # Chuẩn bị context cho email template
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
            'service_fee': format_price(price_data.get('service_fee')),
            'total_price': format_price(price_data.get('total')),
            'booking_url': request.build_absolute_uri(reverse('booking_success', args=[booking.booking_id])),
            'booking_history_url': request.build_absolute_uri(reverse('user_booking_history')),
        }
        
        # Render HTML email
        html_message = render_to_string('app/emails/booking_confirmation.html', context)
        plain_message = strip_tags(html_message)
        
        # Gửi email
        send_mail(
            subject=f'Xác nhận đặt phòng #{booking.booking_id} - Home Nest',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        return True
    except Exception as e:
        print(f"Lỗi chi tiết khi gửi email: {e}")
        raise


def send_cancellation_email(request, booking, refund_amount=0):
    """
    Gửi email thông báo hủy đặt phòng cho khách hàng
    """
    try:
        # Tính số đêm
        nights = (booking.check_out - booking.check_in).days
        
        # Format giá tiền
        def format_price(price):
            if price is None:
                return "0"
            return f"{int(price):,}".replace(",", ".")
        
        # Chuẩn bị context cho email template
        context = {
            'user_name': booking.user.get_full_name() or booking.user.username,
            'listing_title': booking.listing.title,
            'listing_image': booking.listing.images.first().image_url if booking.listing.images.exists() else '',
            'booking_id': booking.booking_id,
            'check_in': booking.check_in.strftime('%d/%m/%Y'),
            'check_out': booking.check_out.strftime('%d/%m/%Y'),
            'nights': nights,
            'total_price': format_price(booking.total_price),
            'refund_amount': format_price(refund_amount),
            'has_refund': refund_amount > 0,
            'booking_history_url': request.build_absolute_uri(reverse('user_booking_history')),
            'home_url': request.build_absolute_uri(reverse('home')),
        }
        
        # Render HTML email
        html_message = render_to_string('app/emails/booking_cancellation.html', context)
        plain_message = strip_tags(html_message)
        
        # Gửi email
        send_mail(
            subject=f'Xác nhận hủy đặt phòng #{booking.booking_id} - Home Nest',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        return True
    except Exception as e:
        print(f"Lỗi chi tiết khi gửi email hủy: {e}")
        raise

