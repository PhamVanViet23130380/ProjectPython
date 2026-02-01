from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.shortcuts import get_object_or_404, redirect, render

from app.models import Booking, Complaint


@login_required
def complaint_create(request, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)

    if booking.booking_status != 'completed':
        messages.error(request, 'Chỉ cho phép gửi khiếu nại sau khi hoàn thành kỳ thuê.')
        return redirect('user_booking_history')

    if request.method == 'POST':
        reason = (request.POST.get('reason') or '').strip()
        if not reason:
            messages.error(request, 'Vui lòng nhập nội dung khiếu nại.')
        elif len(reason) < 10:
            messages.error(request, 'Nội dung khiếu nại cần ít nhất 10 ký tự.')
        else:
            existing_open = Complaint.objects.filter(
                user=request.user,
                listing=booking.listing,
                status='open',
            ).first()
            if existing_open:
                messages.warning(
                    request,
                    'Bạn đã có một khiếu nại đang mở cho chỗ ở này. Vui lòng đợi xử lý.'
                )
            else:
                Complaint.objects.create(
                    user=request.user,
                    listing=booking.listing,
                    reason=reason,
                    status='open',
                )
                try:
                    send_complaint_confirmation_email(request.user, booking, reason)
                except Exception:
                    pass
                messages.success(request, 'Đã gửi khiếu nại. Chúng tôi sẽ xử lý sớm.')
                return redirect('complaint_list')

    context = {
        'booking': booking,
        'listing': booking.listing,
    }
    return render(request, 'app/user/complaint_create.html', context)


@login_required
def complaint_list(request):
    complaints = Complaint.objects.filter(
        user=request.user
    ).select_related('listing').order_by('-created_at')

    context = {
        'complaints': complaints,
    }
    return render(request, 'app/user/complaint_list.html', context)


def send_complaint_confirmation_email(user, booking, reason):
    subject = 'Xac nhan da nhan khieu nai - Home Nest'
    context = {
        'user_name': user.get_full_name() or user.username,
        'listing_title': booking.listing.title,
        'booking_id': booking.booking_id,
        'check_in': booking.check_in,
        'check_out': booking.check_out,
        'total_price': booking.base_price,
        'reason': reason,
    }
    html_message = render_to_string('app/emails/complaint_confirmation.html', context)
    plain_message = strip_tags(html_message)
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=True,
    )
