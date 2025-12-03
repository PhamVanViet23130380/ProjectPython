from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('experience/', views.experience, name='experience'),
    path('dich-vu/', views.service, name='service'),
    path('login/', views.login_view, name='login'),
]
