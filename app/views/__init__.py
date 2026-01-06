from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from .user_view import user_profile

from ..auth_views import login_view, logout_view

# Import submodules from this package
from .home_views import home_view
from .category_views import category_view
from .bnb_information import listing_detail
from .result_view import search_results


from .user_view import user_profile, edit_profile, user_listings, user_bookings, profile_trips , profile_host


from .book_view import create_booking, booking_detail, cancel_booking, host_bookings
from .booking_success_view import booking_success
from .user_booking_history_view import user_booking_history
from .sub_info_view import amenity_detail, host_policy_view, verification_status, payment_info
from .add_new_bnb import create_listing
from .owner_management_view import owner_dashboard, owner_listings, owner_bookings, suspend_host, reinstate_host
from .info_owner_bnb_view import owner_listing_info
from .contact_view import contact, contact_host
from .create_listing_views import (
    step_loaichoo, step_dattieude, step_duocuse, step_diachi, step_thoigianthue, step_thongtincb,
    step_tiennghii, step_themanh, step_tieude, step_thietlapgia, step_chiasett
)


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


# def chitietnoio(request):
#     """Render the detail page template created by the user."""
#     from app.models import Listing
#     room_param = request.GET.get('room')
#     if not room_param:
#         return render(request, 'app/guest/chitietnoio.html', {})

#     try:
#         room_id = int(room_param)
#     except (TypeError, ValueError):
#         room_id = None

#     listing = None
#     if room_id:
#         try:
#             listing = Listing.objects.select_related().prefetch_related('images', 'amenities').get(listing_id=room_id)
#         except Listing.DoesNotExist:
#             listing = None

#     context = {'listing': listing}
#     return render(request, 'app/guest/chitietnoio.html', context)

from django.shortcuts import render, get_object_or_404
from django.db.models import Avg
from app.models import Listing, Review, Booking, ReviewAnalysis
from django.utils import timezone
from app.sentiment import analyze_sentiment

