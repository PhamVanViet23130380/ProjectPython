from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from app.models import Listing, ListingAddress, ListingImage, Amenity
from decimal import Decimal
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os
import shutil


@login_required
def step_loaichoo(request):
    """Bước 1: Chọn loại chỗ ở"""
    if request.method == 'POST':
        property_type = request.POST.get('property_type')
        request.session['listing_data'] = {'property_type': property_type}
        return redirect('dattieude')
    return render(request, 'app/host/loaichoo.html')
@login_required
def step_dattieude(request):
    """Bước sau loaichoo: Đặt tiêu đề nhanh với CSS tieude"""
    if request.method == 'POST':
        listing_data = request.session.get('listing_data', {})
        listing_data['title'] = request.POST.get('title')
        request.session['listing_data'] = listing_data
        return redirect('duocuse')
    return render(request, 'app/host/dattieude.html')


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
        # Lưu tọa độ nếu có
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        if latitude and longitude:
            listing_data['latitude'] = latitude
            listing_data['longitude'] = longitude
        request.session['listing_data'] = listing_data
        return redirect('thoigianthue')  # Đi qua trang thời gian thuê
    return render(request, 'app/host/diachi.html')


@login_required
def step_thoigianthue(request):
    """Bước 4: Khoảng thời gian cho thuê"""
    if request.method == 'POST':
        listing_data = request.session.get('listing_data', {})
        listing_data['available_from'] = request.POST.get('available_from')
        listing_data['available_to'] = request.POST.get('available_to')
        request.session['listing_data'] = listing_data
        return redirect('thongtincb')  # Tiếp tục đến trang thông tin cơ bản
    return render(request, 'app/host/thoigianthue.html')


@login_required
def step_thongtincb(request):
    """Bước 4: Thông tin cơ bản (số khách, phòng ngủ, giường, phòng tắm)"""
    if request.method == 'POST':
        listing_data = request.session.get('listing_data', {})
        listing_data['max_adults'] = int(request.POST.get('max_adults', 1))
        listing_data['max_children'] = int(request.POST.get('max_children', 0))
        listing_data['max_pets'] = int(request.POST.get('max_pets', 0))
        listing_data['bedrooms'] = int(request.POST.get('bedrooms', 1))
        listing_data['beds'] = int(request.POST.get('beds', 1))
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
    
    # Lấy danh sách tiện nghi theo category
    context = {
        'basic_amenities': Amenity.objects.filter(category='basic'),
        'featured_amenities': Amenity.objects.filter(category='featured'),
        'safety_amenities': Amenity.objects.filter(category='safety'),
    }
    return render(request, 'app/host/tiennghii.html', context)


@login_required
def step_themanh(request):
    """Bước 6: Thêm ảnh"""
    if request.method == 'POST':
        listing_data = request.session.get('listing_data', {})
        files = request.FILES.getlist('images')
        if not files or len(files) < 5:
            messages.error(request, 'Vui lòng tải lên tối thiểu 5 ảnh.')
            return render(request, 'app/host/themanh.html')

        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'listing_images', 'staged', str(request.user.id)))
        saved_paths = []
        os.makedirs(fs.location, exist_ok=True)
        for f in files[:5]:
            filename = fs.save(f.name, f)
            rel_url = f"{settings.MEDIA_URL}listing_images/staged/{str(request.user.id)}/{filename}"
            saved_paths.append(rel_url)

        listing_data['images'] = saved_paths
        request.session['listing_data'] = listing_data
        return redirect('tieude')
    return render(request, 'app/host/themanh.html')


