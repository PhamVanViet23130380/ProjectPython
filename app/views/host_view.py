from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from app.models import Listing, ListingAddress, ListingImage, Amenity #

@login_required
def taobaidang_view(request):
    # Trang bắt đầu, khởi tạo session trống
    request.session['temp_listing'] = {}
    return render(request, 'app/pages/taobaidang.html')

def buoc1_view(request):
    return render(request, 'app/pages/buoc1.html')

def loaichoo_view(request):
    if request.method == 'POST':
        data = request.session.get('temp_listing', {})
        data['property_type'] = request.POST.get('property_type')
        request.session['temp_listing'] = data
        return redirect('duocuse')
    return render(request, 'app/pages/loaichoo.html')

def duocuse_view(request):
    if request.method == 'POST':
        data = request.session.get('temp_listing', {})
        data['room_type'] = request.POST.get('room_type')
        request.session['temp_listing'] = data
        return redirect('diachi')
    return render(request, 'app/pages/duocuse.html')

def diachi_view(request):
    if request.method == 'POST':
        data = request.session.get('temp_listing', {})
        data.update({
            'city': request.POST.get('city'),
            'district': request.POST.get('district'),
            'street': request.POST.get('street'),
        })
        request.session['temp_listing'] = data
        return redirect('thongtincb')
    return render(request, 'app/pages/diachi.html')

def thongtincb_view(request):
    if request.method == 'POST':
        data = request.session.get('temp_listing', {})
        data.update({
            'max_adults': request.POST.get('guests'),
            'bedrooms': request.POST.get('bedrooms'),
            'beds': request.POST.get('beds'),
            'bathrooms': request.POST.get('bathrooms'),
        })
        request.session['temp_listing'] = data
        return redirect('buoc2')
    return render(request, 'app/pages/thongtincb.html')

def buoc2_view(request):
    return render(request, 'app/pages/buoc2.html')

def tiennghii_view(request):
    if request.method == 'POST':
        # Lấy danh sách ID tiện nghi người dùng đã chọn
        amenity_ids = request.POST.getlist('amenities')
        data = request.session.get('temp_listing', {})
        data['amenity_ids'] = amenity_ids
        request.session['temp_listing'] = data
        return redirect('themanh')
    return render(request, 'app/pages/tiennghii.html')

def themanh_view(request):
    if request.method == 'POST':
        # Đồ án nhanh: cho nhập URL ảnh, nếu xịn hơn thì dùng request.FILES
        data = request.session.get('temp_listing', {})
        data['image_urls'] = request.POST.getlist('image_urls')
        request.session['temp_listing'] = data
        return redirect('tieude')
    return render(request, 'app/pages/themanh.html')

def tieude_view(request):
    if request.method == 'POST':
        data = request.session.get('temp_listing', {})
        data['title'] = request.POST.get('title')
        request.session['temp_listing'] = data
        return redirect('buoc3')
    return render(request, 'app/pages/tieude.html')

def buoc3_view(request):
    return render(request, 'app/pages/buoc3.html')

def thietlapgia_view(request):
    if request.method == 'POST':
        data = request.session.get('temp_listing', {})
        data['price'] = request.POST.get('price')
        request.session['temp_listing'] = data
        return redirect('giacuoituan')
    return render(request, 'app/pages/thietlapgia.html')

def giacuoituan_view(request):
    return render(request, 'app/pages/giacuoituan.html')

def chiasett_view(request):
    if request.method == 'POST':
        data = request.session.get('temp_listing')
        
        # CHỐT HẠ: LƯU VÀO DATABASE
        # 1. Tạo Listing
        listing = Listing.objects.create(
            host=request.user,
            title=data.get('title'),
            description="Chỗ ở tuyệt vời",
            price_per_night=data.get('price'),
            max_adults=data.get('max_adults'),
            is_active=True
        )
        
        # 2. Tạo Địa chỉ
        ListingAddress.objects.create(
            listing=listing,
            city=data.get('city'),
            district=data.get('district'),
            street=data.get('street')
        )
        
        # 3. Tạo Ảnh
        for url in data.get('image_urls', []):
            ListingImage.objects.create(listing=listing, image_url=url, is_main=True)
            
        # 4. Gán Tiện nghi
        for aid in data.get('amenity_ids', []):
            listing.amenities.add(Amenity.objects.get(amenity_id=aid))
            
        # Xóa session sau khi xong
        del request.session['temp_listing']
        return redirect('home')
        
    return render(request, 'app/pages/chiasett.html')