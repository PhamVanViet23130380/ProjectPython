from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.timezone import now
from django.db.models import Sum, Avg
from app.models import Booking, Review, Listing, User



from django.shortcuts import render

@login_required
def profile_host_bookings(request):
    bookings = Booking.objects.filter(
        listing__host=request.user
    ).select_related('listing', 'user')

    return render(request, 'app/user/profile_host_bookings.html', {
        'bookings': bookings
    })




def build_profile_stats(user):
    bookings = Booking.objects.filter(user=user)

    return {
        'total_trips': bookings.count(),

        'upcoming_trips': bookings.filter(
            booking_status='confirmed' ,
            check_in__gt=now().date()   # ← PHẢI là check_in
        ).count(),

        'completed_trips': bookings.filter(
            booking_status='completed'
        ).count(),

        'total_spent': bookings.filter(
            booking_status='completed'
        ).aggregate(total=Sum('total_price'))['total'] or 0,

        'avg_rating': (
            Review.objects.filter(listing__host=user)
            .aggregate(avg=Avg('rating'))['avg']
            if hasattr(user, 'listings') and user.listings.exists()
            else None
        )
    }






def user_profile(request, username=None):
    """Display a user's public profile.

    If `username` is None, show the current user's profile (login required).
    """

    if username is None:
        if not request.user.is_authenticated:
            messages.error(request, 'Vui lòng đăng nhập để xem hồ sơ')
            return redirect('login')
        user = request.user
    else:
        user = get_object_or_404(User, username=username)

    is_owner = request.user.is_authenticated and request.user.id == user.id

    # expose a minimal public context
    public_info = {
        'username': getattr(user, 'username', ''),
        'full_name': getattr(user, 'full_name', '') if hasattr(user, 'full_name') else getattr(user, 'get_full_name', lambda: '')(),
        'profile_photo': getattr(user, 'profile_photo', None),
        'bio': getattr(user, 'bio', '') if hasattr(user, 'bio') else '',
    }

    stats = build_profile_stats(user)


    return render(request, 'app/user/profile.html', {'profile_user': user, 'public': public_info, 
            'is_owner': is_owner,
            **stats,})


@login_required
def edit_profile(request):
    user = request.user

    if request.method == 'POST':
        user.full_name = request.POST.get('full_name')
        user.phone_number = request.POST.get('phone_number')

        if 'avatar' in request.FILES:
            user.avatar = request.FILES['avatar']

        user.save()
        return redirect('profile')

    stats = build_profile_stats(user)

    return render(
        request,
        'app/user/profile.html',
        {
            'edit_mode': True,
            'profile_user': user,
            **stats
        }
    )


def user_listings(request, username=None):
    """List listings for a user. If `username` omitted, use current user (login required)."""
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
    qs = Booking.objects.filter(user=request.user).order_by('-check_in')
    page = request.GET.get('page', 1)
    paginator = Paginator(qs, 12)
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(request, 'app/pages/user_bookings.html', {'page_obj': page_obj})


@login_required
def profile_trips(request):
    today = now().date()

    bookings = Booking.objects.filter(user=request.user)

    upcoming = bookings.filter(
        booking_status='confirmed',
        check_in__gt=today
    )

    ongoing = bookings.filter(
        booking_status__in=['confirmed', 'in_progress'],
        check_in__lte=today,
        check_out__gte=today
    )

    completed = bookings.filter(
        booking_status='completed'
    )

    return render(
        request,
        'app/user/profile_trips.html',
        {
            'upcoming': upcoming,
            'ongoing': ongoing,
            'completed': completed,
        }
    )

@login_required
def profile_host(request):
    user = request.user

    # Listings của host (prefetch ảnh để đỡ query)
    listings = user.listings.prefetch_related('images')

    total_listings = listings.count()

    # Booking cho các listing của host
    bookings = Booking.objects.filter(listing__host=user)

    total_bookings = bookings.exclude(
        booking_status='cancelled'
    ).count()

    total_revenue = bookings.filter(
        booking_status='completed'
    ).aggregate(total=Sum('total_price'))['total'] or 0

    avg_rating = Review.objects.filter(
        listing__host=user
    ).aggregate(avg=Avg('rating'))['avg'] or None

    return render(
        request,
        'app/user/profile_host.html',
        {
            'listings': listings,
            'total_listings': total_listings,
            'total_bookings': total_bookings,
            'total_revenue': total_revenue,
            'avg_rating': avg_rating,
        }
    )
