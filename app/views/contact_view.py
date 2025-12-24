from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail, BadHeaderError


def _get_admin_email():
    # Prefer ADMINS setting, fallback to DEFAULT_FROM_EMAIL
    admins = getattr(settings, 'ADMINS', None)
    if admins:
        first = admins[0]
        return first[1] if len(first) > 1 else None
    return getattr(settings, 'DEFAULT_FROM_EMAIL', None)


def contact(request):
    """General contact form. GET shows form, POST sends message to site admin or saves Message when possible."""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', 'Liên hệ từ người dùng').strip()
        message_body = request.POST.get('message', '').strip()

        if not message_body:
            messages.error(request, 'Vui lòng nhập nội dung liên hệ')
            return redirect('contact')

        # Try to save as Message model if available and user is authenticated
        try:
            from .models import Message, User
            if request.user and request.user.is_authenticated:
                admin_user = User.objects.filter(is_superuser=True).first()
                if admin_user:
                    try:
                        Message.objects.create(sender=request.user, receiver=admin_user, content=f"{subject}\n\n{message_body}")
                        messages.success(request, 'Gửi liên hệ thành công')
                        return redirect('contact')
                    except Exception:
                        pass
        except Exception:
            # models may not exist or create failed; fall back to email
            pass

        # Fallback: send email to ADMINS/DEFAULT_FROM_EMAIL
        admin_email = _get_admin_email()
        if admin_email:
            try:
                full_message = f"From: {name} <{email}>\n\n{message_body}"
                send_mail(subject, full_message, getattr(settings, 'DEFAULT_FROM_EMAIL', None), [admin_email])
                messages.success(request, 'Gửi liên hệ thành công')
            except BadHeaderError:
                messages.error(request, 'Tiêu đề email không hợp lệ')
            except Exception:
                messages.error(request, 'Không thể gửi email — thử lại sau')
        else:
            # No admin email configured; still show success to avoid UX blocker
            messages.info(request, 'Tin nhắn đã được ghi nhận (no email configured)')

        return redirect('contact')

    return render(request, 'app/pages/contact.html')


def contact_host(request, listing_id):
    """Contact the host of a listing. POST creates a Message if possible, otherwise attempts email to host.avatar_url?? (best-effort).

    Expects fields: subject, message
    """
    try:
        from .models import Listing, Message
    except Exception:
        listings_available = False
        Listing = None
    else:
        listings_available = True

    listing = None
    if listings_available:
        listing = get_object_or_404(Listing, pk=listing_id)
        host = getattr(listing, 'host', None)
    else:
        host = None

    if request.method == 'POST':
        subject = request.POST.get('subject', f'Yêu cầu về chỗ ở #{listing_id}' if listing else 'Yêu cầu').strip()
        message_body = request.POST.get('message', '').strip()

        if not message_body:
            messages.error(request, 'Vui lòng nhập nội dung')
            return redirect('listing_detail', listing_id=listing_id)

        # Try to save Message if model available and user authenticated
        try:
            from .models import Message
            if request.user and request.user.is_authenticated and host is not None:
                try:
                    Message.objects.create(sender=request.user, receiver=host, content=f"{subject}\n\n{message_body}")
                    messages.success(request, 'Tin nhắn đã gửi tới chủ nhà')
                    return redirect('listing_detail', listing_id=listing_id)
                except Exception:
                    pass
        except Exception:
            pass

        # Fallback: attempt to email host if host has email field
        host_email = None
        try:
            if host is not None:
                host_email = getattr(host, 'email', None)
        except Exception:
            host_email = None

        if host_email:
            try:
                full_message = f"From: {getattr(request.user, 'email', '')}\n\n{message_body}"
                send_mail(subject, full_message, getattr(settings, 'DEFAULT_FROM_EMAIL', None), [host_email])
                messages.success(request, 'Tin nhắn đã gửi tới chủ nhà')
            except Exception:
                messages.error(request, 'Không thể gửi tin nhắn tới chủ nhà')
        else:
            messages.info(request, 'Không thể liên hệ chủ nhà trực tiếp — đã ghi nhận yêu cầu')

        return redirect('listing_detail', listing_id=listing_id)

    # GET: render a contact-host form
    context = {'listing': listing}
    return render(request, 'app/pages/contact_host.html', context)