@login_required
def step_tieude(request):
    """Bước 7: Tiêu đề và mô tả"""
    if request.method == 'POST':
        listing_data = request.session.get('listing_data', {})
        # Trang tieude giờ chỉ nhận mô tả
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
            # Validate bắt buộc
            required_fields = [
                ('title', 'Tiêu đề'),
                ('description', 'Mô tả'),
                ('price_per_night', 'Giá mỗi đêm'),
            ]
            for key, label in required_fields:
                if not listing_data.get(key):
                    messages.error(request, f'Thiếu {label}. Vui lòng hoàn tất các bước trước đó.')
                    return redirect('chiasett')

            images = [u for u in listing_data.get('images', []) if u]
            if len(images) < 5:
                messages.error(request, 'Vui lòng tải lên tối thiểu 5 ảnh trước khi xuất bản.')
                return redirect('chiasett')

            listing = Listing.objects.create(
                host=request.user,
                title=listing_data.get('title', 'Chưa có tiêu đề'),
                description=listing_data.get('description', 'Chưa có mô tả'),
                property_type=listing_data.get('property_type', 'Nhà riêng'),
                usage_type=listing_data.get('usage_type', 'Toàn bộ nhà'),
                price_per_night=Decimal(listing_data.get('price_per_night', '0')),
                available_from=listing_data.get('available_from') or None,
                available_to=listing_data.get('available_to') or None,
                max_adults=listing_data.get('max_adults', 1),
                max_children=listing_data.get('max_children', 0),
                max_pets=listing_data.get('max_pets', 0),
                bedrooms=listing_data.get('bedrooms', 1),
                beds=listing_data.get('beds', 1),
                bathrooms=listing_data.get('bathrooms', 1),
                is_active=False,
                status='pending'
            )
            
            # Tạo địa chỉ
            address_data = {
                'listing': listing,
                'city': listing_data.get('city', ''),
                'district': listing_data.get('district', ''),
                'street': listing_data.get('street', '')
            }
            # Thêm tọa độ nếu có
            if listing_data.get('latitude') and listing_data.get('longitude'):
                try:
                    address_data['latitude'] = Decimal(listing_data.get('latitude'))
                    address_data['longitude'] = Decimal(listing_data.get('longitude'))
                except:
                    pass
            ListingAddress.objects.create(**address_data)
            
            # Thêm ảnh
            # Ảnh: di chuyển từ staged vào thư mục theo listing
            final_dir = os.path.join(settings.MEDIA_ROOT, 'listing_images', str(listing.listing_id))
            os.makedirs(final_dir, exist_ok=True)
            for idx, url in enumerate(images[:5]):
                if not url:
                    continue
                # url like 'media/listing_images/staged/<uid>/<filename>'
                # derive filesystem path
                # remove leading MEDIA_URL
                relative_path = url.replace(settings.MEDIA_URL, '').lstrip('/') if url.startswith(settings.MEDIA_URL) else url
                src_path = os.path.join(settings.MEDIA_ROOT, relative_path.replace('/', os.sep))
                fname = os.path.basename(src_path)
                dst_path = os.path.join(final_dir, fname)
                try:
                    shutil.move(src_path, dst_path)
                except Exception:
                    # fallback copy
                    try:
                        shutil.copy2(src_path, dst_path)
                    except Exception:
                        continue
                final_url = f"{settings.MEDIA_URL}listing_images/{str(listing.listing_id)}/{fname}"
                ListingImage.objects.create(
                    listing=listing,
                    image_url=final_url,
                    is_main=(idx == 0)
                )
            
            # Thêm tiện nghi
            amenity_ids = listing_data.get('amenities', [])
            for amenity_id in amenity_ids:
                try:
                    amenity = Amenity.objects.get(amenity_id=int(amenity_id))
                    listing.amenities.add(amenity)
                except (Amenity.DoesNotExist, ValueError, TypeError):
                    pass
            
            # Xóa session
            del request.session['listing_data']
            
            messages.success(request, f'Chúc mừng! Bài đăng "{listing.title}" đã được tạo thành công!')
            return redirect('home')
            
        except Exception as e:
            messages.error(request, f'Có lỗi xảy ra: {str(e)}')
            return redirect('chiasett')
    
    return render(request, 'app/host/chiasett.html', {'listing_data': listing_data})
