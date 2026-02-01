from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone
from django.urls import path, reverse
from django.shortcuts import redirect
import json
import uuid
from django import forms
from django.core.exceptions import ValidationError
from decimal import Decimal
from .models import (
    Listing, ListingAddress, ListingImage, Amenity, ListingAmenity,
    Booking, Payment, Review, ReviewMedia, ReviewAnalysis,
    Complaint, HostPolicy, ReviewClassification
)

User = get_user_model()


# --- Custom AdminSite để thêm link thống kê ---
class CustomAdminSite(admin.AdminSite):
    site_header = "HOMNEST ADMINISTRATION"
    site_title = "Homnest Admin Portal"
    index_title = "Bảng Điều Khiển Quản Trị Hệ Thống"
    
    def get_app_list(self, request, app_label=None):
        app_list = super().get_app_list(request, app_label)
        
        # Thêm mục Thống kê doanh thu vào đầu danh sách
        revenue_stats = {
            'name': 'Thống kê & Báo cáo',
            'app_label': 'statistics',
            'app_url': reverse('admin_revenue_statistics'),
            'has_module_perms': True,
            'models': [
                {
                    'name': '📊 Thống kê doanh thu',
                    'object_name': 'RevenueStatistics',
                    'admin_url': reverse('admin_revenue_statistics'),
                    'view_only': True,
                }
            ]
        }
        
        # Chèn vào đầu danh sách
        app_list.insert(0, revenue_stats)
        
        return app_list


# Override default admin site
admin.site.__class__ = CustomAdminSite

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


class PaymentInline(admin.StackedInline):
    model = Payment
    can_delete = True
    readonly_fields = ('method', 'amount', 'status', 'paid_at', 'transaction_id', 'details')
    fields = ('method', 'amount', 'status', 'paid_at', 'transaction_id', 'details')
    extra = 0

    def transaction_id(self, obj):
        return getattr(obj, 'transaction_id', None)

    def details(self, obj):
        # pretty-print JSON if possible
        val = getattr(obj, 'details', None)
        try:
            return json.dumps(json.loads(val), ensure_ascii=False, indent=2) if val else ''
        except Exception:
            return val

    def has_delete_permission(self, request, obj=None):
        # Ensure inline shows delete checkbox for users who have model delete permission
        return request.user.has_perm('app.delete_payment') or request.user.is_superuser

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
    list_display = ('title', 'host_link', 'price_display', 'review_sentiment_chart', 'status', 'is_active', 'created_at')
    list_editable = ('status', 'is_active',)
    list_filter = ('status', 'is_active', 'created_at')
    search_fields = ('title', 'host__full_name')
    inlines = [ListingAddressInline, ListingImageInline, ListingAmenityInline]
    actions = ('approve_listings', 'reject_listings')
    
    def save_model(self, request, obj, form, change):
        """Auto-set is_active based on status when saving"""
        if obj.status == 'approved':
            obj.is_active = True
        elif obj.status in ('rejected', 'pending'):
            obj.is_active = False
        super().save_model(request, obj, form, change)
    
    def host_link(self, obj):
        # use primary key `id` (or `pk`) — User model does not have `user_id` attribute
        return format_html('<a href="/admin/app/user/{}/change/" style="color:#5D4037; font-weight:bold;">{}</a>', 
                           obj.host.pk, obj.host.full_name)
    host_link.short_description = "Chủ nhà"

    def price_display(self, obj):
        return format_html('<b style="color:#5D4037;">${}</b> / đêm', obj.price_per_night)
    price_display.short_description = "Giá"

    def approve_listings(self, request, queryset):
        updated = queryset.update(status='approved', is_active=True)
        self.message_user(request, f"Approved {updated} listing(s) and set active.")
    approve_listings.short_description = 'Approve selected listings'

    def reject_listings(self, request, queryset):
        updated = queryset.update(status='rejected', is_active=False)
        self.message_user(request, f"Rejected {updated} listing(s) and set inactive.")
    reject_listings.short_description = 'Reject selected listings'

    def review_sentiment_chart(self, obj):
        # qs = Review.objects.filter(listing=obj).select_related('analysis')

        qs = Review.objects.filter(
            listing=obj,
            reviewclassification__spam_status=False
        ).select_related("analysis").select_related('analysis')


        pos = qs.filter(analysis__sentiment='pos').count()
        neg = qs.filter(analysis__sentiment='neg').count()

        total = pos + neg
        if total == 0:
            return format_html('<span style="color:#999;">Chưa có đánh giá</span>')

        pos_pct = round(pos * 100 / total)
        neg_pct = 100 - pos_pct

        return format_html(
            '''
            <div style="display:flex; align-items:center; gap:10px;">
                
                <!-- PIE -->
                <div style="
                    width:64px;
                    height:64px;
                    border-radius:50%;
                    background:
                        conic-gradient(
                            #2e7d32 0% {pos_pct}%,
                            #c62828 {pos_pct}% 100%
                        );
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    font-size:13px;
                    font-weight:600;
                    color:#333;
                    box-shadow: inset 0 0 0 6px #fff;
                ">
                    {pos_pct}%
                </div>

                <!-- LEGEND -->
                <div style="font-size:11px; line-height:1.4;">
                    <div style="color:#2e7d32;">● 👍 {pos_pct}% ({pos})</div>
                    <div style="color:#c62828;">● 👎 {neg_pct}% ({neg})</div>
                </div>
            </div>
            ''',
            pos_pct=pos_pct,
            neg_pct=neg_pct,
            pos=pos,
            neg=neg
        )




    review_sentiment_chart.short_description = "Đánh giá (AI)"
