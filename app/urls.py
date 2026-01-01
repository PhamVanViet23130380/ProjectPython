from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from app.views.bnb_information import listing_detail


urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('become-host/', views.taobaidang, name='become_host'),
    path('taobaidang/', views.taobaidang, name='taobaidang'),

    path('buoc1/', views.buoc1, name='buoc1'),
    path('loaichoo/', views.loaichoo, name='loaichoo'),
    path('trungtamtrogiup/', views.trungtamtrogiup, name='trungtamtrogiup'),
    path('datphong/', views.datphong, name='datphong'),
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
    path('themanh/', views.themanh, name='themanh'),
    path('thongtincb/', views.thongtincb, name='thongtincb'),
    path('tiennghii/', views.tiennghii, name='tiennghii'),
    path('tieude/', views.tieude, name='tieude'),
    path('diachi/', views.diachi, name='diachi'),
    path('buoc3/', views.buoc3, name='buoc3'),
    path('thietlapgia/', views.thietlapgia, name='thietlapgia'),
    path('giacuoituan/', views.giacuoituan, name='giacuoituan'),
    path('chiasett/', views.chiasett, name='chiasett'),
    



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



]
