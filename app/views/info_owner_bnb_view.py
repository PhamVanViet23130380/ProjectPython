from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Avg, Q
from django.utils import timezone


@login_required
def owner_listing_info(request, listing_id):
    """Return dashboard-like information for a host about a single listing.

    Provides: total_bookings, upcoming_bookings, total_earnings, avg_rating, recent_messages.
    Only the listing owner (host) or superuser can access.
    """
    try:
        from .models import Listing, Booking, Payment, Review, Message
    except Exception:
        return render(request, 'app/pages/owner/listing_info.html', {'error': 'Models unavailable'})

    listing = get_object_or_404(Listing, pk=listing_id)

    # permission: host or superuser
    if not (request.user.is_superuser or getattr(listing, 'host_id', None) == getattr(request.user, 'id', None)):
        messages.error(request, 'Bạn không có quyền xem trang này')
        return redirect('home')

    # bookings
    bookings_qs = Booking.objects.filter(listing=listing)
    total_bookings = bookings_qs.count()

    now = timezone.now().date()
    upcoming_bookings = bookings_qs.filter(check_in__gte=now).order_by('check_in')[:10]

    # earnings: sum of payments.amount for bookings of this listing
    payments_qs = Payment.objects.filter(booking__listing=listing)
    total_earnings = payments_qs.aggregate(total=Sum('amount'))['total'] or 0

    # ratings
    avg_rating = Review.objects.filter(listing=listing).aggregate(avg=Avg('rating'))['avg']

    # recent messages to host regarding this listing (if Message model exists)
    recent_messages = []
    try:
        recent_messages = Message.objects.filter(Q(receiver=request.user) | Q(sender=request.user)).order_by('-created_at')[:10]
    except Exception:
        recent_messages = []

    context = {
        'listing': listing,
        'total_bookings': total_bookings,
        'upcoming_bookings': upcoming_bookings,
        'total_earnings': total_earnings,
        'avg_rating': avg_rating,
        'recent_messages': recent_messages,
    }

    return render(request, 'app/pages/owner/listing_info.html', context)