# --- QUẢN LÝ ĐẶT PHÒNG (BOOKINGS) ---
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_id', 'user_link', 'listing', 'check_in', 'check_out', 'colored_status', 'base_price', 'payment_status')
    list_filter = ('booking_status', 'check_in')
    raw_id_fields = ('user', 'listing')
    inlines = [PaymentInline]
    actions = ('mark_as_paid',)

    def user_link(self, obj):
        try:
            return format_html('<a href="/admin/app/user/{}/change/">{}</a>', obj.user.pk, obj.user.email)
        except Exception:
            return str(obj.user)
    user_link.short_description = 'Khách'

    def colored_status(self, obj):
        bg = '#A1887F' if obj.booking_status == 'pending' else '#5D4037'
        return format_html('<span style="background:{}; color:white; padding:3px 10px; border-radius:10px;">{}</span>', 
                           bg, obj.get_booking_status_display())

    def payment_status(self, obj):
        try:
            p = obj.payment
            color = '#2e7d32' if p.status == 'paid' else '#d32f2f'
            return format_html('<b style="color:{};">{}</b>', color, p.get_status_display())
        except Exception:
            return 'Chưa thanh toán'
    payment_status.short_description = 'Thanh toán'

    def mark_as_paid(self, request, queryset):
        """Admin action: create or update Payment to mark bookings as paid and confirm booking."""
        created = 0
        updated = 0
        for booking in queryset:
            try:
                payment = getattr(booking, 'payment', None)
                if payment is None:
                    payment = Payment.objects.create(
                        booking=booking,
                        method='admin',
                        amount=booking.total_price,
                        status='paid',
                        paid_at=timezone.now(),
                        transaction_id=f"admin-{booking.booking_id}-{uuid.uuid4().hex[:8]}",
                        details=json.dumps({'admin_action': True, 'amount': str(booking.total_price)}),
                    )
                    created += 1
                else:
                    payment.status = 'paid'
                    payment.paid_at = timezone.now()
                    payment.transaction_id = payment.transaction_id or f"admin-{booking.booking_id}-{uuid.uuid4().hex[:8]}"
                    payment.details = json.dumps({'admin_action': True, 'amount': str(booking.total_price)})
                    payment.save()
                    updated += 1

                if booking.booking_status != 'confirmed':
                    booking.booking_status = 'confirmed'
                    booking.save()
            except Exception:
                continue

        self.message_user(request, f"Marked paid: created={created}, updated={updated}")
    mark_as_paid.short_description = 'Mark selected bookings as paid and confirm'

# --- QUẢN LÝ ĐÁNH GIÁ & AI (REVIEWS) ---
class ReviewMediaInline(admin.TabularInline):
    model = ReviewMedia
    extra = 0

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('review_id', 'user', 'listing', 'star_rating', 'ai_sentiment', 'created_at')
    inlines = [ReviewMediaInline]
    list_filter = ("reviewclassification__spam_status",)
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
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'booking', 'amount', 'status', 'paid_at')

    class Media:
        js = ('app/js/admin_payment.js',)

    class PaymentForm(forms.ModelForm):
        class Meta:
            model = Payment
            fields = '__all__'

        def clean(self):
            cleaned = super().clean()
            booking = cleaned.get('booking')
            amount = cleaned.get('amount')
            if booking and amount is not None:
                try:
                    booking_total = Decimal(booking.total_price)
                except Exception:
                    booking_total = None
                if booking_total is not None and Decimal(amount) != booking_total:
                    raise ValidationError({'amount': f'Amount must equal booking total_price ({booking_total}).'})
            return cleaned

    form = PaymentForm

    def get_form(self, request, obj=None, **kwargs):
        BaseForm = super().get_form(request, obj, **kwargs)
        booking_model = Booking

        class AdminForm(BaseForm):
            def __init__(self, *args, **kw):
                super().__init__(*args, **kw)
                try:
                    bk = None
                    # prefer booking from GET param (when adding from booking change page)
                    if request and request.GET.get('booking'):
                        bk = request.GET.get('booking')
                    # if bound form, data may contain booking
                    if not bk:
                        if getattr(self, 'data', None):
                            bk = self.data.get('booking')
                        else:
                            bk = self.initial.get('booking') if getattr(self, 'initial', None) else None

                    if bk:
                        b = booking_model.objects.filter(pk=bk).first()
                        if b and 'amount' in self.fields:
                            self.fields['amount'].initial = b.total_price
                except Exception:
                    pass

        return AdminForm

    def save_model(self, request, obj, form, change):
        # do not silently override amount; validation above will prevent mismatches
        super().save_model(request, obj, form, change)

admin.site.register(Payment, PaymentAdmin)
admin.site.unregister(Group)
admin.site.register(Group)
@admin.register(ReviewClassification)
class ReviewClassificationAdmin(admin.ModelAdmin):
    list_display = ("review", "spam_status")
    list_filter = ("spam_status",)