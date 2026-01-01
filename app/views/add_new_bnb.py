from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from decimal import Decimal, InvalidOperation


@login_required
def create_listing(request):
    """Allow hosts to create a new Listing with address, images and amenities.

    Expected POST fields (simple form):
    - title, description, price_per_night, max_adults, max_children, max_pets
    - city, district, street, latitude, longitude
    - amenities (comma-separated names or repeated inputs)
    - images (comma-separated URLs)
    """
    try:
        from .models import Listing, ListingAddress, ListingImage, Amenity, ListingAmenity
    except Exception:
        messages.error(request, 'Models unavailable')
        return redirect('home')

    if getattr(request.user, 'role', None) == 'ADMIN':
        messages.error(request, 'Admin không thể tạo listing')
        return redirect('home')
    

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        price_raw = request.POST.get('price_per_night', '').strip()
        max_adults = request.POST.get('max_adults')
        max_children = request.POST.get('max_children') or 0
        max_pets = request.POST.get('max_pets') or 0

        city = request.POST.get('city', '').strip()
        district = request.POST.get('district', '').strip()
        street = request.POST.get('street', '').strip()
        lat_raw = request.POST.get('latitude')
        lon_raw = request.POST.get('longitude')

        amenities_raw = request.POST.getlist('amenities') or request.POST.get('amenities', '')
        if isinstance(amenities_raw, str):
            amenities = [a.strip() for a in amenities_raw.split(',') if a.strip()]
        else:
            amenities = [a.strip() for a in amenities_raw if a.strip()]

        images_raw = request.POST.get('images', '')
        images = [u.strip() for u in images_raw.split(',') if u.strip()]

        if not title or not description:
            messages.error(request, 'Vui lòng cung cấp tiêu đề và mô tả')
            return redirect('add_new_bnb')


        if not price_raw:
            messages.error(request, 'Vui lòng nhập giá mỗi đêm')
            return redirect('add_new_bnb')
        
        try:
            price_per_night = Decimal(price_raw) 
            if price_per_night <= 0:
                raise InvalidOperation
        except (InvalidOperation, TypeError):
            messages.error(request, 'Giá không hợp lệ')
            return redirect('add_new_bnb')

        try:
            max_adults = int(max_adults)
            max_children = int(max_children)
            max_pets = int(max_pets)
            if max_adults < 1 :
                raise ValueError
        except Exception:
            messages.error(request, 'Số người/đồ không hợp lệ')
            return redirect('add_new_bnb')

        try:
            latitude = Decimal(lat_raw) if lat_raw else None
            longitude = Decimal(lon_raw) if lon_raw else None
        except Exception:
            latitude = None
            longitude = None

        # Create objects inside a transaction
        try:
            with transaction.atomic():
                listing = Listing.objects.create(
                    host=request.user,
                    title=title,
                    description=description,
                    price_per_night=price_per_night,
                    max_adults=max_adults,
                    max_children=max_children,
                    max_pets=max_pets,
                    is_active=True,
                )

                # address
                ListingAddress.objects.create(
                    listing=listing,
                    city=city,
                    district=district,
                    street=street,
                    latitude=latitude,
                    longitude=longitude,
                )

                # images
                for idx, url in enumerate(images):
                    ListingImage.objects.create(listing=listing, image_url=url, is_main=(idx == 0))

                # amenities: find or create then link via through model
                for name in amenities:
                    if not name:
                        continue
                    # allow numeric ids
                    amenity = None
                    try:
                        if name.isdigit():
                            amenity = Amenity.objects.filter(amenity_id=int(name)).first()
                    except Exception:
                        amenity = None
                    if amenity is None:
                        amenity, _ = Amenity.objects.get_or_create(name=name)

                    # create through relation
                    try:
                        ListingAmenity.objects.get_or_create(listing=listing, amenity=amenity)
                    except Exception:
                        # fallback: try m2m add
                        try:
                            listing.amenities.add(amenity)
                        except Exception:
                            pass

            messages.success(request, 'Tạo listing thành công')
            return redirect('listing_detail', listing_id=getattr(listing, 'listing_id', listing.pk))
        except Exception as exc:
            messages.error(request, f'Không thể tạo listing: {exc}')
            return redirect('add_new_bnb')

    # GET: render a simple form template
    return render(request, 'app/pages/create-new-bnb.html')
