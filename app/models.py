from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser

# Khai báo các lựa chọn (Choices) cho các trường ENUM
# Trong Django, chúng ta định nghĩa các ENUM bằng cách sử dụng Tuple of Tuples
ROLE_CHOICES = [
    ('admin', 'Admin'),
    ('host', 'Chủ nhà'),
    ('guest', 'Khách hàng'),
]

BOOKING_STATUS_CHOICES = [
    ('pending', 'Chờ xác nhận'),
    ('confirmed', 'Đã xác nhận'),
    ('cancelled', 'Đã hủy'), 
]

PAYMENT_STATUS_CHOICES = [
    ('paid', 'Đã thanh toán'),
    ('failed', 'Thanh toán thất bại'),
]

MEDIA_TYPE_CHOICES = [
    ('image', 'Ảnh'),
    ('video', 'Video'),
]

SENTIMENT_CHOICES = [
    ('positive', 'Tích cực'),
    ('negative', 'Tiêu cực'),
    ('neutral', 'Trung tính'), 
]

COMPLAINT_STATUS_CHOICES = [
    ('open', 'Chưa giải quyết'),
    ('resolved', 'Đã giải quyết'),
]

# --- 1. USERS ---
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """Custom User model kế thừa AbstractUser để có đầy đủ tính năng auth của Django"""
    
    # Ghi đè để bắt buộc email unique
    email = models.EmailField(unique=True, verbose_name='Email đăng nhập')
    
    # Thêm các trường tùy chỉnh
    full_name = models.CharField(max_length=150, blank=True, verbose_name='Họ tên đầy đủ')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='guest', verbose_name='Phân quyền')
    phone_number = models.CharField(max_length=20, null=True, blank=True, verbose_name='Số điện thoại')
    avatar_url = models.URLField(max_length=255, null=True, blank=True, verbose_name='Ảnh đại diện')
    
    # Đăng nhập bằng email thay vì username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username'] 
    
    def __str__(self):
        return self.email
    
    class Meta:
        db_table = 'users'
        verbose_name = "Người dùng"
        verbose_name_plural = "Người dùng"

# --- 2. LISTINGS ---
class Listing(models.Model):
    # listing_id (PK): BIGINT (BigAutoField)
    listing_id = models.BigAutoField(primary_key=True, verbose_name='Khóa chính')

    # host_id (FK): BIGINT (ForeignKey(User))
    # Quan hệ: 1 USERS -> N LISTINGS
    host = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='listings', verbose_name='Chủ nhà')

    # title: VARCHAR(255) (CharField)
    title = models.CharField(max_length=255, verbose_name='Tiêu đề')

    # description: TEXT (TextField)
    description = models.TextField(verbose_name='Mô tả')

    # price_per_night: DECIMAL(10,2) (DecimalField)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Giá / đêm')

    # max_adults: INT (IntegerField)
    max_adults = models.IntegerField(verbose_name='Số người lớn')

    # max_children: INT (IntegerField)
    max_children = models.IntegerField(default=0, verbose_name='Số trẻ em')

    # max_pets: INT (IntegerField)
    max_pets = models.IntegerField(default=0, verbose_name='Số thú cưng')

    # is_active: BOOLEAN (BooleanField)
    is_active = models.BooleanField(default=True, verbose_name='Có hiển thị không')

    # created_at: DATETIME (DateTimeField)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'listings'
        verbose_name = "Chỗ ở"
        verbose_name_plural = "Chỗ ở"


# --- 3. LISTING_ADDRESSES ---
class ListingAddress(models.Model):
    # address_id (PK): BIGINT (BigAutoField)
    address_id = models.BigAutoField(primary_key=True, verbose_name='Khóa chính')

    # listing_id (FK): BIGINT (OneToOneField)
    # Quan hệ: 1 LISTINGS -> 1 LISTING_ADDRESSES
    listing = models.OneToOneField(Listing, on_delete=models.CASCADE, primary_key=False, verbose_name='Gắn với listing')

    # city: VARCHAR(100) (CharField)
    city = models.CharField(max_length=100, verbose_name='Thành phố')

    # district: VARCHAR(100) (CharField)
    district = models.CharField(max_length=100, verbose_name='Quận')

    # street: VARCHAR(255) (CharField)
    street = models.CharField(max_length=255, verbose_name='Đường')

    # latitude: DECIMAL(9,6) (DecimalField)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name='Vĩ độ')

    # longitude: DECIMAL(9,6) (DecimalField)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name='Kinh độ')

    def __str__(self):
        return f"Địa chỉ của {self.listing.title}"

    class Meta:
        db_table = 'listing_addresses'
        verbose_name = "Địa chỉ chỗ ở"
        verbose_name_plural = "Địa chỉ chỗ ở"


