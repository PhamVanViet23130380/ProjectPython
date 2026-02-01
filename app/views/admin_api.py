from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count
from django.db.models.functions import ExtractMonth, ExtractYear
from django.utils import timezone
from datetime import datetime
import json

from ..models import Booking, Listing

from .payment_views import calculate_total_price


@staff_member_required
def revenue_statistics(request):
    """Admin view: Thống kê doanh thu phí dịch vụ từ booking đã hoàn thành."""
    current_year = timezone.now().year
    current_month = timezone.now().month
    
    # Lấy năm từ query param hoặc dùng năm hiện tại
    selected_year = request.GET.get('year')
    try:
        selected_year = int(selected_year)
    except (TypeError, ValueError):
        selected_year = current_year
    
    # Lấy danh sách các năm có booking
    years_qs = Booking.objects.filter(
        booking_status='confirmed'
    ).annotate(
        year=ExtractYear('created_at')
    ).values('year').distinct().order_by('-year')
    
    available_years = [y['year'] for y in years_qs if y['year']]
    if current_year not in available_years:
        available_years.insert(0, current_year)
    available_years = sorted(set(available_years), reverse=True)
    
    # Lấy booking đã hoàn thành trong năm được chọn
    bookings_year = Booking.objects.filter(
        booking_status='confirmed',
        created_at__year=selected_year
    )
    
    # Tổng doanh thu năm
    year_stats = bookings_year.aggregate(
        total_revenue=Sum('service_fee'),
        total_count=Count('booking_id')
    )
    total_revenue_year = year_stats['total_revenue'] or 0
    total_bookings_year = year_stats['total_count'] or 0
    
    # Doanh thu tháng hiện tại
    bookings_month = Booking.objects.filter(
        booking_status='confirmed',
        created_at__year=current_year,
        created_at__month=current_month
    )
    month_stats = bookings_month.aggregate(
        total_revenue=Sum('service_fee'),
        total_count=Count('booking_id')
    )
    total_revenue_month = month_stats['total_revenue'] or 0
    total_bookings_month = month_stats['total_count'] or 0
    
    # Thống kê theo tháng trong năm được chọn
    monthly_stats = bookings_year.annotate(
        month=ExtractMonth('created_at')
    ).values('month').annotate(
        revenue=Sum('service_fee'),
        count=Count('booking_id')
    ).order_by('month')
    
    # Tạo dữ liệu cho 12 tháng
    monthly_data = []
    monthly_revenue_dict = {item['month']: item for item in monthly_stats}
    
    for m in range(1, 13):
        if m in monthly_revenue_dict:
            monthly_data.append({
                'month': m,
                'revenue': float(monthly_revenue_dict[m]['revenue'] or 0),
                'count': monthly_revenue_dict[m]['count']
            })
        else:
            monthly_data.append({
                'month': m,
                'revenue': 0,
                'count': 0
            })
    
    # Tính trung bình doanh thu/tháng
    months_with_data = len([m for m in monthly_data if m['revenue'] > 0])
    avg_revenue_per_month = float(total_revenue_year) / months_with_data if months_with_data > 0 else 0
    
    # Dữ liệu cho biểu đồ
    monthly_labels = [f"Tháng {m}" for m in range(1, 13)]
    monthly_values = [m['revenue'] for m in monthly_data]
    
    context = {
        'title': 'Thống kê doanh thu',
        'selected_year': selected_year,
        'available_years': available_years,
        'total_revenue_year': total_revenue_year,
        'total_bookings_year': total_bookings_year,
        'total_revenue_month': total_revenue_month,
        'total_bookings_month': total_bookings_month,
        'avg_revenue_per_month': avg_revenue_per_month,
        'monthly_data': monthly_data,
        'monthly_labels': json.dumps(monthly_labels),
        'monthly_values': json.dumps(monthly_values),
    }
    
    return render(request, 'admin/revenue_statistics.html', context)


def booking_total_price(request, booking_id):
    """Return booking base amount (admin use previously required staff)."""
    booking = get_object_or_404(Booking, pk=booking_id)
    return JsonResponse({'base_price': str(booking.base_price)})


def listing_price(request):
    """Public API: calculate price breakdown for a listing.

    Query params: listing (id), checkin (YYYY-MM-DD), checkout (YYYY-MM-DD), guests (int)
    Returns JSON with keys: nights, base, service_fee, taxes, total
    (all strings for Decimal values).
    """
    listing_id = request.GET.get('listing') or request.GET.get('room')
    checkin = request.GET.get('checkin')
    checkout = request.GET.get('checkout')
    guests = request.GET.get('guests') or request.GET.get('guest') or request.GET.get('guests_count')

    try:
        listing = get_object_or_404(Listing, listing_id=int(listing_id))
    except Exception:
        return JsonResponse({'error': 'invalid listing'}, status=400)

    # parse guests
    try:
        guests = int(guests) if guests else 1
    except Exception:
        guests = 1

    # validate dates; rely on calculate_total_price to raise if invalid
    try:
        from datetime import datetime
        ci = datetime.strptime(checkin, '%Y-%m-%d').date() if checkin else None
        co = datetime.strptime(checkout, '%Y-%m-%d').date() if checkout else None
        if not ci or not co:
            return JsonResponse({'error': 'missing dates'}, status=400)
    except Exception:
        return JsonResponse({'error': 'invalid dates'}, status=400)

    try:
        breakdown = calculate_total_price(listing, ci, co, guests)
    except Exception as exc:
        return JsonResponse({'error': str(exc)}, status=400)

    # convert Decimal to string for JSON
    out = {k: (str(v) if hasattr(v, 'quantize') or isinstance(v, (int, float)) else str(v)) for k, v in breakdown.items()}
    return JsonResponse(out)


def listing_detail(request):
    """Return JSON details for a listing.

    Query params: listing (id) or room
    """
    listing_id = request.GET.get('listing') or request.GET.get('room')
    try:
        listing = Listing.objects.get(listing_id=int(listing_id))
    except Exception:
        return JsonResponse({'error': 'invalid listing'}, status=400)

    # build response
    images = [img.image_url for img in listing.images.all()[:10]]
    amenities = []
    for a in listing.amenities.all():
        amenities.append({'name': a.name})

    data = {
        'listing_id': listing.listing_id,
        'title': listing.title,
        'description': listing.description,
        'price_per_night': str(listing.price_per_night),
        'max_adults': listing.max_adults,
        'max_children': listing.max_children,
        'max_pets': listing.max_pets,
        'is_active': listing.is_active,
        'images': images,
        'amenities': amenities,
        # provide simple defaults for fields the frontend expects
        'rating': 5.0,
        'reviews': 0,
    }
    return JsonResponse(data)
