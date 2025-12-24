from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from .models import (
    Listing, ListingAddress, ListingImage, Amenity, ListingAmenity,
    Booking, Payment, Review, ReviewMedia, ReviewAnalysis,
    Message, Complaint, HostPolicy
)

User = get_user_model()

# --- CẤU HÌNH CHUNG CHO TOÀN TRANG ---
admin.site.site_header = "HOMNEST ADMINISTRATION"
admin.site.site_title = "Homnest Admin Portal"
admin.site.index_title = "Bảng Điều Khiển Quản Trị Hệ Thống"

# --- CÁC LỚP INLINE (HIỂN THỊ LỒNG NHAU) ---
class ListingAddressInline(admin.StackedInline):
    model = ListingAddress
    can_delete = False
    verbose_name = "Địa chỉ chi tiết"

class ListingImageInline(admin.TabularInline):
    model = ListingImage
    extra = 2
    fields = ('image_url', 'is_main', 'preview')
    readonly_fields = ('preview',)

    def preview(self, obj):
        if obj.image_url:
            return format_html('<img src="{}" style="height:50px; border-radius:5px;"/>', obj.image_url)
        return "No Image"

class ListingAmenityInline(admin.TabularInline):
    model = ListingAmenity
    extra = 1

# --- QUẢN LÝ NGƯỜI DÙNG (USERS) ---
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # Thay 'created_at' bằng 'date_joined' (trường chuẩn của Django User)
    list_display = ('id', 'full_name', 'email', 'colored_role', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active')
    search_fields = ('full_name', 'email', 'phone_number')

    ordering = ('-id',)

    def display_avatar(self, obj):
        url = obj.avatar_url if obj.avatar_url else 'https://via.placeholder.com/40'
        return format_html('<img src="{}" style="width:35px; height:35px; border-radius:50%; border: 2px solid #5D4037;"/>', url)
    display_avatar.short_description = "AVT"

    def colored_role(self, obj):
        colors = {'admin': '#3e2723', 'host': '#8d7767', 'guest': '#a1887f'}
        return format_html('<span style="color: white; background: {}; padding: 2px 8px; border-radius: 4px;">{}</span>', 
                           colors.get(obj.role, '#ccc'), obj.get_role_display())
    colored_role.short_description = "Vai trò"

# --- QUẢN LÝ CHỖ Ở (LISTINGS) ---
@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'host_link', 'price_display', 'is_active', 'created_at')
    list_editable = ('is_active',)
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'host__full_name')
    inlines = [ListingAddressInline, ListingImageInline, ListingAmenityInline]
    
    def host_link(self, obj):
        return format_html('<a href="/admin/app/user/{}/change/" style="color:#5D4037; font-weight:bold;">{}</a>', 
                           obj.host.user_id, obj.host.full_name)
    host_link.short_description = "Chủ nhà"

    def price_display(self, obj):
        return format_html('<b style="color:#5D4037;">${}</b> / đêm', obj.price_per_night)
    price_display.short_description = "Giá"

# --- QUẢN LÝ ĐẶT PHÒNG (BOOKINGS) ---
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_id', 'user', 'listing', 'check_in', 'check_out', 'colored_status', 'total_price')
    list_filter = ('booking_status', 'check_in')
    raw_id_fields = ('user', 'listing')

    def colored_status(self, obj):
        bg = '#A1887F' if obj.booking_status == 'pending' else '#5D4037'
        return format_html('<span style="background:{}; color:white; padding:3px 10px; border-radius:10px;">{}</span>', 
                           bg, obj.get_booking_status_display())

# --- QUẢN LÝ ĐÁNH GIÁ & AI (REVIEWS) ---
class ReviewMediaInline(admin.TabularInline):
    model = ReviewMedia
    extra = 0

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('review_id', 'user', 'listing', 'star_rating', 'ai_sentiment', 'created_at')
    inlines = [ReviewMediaInline]

    def star_rating(self, obj):
        return format_html('<span style="color: #8D6E63;">{} ★</span>', obj.rating)
    
    def ai_sentiment(self, obj):
        # Truy xuất kết quả từ bảng ReviewAnalysis (OneToOne)
        try:
            analysis = obj.analysis
            color = '#5D4037' if analysis.sentiment == 'positive' else '#d9534f'
            return format_html('<b style="color: {};">{}</b>', color, analysis.sentiment.upper())
        except:
            return "Chưa phân tích"

# --- QUẢN LÝ KHIẾU NẠI & CHÍNH SÁCH ---
@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('complaint_id', 'user', 'listing', 'colored_status')
    def colored_status(self, obj):
        color = '#5D4037' if obj.status == 'resolved' else '#8D6E63'
        return format_html('<b style="color:{};">{}</b>', color, obj.status.upper())

@admin.register(HostPolicy)
class HostPolicyAdmin(admin.ModelAdmin):
    list_display = ('host', 'warning_count', 'is_suspended_status')
    def is_suspended_status(self, obj):
        icon = "✅ Bình thường" if not obj.is_suspended else "🚫 Đã khóa"
        return icon

# --- ĐĂNG KÝ CÁC BẢNG CÒN LẠI ---
admin.site.register(Amenity)
admin.site.register(Payment)
admin.site.register(Message)
admin.site.unregister(Group)
admin.site.register(Group)
