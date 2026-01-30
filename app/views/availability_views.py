from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from datetime import datetime

from ..models import Booking, Listing


def check_availability(request):
    """
    API endpoint to check if a listing is available for given dates.
    
    Query params: 
    - listing (id)
    - checkin (YYYY-MM-DD)
    - checkout (YYYY-MM-DD)
    
    Returns JSON: {'available': true/false, 'error': 'message' (if any)}
    """
    listing_id = request.GET.get('listing') or request.GET.get('room')
    checkin = request.GET.get('checkin')
    checkout = request.GET.get('checkout')

    print(f"[CHECK AVAILABILITY] listing_id={listing_id}, checkin={checkin}, checkout={checkout}")

    # Validate inputs
    if not listing_id or not checkin or not checkout:
        print("[CHECK AVAILABILITY] Missing params")
        return JsonResponse({'available': False, 'error': 'Thiếu thông tin listing hoặc ngày.'}, status=400)

    # Get listing
    try:
        listing = get_object_or_404(Listing, listing_id=int(listing_id))
        print(f"[CHECK AVAILABILITY] Found listing: {listing.title}")
    except Exception as e:
        print(f"[CHECK AVAILABILITY] Listing not found: {e}")
        return JsonResponse({'available': False, 'error': 'Không tìm thấy chỗ ở.'}, status=400)

    # Check if listing is active
    if not listing.is_active:
        print("[CHECK AVAILABILITY] Listing not active")
        return JsonResponse({'available': False, 'error': 'Chỗ ở này hiện không còn hoạt động.'})

    # Parse dates
    try:
        checkin_date = datetime.strptime(checkin, '%Y-%m-%d').date()
        checkout_date = datetime.strptime(checkout, '%Y-%m-%d').date()
        print(f"[CHECK AVAILABILITY] Parsed dates: checkin={checkin_date}, checkout={checkout_date}")
    except Exception as e:
        print(f"[CHECK AVAILABILITY] Date parse error: {e}")
        return JsonResponse({'available': False, 'error': 'Định dạng ngày không hợp lệ.'}, status=400)

    # Validate dates
    from datetime import date
    today = date.today()
    
    if checkin_date < today:
        print(f"[CHECK AVAILABILITY] Checkin in past: {checkin_date} < {today}")
        return JsonResponse({'available': False, 'error': 'Ngày nhận phòng phải từ hôm nay trở đi.'})
    
    if checkout_date <= checkin_date:
        print(f"[CHECK AVAILABILITY] Invalid date range: checkout {checkout_date} <= checkin {checkin_date}")
        return JsonResponse({'available': False, 'error': 'Ngày trả phải lớn hơn ngày nhận.'})


    # Validate against listing available window (if set)
    if listing.available_from and listing.available_to and listing.available_from > listing.available_to:
        print("[CHECK AVAILABILITY] Invalid listing availability window")
        return JsonResponse({'available': False, 'error': 'Khoang thoi gian cho thue khong hop le.'}, status=400)

    if listing.available_from and checkin_date < listing.available_from:
        return JsonResponse({'available': False, 'error': 'Ngay nhan phong phai tu ngay bat dau cho thue.'})

    if listing.available_to and checkout_date > listing.available_to:
        return JsonResponse({'available': False, 'error': 'Ngay tra phong khong duoc sau ngay ket thuc cho thue.'})

    # Check for overlapping bookings
    # Get all non-cancelled bookings for this listing
    existing_bookings = Booking.objects.filter(
        listing=listing
    ).exclude(
        booking_status='cancelled'
    )

    print(f"[CHECK AVAILABILITY] Found {existing_bookings.count()} non-cancelled bookings")

    # Check for overlap
    for booking in existing_bookings:
        print(f"[CHECK AVAILABILITY] Checking booking #{booking.booking_id}: {booking.check_in} to {booking.check_out}, status={booking.booking_status}")
        # Two bookings overlap if they are NOT (one ends before the other starts)
        # Overlap: NOT (booking.check_out <= checkin_date OR booking.check_in >= checkout_date)
        # Allow same-day checkout and checkin (checkout at 12:00, checkin at 14:00)
        if not (booking.check_out <= checkin_date or booking.check_in >= checkout_date):
            # Found overlapping booking
            print(f"[CHECK AVAILABILITY] OVERLAP FOUND with booking #{booking.booking_id}")
            return JsonResponse({
                'available': False,
                'error': f'Khoảng thời gian này đã có người đặt. Vui lòng chọn ngày khác.'
            })

    # No conflicts - available
    print("[CHECK AVAILABILITY] No conflicts - available!")
    return JsonResponse({
        'available': True,
        'message': 'Chỗ ở còn trống trong thời gian này.'
    })
