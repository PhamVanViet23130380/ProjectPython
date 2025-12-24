from django.shortcuts import render, get_object_or_404
from django.db.models import Avg


def listing_detail(request, listing_id):
    """Show detailed page for a single listing (bnb).

    Loads related address, images, amenities and reviews. Keeps queries
    defensive so the view still works if some relations are missing.
    Renders `app/pages/listing_detail.html` (create template if missing).
    """
    try:
        from .models import Listing
    except Exception:
        # If models can't be imported, render an error-like page without raising
        return render(request, 'app/pages/listing_detail.html', {'error': 'Listing model unavailable'})

    listing = get_object_or_404(Listing, pk=listing_id)

    # related objects (use safe attribute access)
    address = getattr(listing, 'listingaddress', None)
    images = list(getattr(listing, 'images', []).all()) if hasattr(listing, 'images') else []
    amenities = list(getattr(listing, 'amenities', []).all()) if hasattr(listing, 'amenities') else []

    # reviews and aggregated rating
    reviews_qs = getattr(listing, 'reviews', None)
    reviews = list(reviews_qs.all()) if reviews_qs is not None else []
    avg_rating = None
    try:
        avg_rating = reviews_qs.aggregate(avg=Avg('rating'))['avg'] if reviews_qs is not None else None
    except Exception:
        avg_rating = None

    context = {
        'listing': listing,
        'address': address,
        'images': images,
        'amenities': amenities,
        'reviews': reviews,
        'avg_rating': avg_rating,
    }

    return render(request, 'app/pages/listing_detail.html', context)
