from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from app.models import Listing, ListingAddress, ListingImage, Amenity
from decimal import Decimal


@login_required
def step_loaichoo(request):
    """Bước 1: Chọn loại chỗ ở"""
    if request.method == 'POST':
        property_type = request.POST.get('property_type')
        request.session['listing_data'] = {'property_type': property_type}
        return redirect('duocuse')
    return render(request, 'app/host/loaichoo.html')


@login_required
def step_duocuse(request):
    """Bước 2: Khách được sử dụng loại chỗ ở nào"""
    if request.method == 'POST':
        usage_type = request.POST.get('usage_type')
        listing_data = request.session.get('listing_data', {})
        listing_data['usage_type'] = usage_type
        request.session['listing_data'] = listing_data
        return redirect('diachi')
    return render(request, 'app/host/duocuse.html')


@login_required
def step_diachi(request):
    """Bước 3: Địa chỉ"""
    if request.method == 'POST':
        listing_data = request.session.get('listing_data', {})
        listing_data['city'] = request.POST.get('city')
        listing_data['district'] = request.POST.get('district')
        listing_data['street'] = request.POST.get('street')
        request.session['listing_data'] = listing_data
        return redirect('thongtincb')
    return render(request, 'app/host/diachi.html')


@login_required
def step_thongtincb(request):
    """Bước 4: Thông tin cơ bản (số khách, phòng ngủ, giường, phòng tắm)"""
    if request.method == 'POST':
        listing_data = request.session.get('listing_data', {})
        listing_data['max_adults'] = int(request.POST.get('max_adults', 1))
        listing_data['max_children'] = int(request.POST.get('max_children', 0))
        listing_data['max_pets'] = int(request.POST.get('max_pets', 0))
        listing_data['bedrooms'] = int(request.POST.get('bedrooms', 1))
        listing_data['bathrooms'] = int(request.POST.get('bathrooms', 1))
        request.session['listing_data'] = listing_data
        return redirect('tiennghii')
    return render(request, 'app/host/thongtincb.html')


@login_required
def step_tiennghii(request):
    """Bước 5: Tiện nghi"""
    if request.method == 'POST':
        listing_data = request.session.get('listing_data', {})
        amenities = request.POST.getlist('amenities')  # Danh sách ID tiện nghi
        listing_data['amenities'] = amenities
        request.session['listing_data'] = listing_data
        return redirect('themanh')
    
    # Lấy danh sách tiện nghi có sẵn
    amenities = Amenity.objects.all()
    return render(request, 'app/host/tiennghii.html', {'amenities': amenities})


@login_required
def step_themanh(request):
    """Bước 6: Thêm ảnh"""
    if request.method == 'POST':
        listing_data = request.session.get('listing_data', {})
        images = request.POST.getlist('images')  # Danh sách URL ảnh
        listing_data['images'] = images
        request.session['listing_data'] = listing_data
        return redirect('tieude')
    return render(request, 'app/host/themanh.html')


@login_required
def step_tieude(request):
    """Bước 7: Tiêu đề và mô tả"""
    if request.method == 'POST':
        listing_data = request.session.get('listing_data', {})
        listing_data['title'] = request.POST.get('title')
        listing_data['description'] = request.POST.get('description')
        request.session['listing_data'] = listing_data
        return redirect('thietlapgia')
    return render(request, 'app/host/tieude.html')


@login_required
def step_thietlapgia(request):
    """Bước 8: Thiết lập giá"""
    if request.method == 'POST':
        listing_data = request.session.get('listing_data', {})
        listing_data['price_per_night'] = request.POST.get('price_per_night')
        request.session['listing_data'] = listing_data
        return redirect('chiasett')
    return render(request, 'app/host/thietlapgia.html')


@login_required
def step_chiasett(request):
    """Bước 9: Xem lại và xuất bản"""
    listing_data = request.session.get('listing_data', {})
    
    if request.method == 'POST':
        # Tạo listing mới
        try:
            listing = Listing.objects.create(
                host=request.user,
                title=listing_data.get('title', 'Chưa có tiêu đề'),
                description=listing_data.get('description', 'Chưa có mô tả'),
                price_per_night=Decimal(listing_data.get('price_per_night', '0')),
                max_adults=listing_data.get('max_adults', 1),
                max_children=listing_data.get('max_children', 0),
                max_pets=listing_data.get('max_pets', 0),
                is_active=True
            )
            
            # Tạo địa chỉ
            ListingAddress.objects.create(
                listing=listing,
                city=listing_data.get('city', ''),
                district=listing_data.get('district', ''),
                street=listing_data.get('street', '')
            )
            
            # Thêm ảnh
            images = listing_data.get('images', [])
            for idx, img_url in enumerate(images):
                if img_url:
                    ListingImage.objects.create(
                        listing=listing,
                        image_url=img_url,
                        is_main=(idx == 0)  # Ảnh đầu tiên là ảnh chính
                    )
            
            # Thêm tiện nghi
            amenity_ids = listing_data.get('amenities', [])
            for amenity_id in amenity_ids:
                try:
                    amenity = Amenity.objects.get(amenity_id=amenity_id)
                    listing.amenities.add(amenity)
                except Amenity.DoesNotExist:
                    pass
            
            # Xóa session
            del request.session['listing_data']
            
            messages.success(request, f'Chúc mừng! Bài đăng "{listing.title}" đã được tạo thành công!')
            return redirect('home')
            
        except Exception as e:
            messages.error(request, f'Có lỗi xảy ra: {str(e)}')
            return redirect('chiasett')
    
    return render(request, 'app/host/chiasett.html', {'listing_data': listing_data})
