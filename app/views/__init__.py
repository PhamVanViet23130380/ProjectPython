from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model

# auth views live at top-level app/auth_views.py
from ..auth_views import login_view, logout_view

# Import submodules from this package
from .home_views import home
from .category_views import category_view
from .bnb_information import listing_detail
from .result_view import search_results
from .user_view import user_profile, edit_profile, user_listings, user_bookings
from .book_view import create_booking, booking_detail, cancel_booking, host_bookings
from .sub_info_view import amenity_detail, host_policy_view, verification_status, payment_info
from .add_new_bnb import create_listing
from .owner_management_view import owner_dashboard, owner_listings, owner_bookings, suspend_host, reinstate_host
from .info_owner_bnb_view import owner_listing_info
from .contact_view import contact, contact_host


def forgot_password(request):
    """Render the forgot-password page where user can request a password reset."""
    if request.method == 'POST':
        messages.success(request, 'Hướng dẫn đặt lại mật khẩu đã được gửi nếu email tồn tại.')
    return render(request, 'app/auth_template/forgot-password.html')


def taobaidang(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Vui lòng đăng nhập trước')
        return redirect('login')
    return render(request, 'app/host/taobaidang.html')


def chitietnoio(request):
    """Render the detail page template created by the user."""
    from app.models import Listing
    room_param = request.GET.get('room')
    if not room_param:
        return render(request, 'app/guest/chitietnoio.html', {})

    try:
        room_id = int(room_param)
    except (TypeError, ValueError):
        room_id = None

    listing = None
    if room_id:
        try:
            listing = Listing.objects.select_related().prefetch_related('images', 'amenities').get(listing_id=room_id)
        except Listing.DoesNotExist:
            listing = None

    context = {'listing': listing}
    return render(request, 'app/guest/chitietnoio.html', context)


def buoc1(request):
    return render(request, 'app/host/buoc1.html')


def thietlapgia(request):
    return render(request, 'app/host/thietlapgia.html')


def giacuoituan(request):
    return render(request, 'app/host/giacuoituan.html')


def chiasett(request):
    return render(request, 'app/host/chiasett.html')


def loaichoo(request):
    return render(request, 'app/host/loaichoo.html')


def trungtamtrogiup(request):
    return render(request, 'app/other_templates/trungtamtrogiup.html')


def datphong(request):
    return render(request, 'app/guest/datphong.html')


def phuongthucthanhtoan(request):
    return render(request, 'app/other_templates/phuongthucthanhtoan.html')


def chinhsachdieukhoan(request):
    return render(request, 'app/other_templates/chinhsachdieukhoan.html')


def buoc2(request):
    return render(request, 'app/host/buoc2.html')


def duocuse(request):
    return render(request, 'app/host/duocuse.html')


def themanh(request):
    return render(request, 'app/host/themanh.html')


def thongtincb(request):
    return render(request, 'app/host/thongtincb.html')


def tiennghii(request):
    return render(request, 'app/host/tiennghii.html')


def tieude(request):
    return render(request, 'app/host/tieude.html')


def diachi(request):
    return render(request, 'app/host/diachi.html')


def buoc3(request):
    return render(request, 'app/host/buoc3.html')



def profile_view(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Vui lòng đăng nhập để xem hồ sơ')
        return redirect('login')
    return render(request, 'app/components/profile.html')


# Resolve get_user_model after imports
User = get_user_model()


# Error handlers (used when DEBUG=False)
def error_404(request, exception=None):
    from .error_view import error_404 as _error_404
    return _error_404(request, exception)


def error_500(request):
    from .error_view import error_500 as _error_500
    return _error_500(request)


def error_403(request, exception=None):
    from .error_view import error_403 as _error_403
    return _error_403(request, exception)


# Explicitly export commonly-used views from this package
__all__ = [
    'home', 'category_view', 'listing_detail', 'search_results',
    'user_profile', 'edit_profile', 'user_listings', 'user_bookings',
    'create_booking', 'booking_detail', 'cancel_booking', 'host_bookings',
    'amenity_detail', 'host_policy_view', 'verification_status', 'payment_info',
    'create_listing', 'owner_dashboard', 'owner_listings', 'owner_bookings',
    'suspend_host', 'reinstate_host', 'owner_listing_info', 'contact', 'contact_host',
    'login_view', 'logout_view',
    'forgot_password', 'taobaidang', 'chitietnoio', 'buoc1', 'thietlapgia',
    'giacuoituan', 'chiasett', 'loaichoo', 'trungtamtrogiup', 'datphong',
    'phuongthucthanhtoan', 'chinhsachdieukhoan', 'buoc2', 'duocuse', 'themanh',
    'thongtincb', 'tiennghii', 'tieude', 'diachi', 'buoc3', 'profile_view',
    'error_404', 'error_500', 'error_403'
]