# --- 4. LISTING_IMAGES ---
class ListingImage(models.Model):
    # image_id (PK): BIGINT (BigAutoField)
    image_id = models.BigAutoField(primary_key=True)

    # listing_id (FK): BIGINT (ForeignKey)
    # Quan hệ: 1 LISTINGS -> N LISTING_IMAGES
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='images', verbose_name='Thuộc listing')

    # image_url: VARCHAR(255) (ImageField)
    # Dùng URLField nếu chỉ lưu link ảnh bên ngoài, ImageField nếu upload lên Django
    image_url = models.URLField(max_length=255, verbose_name='Ảnh')

    # is_main: BOOLEAN (BooleanField)
    is_main = models.BooleanField(default=False, verbose_name='Ảnh đại diện')

    def __str__(self):
        return f"Ảnh {self.image_id} - {self.listing.title}"

    class Meta:
        db_table = 'listing_images'
        verbose_name = "Ảnh chỗ ở"
        verbose_name_plural = "Ảnh chỗ ở"


# --- 5. AMENITIES ---
class Amenity(models.Model):
    # amenity_id (PK): BIGINT (BigAutoField)
    amenity_id = models.BigAutoField(primary_key=True)

    # name: VARCHAR(100) (CharField)
    name = models.CharField(max_length=100, unique=True, verbose_name='Tên tiện nghi')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'amenities'
        verbose_name = "Tiện nghi"
        verbose_name_plural = "Tiện nghi"


# --- 6. LISTING_AMENITIES (Bảng trung gian cho quan hệ M-N) ---
# Django sẽ tự tạo nếu dùng models.ManyToManyField trên Listing.
# Nhưng nếu bạn muốn bảng trung gian rõ ràng để thêm thuộc tính sau này, ta định nghĩa nó.
class ListingAmenity(models.Model):
    # id (PK): BIGINT (BigAutoField)
    id = models.BigAutoField(primary_key=True)

    # listing_id (FK)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, verbose_name='Listing')

    # amenity_id (FK)
    amenity = models.ForeignKey(Amenity, on_delete=models.CASCADE, verbose_name='Tiện nghi')

    class Meta:
        # Đảm bảo một listing không có cùng tiện nghi hai lần
        db_table = 'listing_amenities'
        unique_together = ('listing', 'amenity')
        verbose_name = "Tiện nghi của chỗ ở"
        verbose_name_plural = "Tiện nghi của chỗ ở"

# Cập nhật Listing để sử dụng Many-to-Many
Listing.amenities = models.ManyToManyField(Amenity, through='ListingAmenity', related_name='listings')


# --- 7. BOOKINGS ---
class Booking(models.Model):
    # booking_id (PK): BIGINT (BigAutoField)
    booking_id = models.BigAutoField(primary_key=True)

    # user_id (FK): Khách
    # Quan hệ: 1 USERS -> N BOOKINGS
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.RESTRICT, related_name='bookings', verbose_name='Khách')

    # listing_id (FK): Phòng
    listing = models.ForeignKey(Listing, on_delete=models.RESTRICT, related_name='bookings', verbose_name='Phòng')

    # check_in: DATE (DateField)
    check_in = models.DateField(verbose_name='Ngày nhận')

    # check_out: DATE (DateField)
    check_out = models.DateField(verbose_name='Ngày trả')

    # total_price: DECIMAL(10,2) (DecimalField)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Tổng tiền')

    # booking_status: ENUM (CharField)
    booking_status = models.CharField(max_length=10, choices=BOOKING_STATUS_CHOICES, default='pending', verbose_name='Trạng thái đặt phòng')

    # created_at: DATETIME (DateTimeField)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Đặt phòng {self.booking_id} tại {self.listing.title}"

    class Meta:
        db_table = 'bookings'
        verbose_name = "Đơn đặt phòng"
        verbose_name_plural = "Đơn đặt phòng"


# --- 8. PAYMENTS ---
class Payment(models.Model):
    # payment_id (PK): BIGINT (BigAutoField)
    payment_id = models.BigAutoField(primary_key=True)

    # booking_id (FK): OneToOneField
    # Quan hệ: 1 BOOKINGS -> 1 PAYMENTS
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')

    # method: VARCHAR(50) (CharField)
    method = models.CharField(max_length=50, verbose_name='Phương thức')

    # amount: DECIMAL(10,2) (DecimalField)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    # status: ENUM (CharField)
    status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='paid', verbose_name='Trạng thái thanh toán')

    # paid_at: DATETIME (DateTimeField)
    paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Thanh toán cho Đơn {self.booking.booking_id}"

    class Meta:
        db_table = 'payments'
        verbose_name = "Thanh toán"
        verbose_name_plural = "Thanh toán"


