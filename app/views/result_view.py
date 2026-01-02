from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Avg, Count
from datetime import datetime


def search_results(request):
    """Run search across listings and render results.

    GET params supported:
    - location: city/district search
    - check_in, check_out: date range
    - adults, children, infants, pets: guest counts
    - min_price, max_price
    - amenity (list or comma-separated)
    - room_type (list)
    - sort: price_asc, price_desc, newest, rating
    - page
    """
    listings = []
    try:
        from app.models import Listing, Amenity

        # Start with active & approved listings
        qs = Listing.objects.filter(is_active=True, status='approved').select_related(
            'listingaddress', 'host'
        ).prefetch_related(
            'images', 'amenities'
        ).annotate(
            average_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        )

        # Location search
        location = request.GET.get('location', '').strip()
        if location:
            # Search in both city and district
            qs = qs.filter(
                Q(listingaddress__city__icontains=location) |
                Q(listingaddress__district__icontains=location)
            )

        # Date-based availability - exclude listings with conflicting bookings
        check_in = request.GET.get('check_in', '').strip()
        check_out = request.GET.get('check_out', '').strip()
        
        if check_in and check_out:
            try:
                check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
                check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()
                
                # Find listings with conflicting confirmed bookings
                from app.models import Booking
                conflicting_booking_listings = Booking.objects.filter(
                    booking_status='confirmed'
                ).exclude(
                    # No overlap if: booking ends before check_in OR starts after check_out
                    Q(check_out__lte=check_in_date) | Q(check_in__gte=check_out_date)
                ).values_list('listing_id', flat=True).distinct()
                
                # Exclude those listings from results
                qs = qs.exclude(listing_id__in=list(conflicting_booking_listings))
            except (ValueError, TypeError):
                pass  # Invalid date format, skip filtering
        
        # Guest capacity filters
        adults = request.GET.get('adults', '0')
        children = request.GET.get('children', '0')
        try:
            adults_count = int(adults)
            children_count = int(children)
            total_guests = adults_count + children_count
            
            if total_guests > 0:
                qs = qs.filter(max_adults__gte=adults_count)
                if children_count > 0:
                    qs = qs.filter(max_children__gte=children_count)
        except (ValueError, TypeError):
            pass

        # Pets filter
        pets = request.GET.get('pets', '0')
        try:
            pets_count = int(pets)
            if pets_count > 0:
                qs = qs.filter(max_pets__gte=pets_count)
        except (ValueError, TypeError):
            pass

        # Price range
        min_price = request.GET.get('min_price', '').strip()
        if min_price:
            try:
                qs = qs.filter(price_per_night__gte=float(min_price))
            except (ValueError, TypeError):
                pass

        max_price = request.GET.get('max_price', '').strip()
        if max_price:
            try:
                qs = qs.filter(price_per_night__lte=float(max_price))
            except (ValueError, TypeError):
                pass

        # Amenities filter
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
                am_q |= Q(amenities__amenity_id__in=id_filters)
            qs = qs.filter(am_q).distinct()

        # Sorting
        sort = request.GET.get('sort', 'newest')
        if sort == 'price_asc':
            qs = qs.order_by('price_per_night')
        elif sort == 'price_desc':
            qs = qs.order_by('-price_per_night')
        elif sort == 'rating':
            qs = qs.order_by('-average_rating', '-review_count')
        else:  # newest or default
            qs = qs.order_by('-created_at')

        # Pagination
        page = request.GET.get('page', 1)
        paginator = Paginator(qs, 12)
        try:
            listings = paginator.page(page)
        except PageNotAnInteger:
            listings = paginator.page(1)
        except EmptyPage:
            listings = paginator.page(paginator.num_pages)

        # Get all amenities for filter
        all_amenities = Amenity.objects.all().order_by('name')

    except Exception as e:
        print(f"Search error: {e}")
        listings = []
        all_amenities = []

    context = {
        'listings': listings,
        'available_amenities': all_amenities,
        'filters': {
            'location': location,
            'check_in': check_in,
            'check_out': check_out,
            'adults': request.GET.get('adults', ''),
            'children': request.GET.get('children', ''),
            'infants': request.GET.get('infants', ''),
            'pets': request.GET.get('pets', ''),
            'min_price': min_price,
            'max_price': max_price,
            'amenity': amenities,
            'sort': sort,
        }
    }

    return render(request, 'app/pages/search_results.html', context)
