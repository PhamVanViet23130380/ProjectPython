from app.models import Listing
from django.shortcuts import render

def home_view(request):
    # Lấy toàn bộ dữ liệu kèm quan hệ địa chỉ và ảnh
    listings = Listing.objects.filter(is_active=True, status='approved').select_related('listingaddress').prefetch_related('images')
    
    context = {
        'hcm_listings': listings.filter(listingaddress__city__icontains="Hồ Chí Minh"),
        'hanoi_listings': listings.filter(listingaddress__city__icontains="Hà Nội"),
        'dalat_listings': listings.filter(listingaddress__city__icontains="Đà Lạt"),
        'danang_listings': listings.filter(listingaddress__city__icontains="Đà Nẵng"),
        'vangiang_listings': listings.filter(listingaddress__district__icontains="Văn Giang"),
        'other_listings': listings.exclude(listingaddress__city__icontains="Hồ Chí Minh")
                                  .exclude(listingaddress__city__icontains="Hà Nội")
                                  .exclude(listingaddress__city__icontains="Đà Lạt")
                                  .exclude(listingaddress__city__icontains="Đà Nẵng"),
    }
    return render(request, 'app/pages/home.html', context)