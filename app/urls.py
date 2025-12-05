from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('taobaidang/', views.taobaidang, name='taobaidang'),
    path('chitietnoio/', views.chitietnoio, name='chitietnoio'),
    path('buoc1/', views.buoc1, name='buoc1'),
    path('loaichoo/', views.loaichoo, name='loaichoo'),
    path('trungtamtrogiup/', views.trungtamtrogiup, name='trungtamtrogiup'),
    path('datphong/', views.datphong, name='datphong'),
    path('timhosthotrop/', views.timhosthotrop, name='timhosthotrop'),
    path('phuongthucthanhtoan/', views.phuongthucthanhtoan, name='phuongthucthanhtoan'),
    path('chinhsachdieukhoản/', views.chinhsachdieukhoản, name='chinhsachdieukhoản'),
]
