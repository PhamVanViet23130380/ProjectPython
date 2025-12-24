from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def user_profile(request, username=None):
    """Display a user's public profile.

    If `username` is None, show the current user's profile (login required).
    """
    try:
        from .models import User
    except Exception:
        return render(request, 'app/pages/user_profile.html', {'error': 'User model unavailable'})

    if username is None:
        if not request.user.is_authenticated:
            messages.error(request, 'Vui lòng đăng nhập để xem hồ sơ')
            return redirect('login')
        user = request.user
    else:
        user = get_object_or_404(User, username=username)

    # expose a minimal public context
    public_info = {
        'username': getattr(user, 'username', ''),
        'full_name': getattr(user, 'full_name', '') if hasattr(user, 'full_name') else getattr(user, 'get_full_name', lambda: '')(),
        'profile_photo': getattr(user, 'profile_photo', None),
        'bio': getattr(user, 'bio', '') if hasattr(user, 'bio') else '',
    }

    return render(request, 'app/pages/user_profile.html', {'profile_user': user, 'public': public_info})


@login_required
def edit_profile(request):
    """Allow authenticated user to update a few profile fields via POST.

    Keeps updates minimal and safe: `full_name`, `phone`, `bio`.
    """
    user = request.user
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        bio = request.POST.get('bio')

        try:
            if full_name is not None and hasattr(user, 'full_name'):
                user.full_name = full_name
            if phone is not None and hasattr(user, 'phone'):
                user.phone = phone
            if bio is not None and hasattr(user, 'bio'):
                user.bio = bio
            user.save()
            messages.success(request, 'Cập nhật hồ sơ thành công')
            return redirect('profile')
        except Exception as exc:
            messages.error(request, f'Lỗi khi lưu: {exc}')

    return render(request, 'app/pages/user_edit.html', {'profile_user': user})


def user_listings(request, username=None):
    """List listings for a user. If `username` omitted, use current user (login required)."""
    try:
        from .models import Listing, User
    except Exception:
        return render(request, 'app/pages/user_listings.html', {'error': 'Models unavailable'})

    if username is None:
        if not request.user.is_authenticated:
            messages.error(request, 'Vui lòng đăng nhập để xem danh sách của bạn')
            return redirect('login')
        owner = request.user
    else:
        owner = get_object_or_404(User, username=username)

    qs = Listing.objects.filter(host=owner).order_by('-created_at')
    page = request.GET.get('page', 1)
    paginator = Paginator(qs, 12)
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(request, 'app/pages/user_listings.html', {'page_obj': page_obj, 'owner': owner})


@login_required
def user_bookings(request):
    """Show bookings for current authenticated user."""
    try:
        from .models import Booking
    except Exception:
        return render(request, 'app/pages/user_bookings.html', {'error': 'Booking model unavailable'})

    qs = Booking.objects.filter(user=request.user).order_by('-checkin')
    page = request.GET.get('page', 1)
    paginator = Paginator(qs, 12)
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(request, 'app/pages/user_bookings.html', {'page_obj': page_obj})
