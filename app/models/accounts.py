from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


# --- 1. USERS ---
ROLE_CHOICES = [
    ('admin', 'Admin'),
    ('host', 'Chủ nhà'),
    ('guest', 'Khách hàng'),
]


class User(AbstractUser):
    """Custom User model"""
    email = models.EmailField(unique=True, verbose_name='Email đăng nhập')
    full_name = models.CharField(max_length=150, blank=True, verbose_name='Họ tên đầy đủ')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='guest', verbose_name='Phân quyền')
    phone_number = models.CharField(max_length=20, null=True, blank=True, verbose_name='Số điện thoại')
    avatar = models.ImageField(
    upload_to='avatars/',
    null=True,
    blank=True,
    verbose_name='Ảnh đại diện')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    class Meta:
        db_table = 'users'
        verbose_name = "Người dùng"
        verbose_name_plural = "Người dùng"


# --- BOOKINGS & PAYMENTS ---
BOOKING_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('confirmed', 'Confirmed'),
    ('in_progress', 'In progress'),
    ('completed', 'Completed'),
    ('cancelled', 'Cancelled'),
]

PAYMENT_STATUS_CHOICES = [
    ('paid', 'Đã thanh toán'),
    ('failed', 'Thanh toán thất bại'),
    ('refunded', 'Đã hoàn tiền'),
]


class Booking(models.Model):
    booking_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.RESTRICT, related_name='bookings', verbose_name='Khách')
    listing = models.ForeignKey('app.Listing', on_delete=models.RESTRICT, related_name='bookings', verbose_name='Phòng')
    check_in = models.DateField(verbose_name='Ngày nhận')
    check_out = models.DateField(verbose_name='Ngày trả')
    guests = models.IntegerField(default=1, verbose_name='Số khách')
    base_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Giá cơ bản')
    service_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Phí dịch vụ')
    booking_status = models.CharField(max_length=20, choices=BOOKING_STATUS_CHOICES, default='pending', verbose_name='Trạng thái đặt phòng')
    created_at = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True, null=True, default='', verbose_name='Ghi chú')

    def clean(self):
        """Validate booking dates and prevent overlapping bookings for same listing.

        Raises ValidationError when check_in >= check_out or when there is an
        existing non-cancelled booking for the same listing that overlaps.
        """
        # Ensure dates are present
        if self.check_in is None or self.check_out is None:
            return

        if self.check_in >= self.check_out:
            raise ValidationError({'check_in': _('Ngày nhận phải sớm hơn ngày trả.')})

        # Check overlapping bookings: consider bookings with status pending/confirmed
        overlap_qs = Booking.objects.filter(
            listing=self.listing,
        ).exclude(pk=self.pk)

        overlapping = []
        for other in overlap_qs:
            # ignore cancelled bookings
            if getattr(other, 'booking_status', None) == 'cancelled':
                continue
            # overlap if not (other.check_out <= self.check_in or other.check_in >= self.check_out)
            if not (other.check_out <= self.check_in or other.check_in >= self.check_out):
                overlapping.append(other)

        if overlapping:
            raise ValidationError(_('Khoảng thời gian đặt phòng trùng với một đặt phòng khác.'))

    def __str__(self):
        return f"Đặt phòng {self.booking_id} tại {self.listing.title}"

    class Meta:
        db_table = 'bookings'
        verbose_name = "Đơn đặt phòng"
        verbose_name_plural = "Đơn đặt phòng"

class Payment(models.Model):
    payment_id = models.BigAutoField(primary_key=True)
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    method = models.CharField(max_length=50, verbose_name='Phương thức')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='paid', verbose_name='Trạng thái thanh toán')
    transaction_id = models.CharField(max_length=255, unique=True, null=True, blank=True, verbose_name='Mã giao dịch')
    paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Thanh toán cho Đơn {self.booking.booking_id}"

    class Meta:
        db_table = 'payments'
        verbose_name = "Thanh toán"
        verbose_name_plural = "Thanh toán"


