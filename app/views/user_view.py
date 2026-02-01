from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.timezone import now
from django.utils import timezone
from django.db.models import Sum, Avg, Count, F
from django.db.models.functions import ExtractMonth, ExtractYear, Coalesce
from django.http import JsonResponse
from decimal import Decimal
import json
from app.models import Booking, Review, Listing, User



from django.shortcuts import render

@login_required
def profile_host_bookings(request):
    bookings = Booking.objects.filter(
        listing__host=request.user
    ).select_related('listing', 'user')

    return render(request, 'app/user/profile_host_bookings.html', {
        'bookings': bookings
    })




def build_profile_stats(user):
    bookings = Booking.objects.filter(user=user)

    return {
        'total_trips': bookings.count(),

        'upcoming_trips': bookings.filter(
            booking_status='confirmed' ,
            check_in__gt=now().date()   # ← PHẢI là check_in
        ).count(),

        'completed_trips': bookings.filter(
            booking_status='completed'
        ).count(),

        'total_spent': bookings.filter(
            booking_status='completed'
        ).aggregate(total=Sum('base_price'))['total'] or 0,

        'avg_rating': (
            Review.objects.filter(listing__host=user)
            .aggregate(avg=Avg('rating'))['avg']
            if hasattr(user, 'listings') and user.listings.exists()
            else None
        )
    }






def user_profile(request, username=None):
    """Display a user's public profile.

    If `username` is None, show the current user's profile (login required).
    """

    if username is None:
        if not request.user.is_authenticated:
            messages.error(request, 'Vui lòng đăng nhập để xem hồ sơ')
            return redirect('login')
        user = request.user
    else:
        user = get_object_or_404(User, username=username)

    is_owner = request.user.is_authenticated and request.user.id == user.id

    # expose a minimal public context
    public_info = {
        'username': getattr(user, 'username', ''),
        'full_name': getattr(user, 'full_name', '') if hasattr(user, 'full_name') else getattr(user, 'get_full_name', lambda: '')(),
        'profile_photo': getattr(user, 'profile_photo', None),
        'bio': getattr(user, 'bio', '') if hasattr(user, 'bio') else '',
    }

    stats = build_profile_stats(user)


    return render(request, 'app/user/profile.html', {'profile_user': user, 'public': public_info, 
            'is_owner': is_owner,
            **stats,})


@login_required
def edit_profile(request):
    user = request.user

    if request.method == 'POST':
        user.full_name = request.POST.get('full_name')
        user.phone_number = request.POST.get('phone_number')

        if 'avatar' in request.FILES:
            user.avatar = request.FILES['avatar']

        user.save()
        return redirect('profile')

    stats = build_profile_stats(user)

    return render(
        request,
        'app/user/profile.html',
        {
            'edit_mode': True,
            'profile_user': user,
            **stats
        }
    )


def user_listings(request, username=None):
    """List listings for a user. If `username` omitted, use current user (login required)."""
    if username is None:
        if not request.user.is_authenticated:
            messages.error(request, 'Vui lòng đăng nhập để xem danh sách của bạn')
            return redirect('login')
        owner = request.user
    else:
        owner = get_object_or_404(User, username=username)

    qs = Listing.objects.filter(host=owner).order_by('-created_at')
    page = request.GET.get('page', 1)
    paginator = Paginator(qs, 12)
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(request, 'app/pages/user_listings.html', {'page_obj': page_obj, 'owner': owner})


@login_required
def user_bookings(request):
    """Show bookings for current authenticated user."""
    qs = Booking.objects.filter(user=request.user).order_by('-check_in')
    page = request.GET.get('page', 1)
    paginator = Paginator(qs, 12)
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(request, 'app/pages/user_bookings.html', {'page_obj': page_obj})


