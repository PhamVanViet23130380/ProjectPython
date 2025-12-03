from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('taobaidang/', views.taobaidang, name='taobaidang'),
    path('chitietnoio/', views.chitietnoio, name='chitietnoio'),
]
