from django.contrib import admin

# Register your models here.
from .models import Room, Review

admin.site.register(Room)
admin.site.register(Review)