def chitietnoio(request):
    """Render the detail page template created by the user."""

    room_param = request.GET.get('room')
    if not room_param:
        return render(request, 'app/guest/chitietnoio.html', {})

    try:
        room_id = int(room_param)
    except (TypeError, ValueError):
        return render(request, 'app/guest/chitietnoio.html', {})

    listing = get_object_or_404(
        Listing.objects
        .select_related('listingaddress')
        .prefetch_related('images', 'amenities', 'reviews__user', 'reviews__analysis'),
        pk=room_id
    )

    # ================== XỬ LÝ POST (GỬI ĐÁNH GIÁ) ==================
    if request.method == "POST" and request.user.is_authenticated:
        rating = int(request.POST.get("rating"))
        comment = request.POST.get("comment", "").strip()

        booking = Booking.objects.filter(
            listing=listing,
            user=request.user,
            check_out__lt=timezone.now(),
            booking_status="completed").order_by("-check_out").first()
        if not booking:
            return redirect(request.path)

        if comment:
            review = Review.objects.create(
                listing=listing,
                user=request.user,
                rating=rating,
                comment=comment
            )

            # Try to analyze sentiment but don't fail the request if model errors occur
            try:
                from decimal import Decimal, ROUND_HALF_UP

                sentiment, confidence = analyze_sentiment(comment)
                # Normalize confidence to Decimal with 2 decimal places
                try:
                    conf_dec = Decimal(str(confidence)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                except Exception:
                    conf_dec = Decimal('0.00')

                ReviewAnalysis.objects.create(
                    review=review,
                    sentiment=sentiment,
                    confidence_score=conf_dec
                )
            except Exception as e:
                # Log error but allow the review to be saved
                print('Sentiment analysis error:', e)
            # Clear any prefetched review caches on the listing so the new
            # review and its analysis are visible when rendering below.
            if hasattr(listing, '_prefetched_objects_cache'):
                listing._prefetched_objects_cache.pop('reviews', None)
                listing._prefetched_objects_cache.pop('reviews__analysis', None)
    # ===============================================================

    reviews = listing.reviews.all()
    avg_rating = reviews.aggregate(avg=Avg('rating'))['avg']

    

    # ================== ĐIỀU KIỆN ĐƯỢC ĐÁNH GIÁ ==================
    can_review = False
    if request.user.is_authenticated:
        has_completed_booking = Booking.objects.filter(
            listing=listing,
            user=request.user,
            check_out__lt=timezone.now(),
            booking_status="completed"
        ).exists()

        already_reviewed = Review.objects.filter(
            listing=listing,
            user=request.user
        ).exists()

        can_review = has_completed_booking and not already_reviewed
    # =============================================================

    context = {
        'listing': listing,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'address': getattr(listing, 'listingaddress', None),
        'images': listing.images.all(),
        'amenities': listing.amenities.all(),
        'can_review': can_review,
    }

    return render(request, 'app/guest/chitietnoio.html', context)


def buoc1(request):
    return render(request, 'app/host/buoc1.html')


def buoc2(request):
    return render(request, 'app/host/buoc2.html')


def buoc3(request):
    return render(request, 'app/host/buoc3.html')


def giacuoituan(request):
    return render(request, 'app/host/giacuoituan.html')


def loaichoo(request):
    return step_loaichoo(request)
def dattieude(request):
    return step_dattieude(request)


def duocuse(request):
    return step_duocuse(request)


def diachi(request):
    return step_diachi(request)


def thoigianthue(request):
    return step_thoigianthue(request)


def thongtincb(request):
    return step_thongtincb(request)


def tiennghii(request):
    return step_tiennghii(request)


def themanh(request):
    return step_themanh(request)


def tieude(request):
    return step_tieude(request)


def thietlapgia(request):
    return step_thietlapgia(request)


def chiasett(request):
    return step_chiasett(request)


def trungtamtrogiup(request):
    return render(request, 'app/other_templates/trungtamtrogiup.html')


@login_required
def datphong(request):
    """Trang đặt phòng với thông tin listing từ database."""
    from ..models import Listing
    from django.shortcuts import get_object_or_404
    
    # Lấy listing_id từ URL query hoặc form
    listing_id = request.GET.get('room') or request.GET.get('listing')
    
    if not listing_id:
        # Nếu không có listing_id, chuyển về trang home
        from django.shortcuts import redirect
        return redirect('home')
    
    try:
        listing = get_object_or_404(Listing, listing_id=int(listing_id))
        
        # Lấy ảnh chính
        main_image = listing.images.filter(is_main=True).first()
        if not main_image:
            main_image = listing.images.first()
        
        # Lấy địa chỉ
        address = getattr(listing, 'listingaddress', None)
        
        # Tính rating trung bình
        reviews = listing.reviews.all()
        avg_rating = sum(r.rating for r in reviews) / len(reviews) if reviews else 0
        
        context = {
            'listing': listing,
            'listing_id': listing.listing_id,
            'title': listing.title,
            'price_per_night': listing.price_per_night,
            'cleaning_fee': listing.cleaning_fee,
            'extra_guest_fee': listing.extra_guest_fee or 0,
            'weekend_multiplier': listing.weekend_multiplier,
            'max_adults': listing.max_adults,
            'max_children': listing.max_children,
            'max_pets': listing.max_pets,
            'image_url': main_image.image_url if main_image else '',
            'location': f"{address.district}, {address.city}" if address else 'Thành phố Hồ Chí Minh',
            'rating': round(avg_rating, 2),
            'review_count': len(reviews),
        }
        
        return render(request, 'app/guest/datphong.html', context)
    except Exception as e:
        from django.shortcuts import redirect
        from django.contrib import messages
        messages.error(request, f'Không tìm thấy chỗ ở: {str(e)}')
        return redirect('home')


def phuongthucthanhtoan(request):
    return render(request, 'app/other_templates/phuongthucthanhtoan.html')


def chinhsachdieukhoan(request):
    return render(request, 'app/other_templates/chinhsachdieukhoan.html')

def profile_view(request):
    """Trang hồ sơ người dùng - chỉ hiển thị thông tin cá nhân."""
    if not request.user.is_authenticated:
        messages.error(request, 'Vui lòng đăng nhập để xem hồ sơ')
        return redirect('login')
    
    # Thống kê
    from app.models import Booking, Review
    booking_count = Booking.objects.filter(user=request.user).count()
    review_count = Review.objects.filter(user=request.user).count()
    
    context = {
        'user': request.user,
        'booking_count': booking_count,
        'review_count': review_count,
    }
    
    return render(request, 'app/user/user_profile.html', context)


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
    'create_booking', 'booking_detail', 'cancel_booking', 'host_bookings', 'booking_success', 'user_booking_history',
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