@login_required
def profile_trips(request):
    today = now().date()

    bookings = Booking.objects.filter(user=request.user)

    upcoming = bookings.filter(
        booking_status='confirmed',
        check_in__gt=today
    )

    ongoing = bookings.filter(
        booking_status__in=['confirmed', 'in_progress'],
        check_in__lte=today,
        check_out__gte=today
    )

    completed = bookings.filter(
        booking_status='completed'
    )

    return render(
        request,
        'app/user/profile_trips.html',
        {
            'upcoming': upcoming,
            'ongoing': ongoing,
            'completed': completed,
        }
    )

@login_required
def profile_host(request):
    user = request.user

    # Listings của host (prefetch ảnh để đỡ query)
    listings = user.listings.prefetch_related('images')

    total_listings = listings.count()

    # Booking cho các listing của host
    bookings = Booking.objects.filter(listing__host=user)

    total_bookings = bookings.exclude(
        booking_status='cancelled'
    ).count()

    # Tính doanh thu: base_price - service_fee (tiền host thực nhận)
    completed_bookings = bookings.filter(booking_status='completed')
    total_revenue = Decimal('0')
    for b in completed_bookings:
        base = b.base_price or Decimal('0')
        fee = b.service_fee or Decimal('0')
        total_revenue += (base - fee)

    avg_rating = Review.objects.filter(
        listing__host=user
    ).aggregate(avg=Avg('rating'))['avg'] or None

    return render(
        request,
        'app/user/profile_host.html',
        {
            'listings': listings,
            'total_listings': total_listings,
            'total_bookings': total_bookings,
            'total_revenue': total_revenue,
            'avg_rating': avg_rating,
            'is_host': True,
        }
    )


@login_required
def host_revenue_statistics(request):
    """Thống kê doanh thu của host theo tháng/năm."""
    user = request.user
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
        listing__host=user,
        booking_status='completed'
    ).annotate(
        year=ExtractYear('created_at')
    ).values('year').distinct().order_by('-year')
    
    available_years = [y['year'] for y in years_qs if y['year']]
    if current_year not in available_years:
        available_years.insert(0, current_year)
    available_years = sorted(set(available_years), reverse=True)
    
    # Lấy booking đã hoàn thành trong năm được chọn
    bookings_year = Booking.objects.filter(
        listing__host=user,
        booking_status='completed',
        created_at__year=selected_year
    )
    
    # Tính tổng doanh thu năm (base_price - service_fee)
    total_revenue_year = Decimal('0')
    for b in bookings_year:
        base = b.base_price or Decimal('0')
        fee = b.service_fee or Decimal('0')
        total_revenue_year += (base - fee)
    
    total_bookings_year = bookings_year.count()
    
    # Doanh thu tháng hiện tại
    bookings_month = Booking.objects.filter(
        listing__host=user,
        booking_status='completed',
        created_at__year=current_year,
        created_at__month=current_month
    )
    total_revenue_month = Decimal('0')
    for b in bookings_month:
        base = b.base_price or Decimal('0')
        fee = b.service_fee or Decimal('0')
        total_revenue_month += (base - fee)
    total_bookings_month = bookings_month.count()
    
    # Thống kê theo tháng trong năm được chọn
    monthly_data = []
    for m in range(1, 13):
        month_bookings = bookings_year.filter(created_at__month=m)
        month_revenue = Decimal('0')
        for b in month_bookings:
            base = b.base_price or Decimal('0')
            fee = b.service_fee or Decimal('0')
            month_revenue += (base - fee)
        monthly_data.append({
            'month': m,
            'revenue': float(month_revenue),
            'count': month_bookings.count()
        })
    
    # Tính trung bình doanh thu/tháng
    months_with_data = len([m for m in monthly_data if m['revenue'] > 0])
    avg_revenue_per_month = float(total_revenue_year) / months_with_data if months_with_data > 0 else 0
    
    # Dữ liệu cho biểu đồ
    monthly_labels = [f"Tháng {m}" for m in range(1, 13)]
    monthly_values = [m['revenue'] for m in monthly_data]
    
    context = {
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
        'is_host': True,
    }
    
    return render(request, 'app/user/host_revenue_statistics.html', context)
