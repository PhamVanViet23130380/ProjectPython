from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def amenity_detail(request, amenity_id):
    """Show information about an amenity and example listings that provide it."""
    try:
        from .models import Amenity
    except Exception:
        return render(request, 'app/pages/sub/amenity_detail.html', {'error': 'Amenity model unavailable'})

    amenity = get_object_or_404(Amenity, pk=amenity_id)
    # related_name on Amenity -> 'listings'
    listings = amenity.listings.filter(is_active=True)[:24] if hasattr(amenity, 'listings') else []

    return render(request, 'app/pages/sub/amenity_detail.html', {
        'amenity': amenity,
        'listings': listings,
    })


def host_policy_view(request, listing_id=None, host_id=None):
    """Display host policy either by listing or by host id.

    If both omitted and user is authenticated, show current user's policy.
    """
    try:
        from .models import Listing, HostPolicy
    except Exception:
        return render(request, 'app/pages/sub/host_policy.html', {'error': 'HostPolicy model unavailable'})

    policy = None
    if listing_id is not None:
        listing = get_object_or_404(Listing, pk=listing_id)
        policy = getattr(listing.host, 'policy', None)
    elif host_id is not None:
        policy = get_object_or_404(HostPolicy, host__pk=host_id)
    else:
        if request.user.is_authenticated:
            policy = getattr(request.user, 'policy', None)

    if policy is None:
        return render(request, 'app/pages/sub/host_policy.html', {'message': 'Không tìm thấy chính sách cho chủ nhà này'})

    return render(request, 'app/pages/sub/host_policy.html', {'policy': policy})


def verification_status(request, user_id=None):
    """Show verification records for a user. Requires login unless `user_id` is provided."""
    try:
        from .models import Verification, User
    except Exception:
        return render(request, 'app/pages/sub/verification_status.html', {'error': 'Verification model unavailable'})

    if user_id is None:
        if not request.user.is_authenticated:
            messages.error(request, 'Vui lòng đăng nhập để xem trạng thái xác thực')
            return render(request, 'app/pages/sub/verification_status.html', {'verifications': []})
        user = request.user
    else:
        user = get_object_or_404(User, pk=user_id)

    verifications = Verification.objects.filter(account=user).order_by('-created_at')
    return render(request, 'app/pages/sub/verification_status.html', {'verifications': verifications, 'user': user})


@login_required
def payment_info(request, booking_id):
    """Show payment information for a booking if current user is actor (payer or host)."""
    try:
        from .models import Booking
    except Exception:
        return render(request, 'app/pages/sub/payment_info.html', {'error': 'Payment model unavailable'})

    booking = get_object_or_404(Booking, pk=booking_id)
    # simple permission: user is booking.user or booking.listing.host
    user = request.user
    allowed = (getattr(booking, 'user_id', None) == getattr(user, 'id', None)) or (
        hasattr(booking, 'listing') and getattr(booking.listing, 'host_id', None) == getattr(user, 'id', None)
    )
    if not allowed:
        messages.error(request, 'Bạn không có quyền xem thông tin thanh toán này')
        return render(request, 'app/pages/sub/payment_info.html', {'error': 'no-permission'})

    payment = getattr(booking, 'payment', None)
    return render(request, 'app/pages/sub/payment_info.html', {'payment': payment, 'booking': booking})
