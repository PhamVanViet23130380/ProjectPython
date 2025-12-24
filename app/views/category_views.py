from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q


def category_view(request):
    """Render category / listing filter page.

    Supported GET params:
    - q: full-text search on title/description
    - city, district: filter by ListingAddress.city/district
    - min_price, max_price: numeric filters on `price_per_night`
    - amenity: repeated or comma-separated names/ids to filter listings that have those amenities
    - page: pagination page number
    """
    listings = []
    try:
        from .models import Listing

        qs = Listing.objects.filter(is_active=True).order_by('-created_at')

        q = request.GET.get('q')
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))

        city = request.GET.get('city')
        if city:
            qs = qs.filter(listingaddress__city__icontains=city)

        district = request.GET.get('district')
        if district:
            qs = qs.filter(listingaddress__district__icontains=district)

        min_price = request.GET.get('min_price')
        if min_price:
            try:
                qs = qs.filter(price_per_night__gte=float(min_price))
            except Exception:
                pass

        max_price = request.GET.get('max_price')
        if max_price:
            try:
                qs = qs.filter(price_per_night__lte=float(max_price))
            except Exception:
                pass

        # amenities may be repeated: ?amenity=Wifi&amenity=Pool or comma-separated
        amenities = request.GET.getlist('amenity') or []
        if len(amenities) == 1 and ',' in amenities[0]:
            amenities = [a.strip() for a in amenities[0].split(',') if a.strip()]

        if amenities:
            # try to match by name first, fallback to id if numeric
            name_filters = [a for a in amenities if not a.isdigit()]
            id_filters = [int(a) for a in amenities if a.isdigit()]
            am_q = Q()
            if name_filters:
                am_q |= Q(amenities__name__in=name_filters)
            if id_filters:
                am_q |= Q(amenities__id__in=id_filters) | Q(amenities__amenity_id__in=id_filters)
            qs = qs.filter(am_q).distinct()

        # pagination
        page = request.GET.get('page', 1)
        paginator = Paginator(qs, 12)
        try:
            listings = paginator.page(page)
        except PageNotAnInteger:
            listings = paginator.page(1)
        except EmptyPage:
            listings = paginator.page(paginator.num_pages)

    except Exception:
        # If models are not available or queries fail, render an empty listing page
        listings = []

    context = {
        'listings': listings,
        'filters': {
            'q': request.GET.get('q', ''),
            'city': request.GET.get('city', ''),
            'district': request.GET.get('district', ''),
            'min_price': request.GET.get('min_price', ''),
            'max_price': request.GET.get('max_price', ''),
            'amenity': request.GET.getlist('amenity') or [],
        }
    }

    return render(request, 'app/pages/category.html', context)
