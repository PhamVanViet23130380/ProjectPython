from django.shortcuts import render
from django.db.models import Count


def home(request):
    """Render the site home page.

    This view keeps logic minimal and safe: if a `Listing` model exists
    the view will attempt to provide a small `latest_listings` context.
    Any exception during model import/query is caught so the view still
    renders the template when the model shape differs.
    """
    latest_listings = []
    listings_da_nang = []
    hot_listings = []
    try:
        # import the Listing model from the package-level models shim
        from app.models import Listing

        if hasattr(Listing, 'objects'):
            try:
                # prefer active listings, prefetch images for template
                latest_listings = list(
                    Listing.objects.filter(is_active=True).prefetch_related('images')[:8]
                )

                # Listings in Đà Nẵng (if addresses exist)
                try:
                    listings_da_nang = list(
                        Listing.objects.filter(is_active=True, listingaddress__city__icontains='Đà Nẵng')
                        .prefetch_related('images')[:8]
                    )
                except Exception:
                    listings_da_nang = []

                # "Hot" listings: order by number of reviews (most reviewed first)
                try:
                    hot_listings = list(
                        Listing.objects.filter(is_active=True)
                        .annotate(review_count=Count('reviews'))
                        .order_by('-review_count')
                        .prefetch_related('images')[:8]
                    )
                except Exception:
                    hot_listings = []
            except Exception:
                latest_listings = []
    except Exception:
        latest_listings = []

    return render(request, 'app/pages/home.html', {'latest_listings': latest_listings})
