from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def _is_host(user):
    return getattr(user, 'role', '') == 'host' or getattr(user, 'is_superuser', False)


@login_required
def owner_dashboard(request):
    """Dashboard for hosts showing quick stats and recent activity."""
    try:
        from .models import Listing, Booking, Message
    except Exception:
        return render(request, 'app/pages/owner/dashboard.html', {'error': 'Models unavailable'})

    if not _is_host(request.user):
        messages.error(request, 'Trang này chỉ dành cho chủ nhà')
        return redirect('home')

    listings_qs = Listing.objects.filter(host=request.user).order_by('-created_at')
    recent_listings = listings_qs[:6]
    recent_bookings = Booking.objects.filter(listing__host=request.user).order_by('-created_at')[:8]
    recent_messages = Message.objects.filter(receiver=request.user).order_by('-created_at')[:8] if hasattr(Message, 'objects') else []

    stats = {
        'total_listings': listings_qs.count(),
        'total_bookings': Booking.objects.filter(listing__host=request.user).count(),
    }

    context = {
        'recent_listings': recent_listings,
        'recent_bookings': recent_bookings,
        'recent_messages': recent_messages,
        'stats': stats,
    }

    return render(request, 'app/pages/owner/dashboard.html', context)


@login_required
def owner_listings(request):
    """Paginated list of a host's own listings."""
    try:
        from .models import Listing
    except Exception:
        return render(request, 'app/pages/owner/listings.html', {'error': 'Models unavailable'})

    if not _is_host(request.user):
        messages.error(request, 'Trang này chỉ dành cho chủ nhà')
        return redirect('home')

    qs = Listing.objects.filter(host=request.user).order_by('-created_at')
    page = request.GET.get('page', 1)
    paginator = Paginator(qs, 12)
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(request, 'app/pages/owner/listings.html', {'page_obj': page_obj})


@login_required
def owner_bookings(request):
    """Paginated bookings across all listings owned by current host."""
    try:
        from .models import Booking
    except Exception:
        return render(request, 'app/pages/owner/bookings.html', {'error': 'Models unavailable'})

    if not _is_host(request.user):
        messages.error(request, 'Trang này chỉ dành cho chủ nhà')
        return redirect('home')

    qs = Booking.objects.filter(listing__host=request.user).order_by('-check_in')
    page = request.GET.get('page', 1)
    paginator = Paginator(qs, 12)
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(request, 'app/pages/owner/bookings.html', {'page_obj': page_obj})


@user_passes_test(lambda u: getattr(u, 'is_superuser', False))
def suspend_host(request, host_id):
    """Admin action: mark a host's policy as suspended."""
    try:
        from .models import HostPolicy, User
    except Exception:
        messages.error(request, 'Models unavailable')
        return redirect('home')

    host = get_object_or_404(User, pk=host_id)
    policy = getattr(host, 'policy', None)
    if policy is None:
        # create policy if missing
        try:
            policy = HostPolicy.objects.create(host=host, warning_count=1, is_suspended=True)
        except Exception as exc:
            messages.error(request, f'Không thể tạo chính sách: {exc}')
            return redirect('home')
    else:
        policy.is_suspended = True
        policy.warning_count = (getattr(policy, 'warning_count', 0) or 0) + 1
        policy.save()

    messages.success(request, f'Chủ nhà {host} đã bị tạm khóa')
    return redirect('admin:auth_user_changelist')


@user_passes_test(lambda u: getattr(u, 'is_superuser', False))
def reinstate_host(request, host_id):
    try:
        from .models import User
    except Exception:
        messages.error(request, 'Models unavailable')
        return redirect('home')

    host = get_object_or_404(User, pk=host_id)
    policy = getattr(host, 'policy', None)
    if policy:
        policy.is_suspended = False
        policy.warning_count = 0
        policy.save()
        messages.success(request, f'Chủ nhà {host} đã được kích hoạt lại')
    else:
        messages.info(request, 'Chưa có chính sách cho chủ nhà này')

    return redirect('admin:auth_user_changelist')