# --- 9. REVIEWS ---
class Review(models.Model):
    # review_id (PK): BIGINT (BigAutoField)
    review_id = models.BigAutoField(primary_key=True)

    # booking_id (FK): OneToOneField
    # Quan hệ: 1 BOOKINGS -> 1 REVIEWS
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='review')

    # listing_id (FK)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='reviews')

    # user_id (FK)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')

    # rating: INT (IntegerField) - CHECK 1-5
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], verbose_name='Điểm (1-5)')

    # comment: TEXT (TextField)
    comment = models.TextField(verbose_name='Nội dung')

    # created_at: DATETIME (DateTimeField)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Đánh giá {self.review_id} - {self.listing.title}"

    class Meta:
        db_table = 'reviews'
        verbose_name = "Đánh giá chỗ ở"
        verbose_name_plural = "Đánh giá chỗ ở"


# --- 10. REVIEW_MEDIA ---
class ReviewMedia(models.Model):
    # media_id (PK): BIGINT (BigAutoField)
    media_id = models.BigAutoField(primary_key=True)

    # review_id (FK)
    # Quan hệ: 1 REVIEWS -> N REVIEW_MEDIA
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='media')

    # media_url: VARCHAR(255) (FileField) - Đổi thành URLField cho đơn giản hoặc FileField nếu bạn muốn lưu tệp tin
    media_url = models.URLField(max_length=255, verbose_name='Link Media')

    # media_type: ENUM (CharField)
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES, verbose_name='Loại media')

    def __str__(self):
        return f"Media cho Review {self.review.review_id}"

    class Meta:
        db_table = 'review_media'
        verbose_name = "Ảnh/Video đánh giá"
        verbose_name_plural = "Ảnh/Video đánh giá"


# --- 11. REVIEW_ANALYSES ---
class ReviewAnalysis(models.Model):
    # analysis_id (PK): BIGINT (BigAutoField)
    analysis_id = models.BigAutoField(primary_key=True)

    # review_id (FK): OneToOneField
    # Quan hệ: 1 REVIEWS -> 1 REVIEW_ANALYSES
    review = models.OneToOneField(Review, on_delete=models.CASCADE, related_name='analysis')

    # sentiment: ENUM (CharField)
    sentiment = models.CharField(max_length=10, choices=SENTIMENT_CHOICES, verbose_name='Cảm xúc')

    # confidence_score: DECIMAL(5,2) (DecimalField)
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Độ tin cậy')

    # analyzed_at: DATETIME (DateTimeField)
    analyzed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Phân tích Review {self.review.review_id}: {self.sentiment}"

    class Meta:
        db_table = 'review_analyses'
        verbose_name = "Phân tích đánh giá AI"
        verbose_name_plural = "Phân tích đánh giá AI"


# --- 12. MESSAGES ---
class Message(models.Model):
    # message_id (PK): BIGINT (BigAutoField)
    message_id = models.BigAutoField(primary_key=True)

    # sender_id (FK) & receiver_id (FK)
    # Quan hệ: 1 USERS -> N MESSAGES
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')

    # content: TEXT (TextField)
    content = models.TextField()

    # created_at: DATETIME (DateTimeField)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Tin nhắn từ {self.sender.email} đến {self.receiver.email}"

    class Meta:
        db_table = 'messages'
        verbose_name = "Tin nhắn"
        verbose_name_plural = "Tin nhắn"


# --- 13. COMPLAINTS ---
class Complaint(models.Model):
    # complaint_id (PK): BIGINT (BigAutoField)
    complaint_id = models.BigAutoField(primary_key=True)

    # user_id (FK)
    # Quan hệ: 1 USERS -> N COMPLAINTS
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.RESTRICT, related_name='complaints', verbose_name='Người khiếu nại')

    # listing_id (FK)
    listing = models.ForeignKey(Listing, on_delete=models.RESTRICT, related_name='complaints', verbose_name='Chỗ ở bị khiếu nại')

    # reason: TEXT (TextField)
    reason = models.TextField()

    # status: ENUM (CharField)
    status = models.CharField(max_length=10, choices=COMPLAINT_STATUS_CHOICES, default='open', verbose_name='Trạng thái')

    # created_at: DATETIME (DateTimeField)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Khiếu nại {self.complaint_id} - Trạng thái: {self.status}"

    class Meta:
        db_table = 'complaints'
        verbose_name = "Khiếu nại"
        verbose_name_plural = "Khiếu nại"


# --- 14. HOST_POLICIES ---
class HostPolicy(models.Model):
    # policy_id (PK): BIGINT (BigAutoField)
    policy_id = models.BigAutoField(primary_key=True)

    # host_id (FK): OneToOneField
    # Quan hệ: 1 USERS -> 1 HOST_POLICIES (chỉ áp dụng cho user có role 'host')
    host = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=False, related_name='policy')

    # warning_count: INT (IntegerField)
    warning_count = models.IntegerField(default=0)

    # is_suspended: BOOLEAN (BooleanField)
    is_suspended = models.BooleanField(default=False)

    # updated_at: DATETIME (DateTimeField)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Chính sách cho Chủ nhà {self.host.full_name}"

    class Meta:
        db_table = 'host_policies'
        verbose_name = "Chính sách chủ nhà"
        verbose_name_plural = "Chính sách chủ nhà"


