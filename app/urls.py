from django.urls import path
from . import views
from .views import payment_views
from django.contrib.auth import views as auth_views
from app.views.auth_views import login_view, logout_view


from .views.admin_api import booking_total_price, listing_price, listing_detail, revenue_statistics
from .views.availability_views import check_availability
from django.conf import settings
from django.conf.urls.static import static

from app.views.bnb_information import listing_detail
from app.views.auth_views import verify_otp





urlpatterns = [
    path('', views.home_view, name='home'),
    path('search/', views.search_results, name='search_results'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    path('verify-otp/', verify_otp, name='verify_otp'),


    path('profile/', views.user_profile , name='profile'),
    path('profile/edit/', views.edit_profile , name='profile_edit'),
    path('profile/trips/', views.profile_trips, name='profile_trips'),
    path('profile/host/', views.profile_host, name='profile_host'),
    path('profile/host-bookings/', views.profile_host_bookings, name='profile_host_bookings'),




    path('become-host/', views.taobaidang, name='become_host'),
    path('taobaidang/', views.taobaidang, name='taobaidang'),

    path('buoc1/', views.buoc1, name='buoc1'),
    path('loaichoo/', views.loaichoo, name='loaichoo'),
    path('dattieude/', views.dattieude, name='dattieude'),
    path('trungtamtrogiup/', views.trungtamtrogiup, name='trungtamtrogiup'),
    path('datphong/', views.datphong, name='datphong'),  # ?room=123
    path('phuongthucthanhtoan/', views.phuongthucthanhtoan, name='phuongthucthanhtoan'),
    path('chinhsachdieukhoan/', views.chinhsachdieukhoan, name='chinhsachdieukhoan'),


    path("chitietnoio/<int:listing_id>/", listing_detail, name="chitietnoio"),

 

    path(
    'forgot-password/',
    auth_views.PasswordResetView.as_view(
        template_name='app/auth_template/forgot-password.html',
        email_template_name='registration/password_reset_email.html',
        success_url='/forgot-password/',
    ),
    name='forgot_password'
),





    path('buoc2/', views.buoc2, name='buoc2'),
    path('duocuse/', views.duocuse, name='duocuse'),
    path('thoigianthue/', views.thoigianthue, name='thoigianthue'),
    path('themanh/', views.themanh, name='themanh'),
    path('thongtincb/', views.thongtincb, name='thongtincb'),
    path('tiennghii/', views.tiennghii, name='tiennghii'),
    path('tieude/', views.tieude, name='tieude'),
    path('diachi/', views.diachi, name='diachi'),
    path('buoc3/', views.buoc3, name='buoc3'),
    path('thietlapgia/', views.thietlapgia, name='thietlapgia'),
    path('giacuoituan/', views.giacuoituan, name='giacuoituan'),
    path('chiasett/', views.chiasett, name='chiasett'),

    
    path(
    'booking/history/',
    views.user_booking_history,
    name='user_booking_history'),

    



    # Của quên mk
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='app/auth_template/password_reset_confirm.html'
        ),
        name='password_reset_confirm'
    ),

    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='app/auth_template/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),


    # Payment (mock) endpoints
    path('payment/start/<int:booking_id>/', payment_views.payment_start, name='payment_start'),
    path('payment/success/<int:booking_id>/', payment_views.payment_success, name='payment_success'),
    path('payment/cancel/<int:booking_id>/', payment_views.payment_cancel, name='payment_cancel'),
    path('payment/create-and-pay/<int:listing_id>/', payment_views.create_booking_and_pay, name='create_and_pay'),
    path('payment/vnpay/create/<int:booking_id>/', payment_views.vnpay_create, name='vnpay_create'),
    path('payment/vnpay/return/', payment_views.vnpay_return, name='vnpay_return'),
    path('payment/vnpay/ipn/', payment_views.vnpay_ipn, name='vnpay_ipn'),

    # Admin AJAX: get booking total price
    path('admin-api/booking/<int:booking_id>/total/', booking_total_price, name='admin_booking_total'),
    path('admin-api/revenue-statistics/', revenue_statistics, name='admin_revenue_statistics'),
        path('api/price/', listing_price, name='listing-price'),
        path('api/listing/', listing_detail, name='listing-detail'),
        path('api/check-availability/', check_availability, name='check-availability'),
    # Create booking (user)
    path('booking/create/<int:listing_id>/', views.create_booking, name='create_booking'),
    path('booking/success/<int:booking_id>/', views.booking_success, name='booking_success'),
    path('booking/cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('booking/history/', views.user_booking_history, name='user_booking_history'),
    # Complaints (UI)
    path('complaints/', views.complaint_list, name='complaint_list'),
    path('complaints/create/<int:booking_id>/', views.complaint_create, name='complaint_create'),







]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
