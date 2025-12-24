from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.html import format_html

from .models import (
    Listing, ListingAddress, ListingImage, Amenity, ListingAmenity,
    Booking, Payment, Review, ReviewMedia, ReviewAnalysis, ReviewClassification,
    Message, Complaint, HostPolicy, Verification,
)

User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'username', 'full_name', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('email', 'username', 'full_name', 'phone_number')
    ordering = ('-id',)
    readonly_fields = ('date_joined',)


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('listing_id', 'title', 'host', 'price_per_night', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('title', 'description', 'host__email')
    raw_id_fields = ('host',)
    inlines = ()
    ordering = ('-created_at',)


@admin.register(ListingAddress)
class ListingAddressAdmin(admin.ModelAdmin):
    list_display = ('address_id', 'listing', 'city', 'district')
    search_fields = ('city', 'district', 'street')
    raw_id_fields = ('listing',)


class ListingImageInline(admin.TabularInline):
    model = ListingImage
    extra = 1


class ListingAmenityInline(admin.TabularInline):
    model = ListingAmenity
    extra = 1
    raw_id_fields = ('amenity',)

# attach inlines to ListingAdmin (assigned after classes are defined)
try:
    ListingAdmin.inlines = (ListingImageInline, ListingAmenityInline)
except NameError:
    # If ListingAdmin not yet defined, it'll be set later when module fully loads
    pass


@admin.register(ListingImage)
class ListingImageAdmin(admin.ModelAdmin):
    list_display = ('image_id', 'listing', 'is_main', 'thumbnail')
    list_filter = ('is_main',)
    raw_id_fields = ('listing',)

    def thumbnail(self, obj):
        if obj.image_url:
            return format_html('<img src="{}" style="height:40px;"/>', obj.image_url)
        return ""
    thumbnail.short_description = 'Thumb'


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ('amenity_id', 'name')
    search_fields = ('name',)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_id', 'listing', 'user', 'check_in', 'check_out', 'booking_status', 'total_price', 'created_at')
    list_filter = ('booking_status',)
    search_fields = ('listing__title', 'user__email')
    raw_id_fields = ('listing', 'user')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'booking', 'method', 'amount', 'status', 'paid_at')
    list_filter = ('status', 'method')
    raw_id_fields = ('booking',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('review_id', 'listing', 'user', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('listing__title', 'user__email', 'comment')
    raw_id_fields = ('booking', 'listing', 'user')


@admin.register(ReviewMedia)
class ReviewMediaAdmin(admin.ModelAdmin):
    list_display = ('media_id', 'review', 'media_type')
    raw_id_fields = ('review',)


@admin.register(ReviewAnalysis)
class ReviewAnalysisAdmin(admin.ModelAdmin):
    list_display = ('analysis_id', 'review', 'sentiment', 'confidence_score', 'analyzed_at')
    raw_id_fields = ('review',)


@admin.register(ReviewClassification)
class ReviewClassificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'review', 'spam_status')
    list_filter = ('spam_status',)
    raw_id_fields = ('review',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('message_id', 'sender', 'receiver', 'created_at')
    raw_id_fields = ('sender', 'receiver')
    search_fields = ('content',)


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('complaint_id', 'user', 'listing', 'status', 'created_at')
    list_filter = ('status',)
    raw_id_fields = ('user', 'listing')


@admin.register(HostPolicy)
class HostPolicyAdmin(admin.ModelAdmin):
    list_display = ('policy_id', 'host', 'warning_count', 'is_suspended', 'updated_at')
    raw_id_fields = ('host',)


@admin.register(Verification)
class VerificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'account', 'verify_type', 'created_at', 'expired_at')
    raw_id_fields = ('account',)
 