# --- COMPLAINTS ---
COMPLAINT_STATUS_CHOICES = [
    ('open', 'Chưa giải quyết'),
    ('resolved', 'Đã giải quyết'),
]


class Complaint(models.Model):
    complaint_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.RESTRICT, related_name='complaints', verbose_name='Người khiếu nại')
    listing = models.ForeignKey('app.Listing', on_delete=models.RESTRICT, related_name='complaints', verbose_name='Chỗ ở bị khiếu nại')
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=COMPLAINT_STATUS_CHOICES, default='open', verbose_name='Trạng thái')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Khiếu nại {self.complaint_id} - Trạng thái: {self.status}"

    class Meta:
        db_table = 'complaints'
        verbose_name = "Khiếu nại"
        verbose_name_plural = "Khiếu nại"


# --- HOST POLICIES ---
class HostPolicy(models.Model):
    policy_id = models.BigAutoField(primary_key=True)
    host = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=False, related_name='policy')
    warning_count = models.IntegerField(default=0)
    is_suspended = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Chính sách cho Chủ nhà {self.host.get_full_name()}"

    class Meta:
        db_table = 'host_policies'
        verbose_name = "Chính sách chủ nhà"
        verbose_name_plural = "Chính sách chủ nhà"

# --- BANK ACCOUNT ---
class BankAccount(models.Model):
    """Thông tin tài khoản ngân hàng của người dùng"""
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='bank_account',
        verbose_name='Người dùng'
    )
    
    bank_name = models.CharField(
        max_length=100, 
        verbose_name='Tên ngân hàng'
    )
    
    account_number = models.CharField(
        max_length=50, 
        verbose_name='Số tài khoản'
    )
    
    account_holder = models.CharField(
        max_length=150, 
        verbose_name='Tên chủ tài khoản'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Cập nhật lần cuối')
    
    def __str__(self):
        return f"{self.bank_name} - {self.account_number} ({self.user.email})"
    
    class Meta:
        db_table = 'bank_accounts'
        verbose_name = "Tài khoản ngân hàng"
        verbose_name_plural = "Tài khoản ngân hàng"


# --- NOTIFICATION ---
NOTIFICATION_TYPE_CHOICES = [
    ('listing_approved', 'Chỗ ở được duyệt'),
    ('listing_rejected', 'Chỗ ở bị từ chối'),
    ('new_booking', 'Có đặt phòng mới'),
    ('booking_confirmed', 'Đặt phòng được xác nhận'),
    ('booking_cancelled', 'Đặt phòng bị hủy'),
    ('guest_checkin', 'Khách nhận phòng'),
    ('guest_checkout', 'Khách trả phòng'),
    ('booking_completed', 'Hoàn thành lượt thuê'),
    ('payment_received', 'Nhận thanh toán'),
    ('review_received', 'Nhận đánh giá mới'),
]


class Notification(models.Model):
    """Thông báo cho người dùng"""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='notifications',
        verbose_name='Người nhận'
    )
    
    notification_type = models.CharField(
        max_length=30, 
        choices=NOTIFICATION_TYPE_CHOICES,
        verbose_name='Loại thông báo'
    )
    
    title = models.CharField(max_length=200, verbose_name='Tiêu đề')
    message = models.TextField(verbose_name='Nội dung')
    
    # Liên kết đến đối tượng liên quan (optional)
    listing = models.ForeignKey(
        'app.Listing', 
        on_delete=models.CASCADE, 
        null=True, blank=True,
        related_name='notifications',
        verbose_name='Chỗ ở liên quan'
    )
    booking = models.ForeignKey(
        Booking, 
        on_delete=models.CASCADE, 
        null=True, blank=True,
        related_name='notifications',
        verbose_name='Đặt phòng liên quan'
    )
    
    is_read = models.BooleanField(default=False, verbose_name='Đã đọc')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Thời gian')
    
    def __str__(self):
        return f"{self.title} - {self.user.email}"
    
    class Meta:
        db_table = 'notifications'
        verbose_name = "Thông báo"
        verbose_name_plural = "Thông báo"
        ordering = ['-created_at']