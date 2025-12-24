from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q


def search_results(request):
    """Run search across listings and render results.

    GET params supported:
    - q: text search
    - city, district
    - min_price, max_price
    - amenity (list or comma-separated)
    - sort: price_asc, price_desc, newest, rating
    - page
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

        amenities = request.GET.getlist('amenity') or []
        if len(amenities) == 1 and ',' in amenities[0]:
            amenities = [a.strip() for a in amenities[0].split(',') if a.strip()]

        if amenities:
            am_q = Q()
            name_filters = [a for a in amenities if not a.isdigit()]
            id_filters = [int(a) for a in amenities if a.isdigit()]
            if name_filters:
                am_q |= Q(amenities__name__in=name_filters)
            if id_filters:
                am_q |= Q(amenities__id__in=id_filters) | Q(amenities__amenity_id__in=id_filters)
            qs = qs.filter(am_q).distinct()

        # sorting
        sort = request.GET.get('sort')
        if sort == 'price_asc':
            qs = qs.order_by('price_per_night')
        elif sort == 'price_desc':
            qs = qs.order_by('-price_per_night')
        elif sort == 'newest':
            qs = qs.order_by('-created_at')

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
        listings = []

    context = {
        'listings': listings,
        'query': request.GET.get('q', ''),
        'filters': {
            'city': request.GET.get('city', ''),
            'district': request.GET.get('district', ''),
            'min_price': request.GET.get('min_price', ''),
            'max_price': request.GET.get('max_price', ''),
            'amenity': request.GET.getlist('amenity') or [],
            'sort': request.GET.get('sort', ''),
        }
    }

    return render(request, 'app/pages/search_results.html', context)
