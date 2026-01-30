from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from ..models import Booking, Listing

from .payment_views import calculate_total_price


def booking_total_price(request, booking_id):
    """Return booking total (admin use previously required staff)."""
    booking = get_object_or_404(Booking, pk=booking_id)
    return JsonResponse({'total_price': str(booking.total_price)})


def listing_price(request):
    """Public API: calculate price breakdown for a listing.

    Query params: listing (id), checkin (YYYY-MM-DD), checkout (YYYY-MM-DD), guests (int)
    Returns JSON with keys: nights, base, service_fee, taxes, total
    (all strings for Decimal values).
    """
    listing_id = request.GET.get('listing') or request.GET.get('room')
    checkin = request.GET.get('checkin')
    checkout = request.GET.get('checkout')
    guests = request.GET.get('guests') or request.GET.get('guest') or request.GET.get('guests_count')

    try:
        listing = get_object_or_404(Listing, listing_id=int(listing_id))
    except Exception:
        return JsonResponse({'error': 'invalid listing'}, status=400)

    # parse guests
    try:
        guests = int(guests) if guests else 1
    except Exception:
        guests = 1

    # validate dates; rely on calculate_total_price to raise if invalid
    try:
        from datetime import datetime
        ci = datetime.strptime(checkin, '%Y-%m-%d').date() if checkin else None
        co = datetime.strptime(checkout, '%Y-%m-%d').date() if checkout else None
        if not ci or not co:
            return JsonResponse({'error': 'missing dates'}, status=400)
    except Exception:
        return JsonResponse({'error': 'invalid dates'}, status=400)

    try:
        breakdown = calculate_total_price(listing, ci, co, guests)
    except Exception as exc:
        return JsonResponse({'error': str(exc)}, status=400)

    # convert Decimal to string for JSON
    out = {k: (str(v) if hasattr(v, 'quantize') or isinstance(v, (int, float)) else str(v)) for k, v in breakdown.items()}
    return JsonResponse(out)


def listing_detail(request):
    """Return JSON details for a listing.

    Query params: listing (id) or room
    """
    listing_id = request.GET.get('listing') or request.GET.get('room')
    try:
        listing = Listing.objects.get(listing_id=int(listing_id))
    except Exception:
        return JsonResponse({'error': 'invalid listing'}, status=400)

    # build response
    images = [img.image_url for img in listing.images.all()[:10]]
    amenities = []
    for a in listing.amenities.all():
        amenities.append({'name': a.name})

    data = {
        'listing_id': listing.listing_id,
        'title': listing.title,
        'description': listing.description,
        'price_per_night': str(listing.price_per_night),
        'max_adults': listing.max_adults,
        'max_children': listing.max_children,
        'max_pets': listing.max_pets,
        'is_active': listing.is_active,
        'images': images,
        'amenities': amenities,
        # provide simple defaults for fields the frontend expects
        'rating': 5.0,
        'reviews': 0,
    }
    return JsonResponse(data)
