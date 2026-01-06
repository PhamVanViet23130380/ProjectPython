from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
LISTING_STATUS_CHOICES = [
    ('pending', 'Chờ duyệt'),
    ('approved', 'Đã duyệt'),
    ('rejected', 'Từ chối'),
]


# --- PROPERTY TYPE CHOICES ---
PROPERTY_TYPE_CHOICES = [
    ('Nhà riêng', 'Nhà riêng / nguyên căn'),
    ('Căn hộ', 'Căn hộ / chung cư'),
    ('Phòng riêng', 'Phòng riêng'),
    ('Biệt thự', 'Biệt thự'),
    ('Khách sạn / resort', 'Khách sạn / resort'),
    ('Nhà khách / nhà nghỉ', 'Nhà khách / nhà nghỉ'),
    ('Cabin / nhà gỗ', 'Cabin / nhà gỗ'),
    ('Tiny house', 'Tiny house'),
    ('Nhà trên cây', 'Nhà trên cây'),
    ('Nhà thuyền', 'Nhà thuyền'),
    ('Glamping / lều', 'Glamping / lều'),
    ('Nông trại / farmstay', 'Nông trại / farmstay'),
]

# --- USAGE TYPE CHOICES ---
USAGE_TYPE_CHOICES = [
    ('Toàn bộ nhà', 'Toàn bộ nhà'),
    ('Phòng riêng', 'Phòng riêng'),
    ('Phòng chung', 'Phòng chung'),
]


# --- LISTINGS ---
class Listing(models.Model):
    listing_id = models.BigAutoField(primary_key=True, verbose_name='Khóa chính')
    host = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='listings', verbose_name='Chủ nhà')
    title = models.CharField(max_length=255, verbose_name='Tiêu đề')
    description = models.TextField(verbose_name='Mô tả')
    property_type = models.CharField(max_length=50, choices=PROPERTY_TYPE_CHOICES, default='Nhà riêng', verbose_name='Loại chỗ ở')
    usage_type = models.CharField(max_length=50, choices=USAGE_TYPE_CHOICES, default='Toàn bộ nhà', verbose_name='Loại sử dụng')
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Giá / đêm')
    cleaning_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Phí vệ sinh')
    available_from = models.DateField(null=True, blank=True, verbose_name='Ngày bắt đầu cho thuê')
    available_to = models.DateField(null=True, blank=True, verbose_name='Ngày kết thúc cho thuê')
    max_adults = models.IntegerField(verbose_name='Số người lớn')
    max_children = models.IntegerField(default=0, verbose_name='Số trẻ em')
    max_pets = models.IntegerField(default=0, verbose_name='Số thú cưng')
    bedrooms = models.IntegerField(default=1, verbose_name='Số phòng ngủ')
    beds = models.IntegerField(default=1, verbose_name='Số giường')
    bathrooms = models.IntegerField(default=1, verbose_name='Số phòng tắm')
    is_active = models.BooleanField(default=True, verbose_name='Có hiển thị không')
    status = models.CharField(max_length=10, choices=LISTING_STATUS_CHOICES, default='pending', verbose_name='Trạng thái duyệt')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')

    # Many-to-many amenities (through table declared below)
    amenities = models.ManyToManyField('Amenity', through='ListingAmenity', related_name='listings')

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'listings'
        verbose_name = "Chỗ ở"
        verbose_name_plural = "Chỗ ở"


class ListingAddress(models.Model):
    address_id = models.BigAutoField(primary_key=True, verbose_name='Khóa chính')
    listing = models.OneToOneField(Listing, on_delete=models.CASCADE, primary_key=False, verbose_name='Gắn với listing')
    city = models.CharField(max_length=100, verbose_name='Thành phố')
    district = models.CharField(max_length=100, verbose_name='Quận')
    street = models.CharField(max_length=255, verbose_name='Đường')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name='Vĩ độ')
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name='Kinh độ')

    def __str__(self):
        return f"Địa chỉ của {self.listing.title}"

    class Meta:
        db_table = 'listing_addresses'
        verbose_name = "Địa chỉ chỗ ở"
        verbose_name_plural = "Địa chỉ chỗ ở"


class ListingImage(models.Model):
    image_id = models.BigAutoField(primary_key=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='images', verbose_name='Thuộc listing')
    image_url = models.CharField(max_length=255, verbose_name='Ảnh')
    is_main = models.BooleanField(default=False, verbose_name='Ảnh đại diện')

    def __str__(self):
        return f"Ảnh {self.image_id} - {self.listing.title}"

    class Meta:
        db_table = 'listing_images'
        verbose_name = "Ảnh chỗ ở"
        verbose_name_plural = "Ảnh chỗ ở"


AMENITY_CATEGORY_CHOICES = [
    ('basic', 'Tiện nghi cơ bản'),
    ('featured', 'Tiện nghi nổi bật'),
    ('safety', 'An toàn'),
]


class Amenity(models.Model):
    amenity_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True, verbose_name='Tên tiện nghi')
    category = models.CharField(max_length=20, choices=AMENITY_CATEGORY_CHOICES, default='basic', verbose_name='Loại')
    icon = models.CharField(max_length=50, blank=True, null=True, verbose_name='Icon class (FontAwesome)')

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"

    class Meta:
        db_table = 'amenities'
        verbose_name = "Tiện nghi"
        verbose_name_plural = "Tiện nghi"


class ListingAmenity(models.Model):
    id = models.BigAutoField(primary_key=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, verbose_name='Listing')
    amenity = models.ForeignKey(Amenity, on_delete=models.CASCADE, verbose_name='Tiện nghi')

    class Meta:
        db_table = 'listing_amenities'
        unique_together = ('listing', 'amenity')
        verbose_name = "Tiện nghi của chỗ ở"
        verbose_name_plural = "Tiện nghi của chỗ ở"


class Review(models.Model):
    review_id = models.BigAutoField(primary_key=True)
    booking = models.OneToOneField('app.Booking', on_delete=models.CASCADE, related_name='review')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], verbose_name='Điểm (1-5)')
    comment = models.TextField(verbose_name='Nội dung')
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        """Validate that the review's booking matches the review listing and user.

        Raises ValidationError when booking.listing != listing or booking.user != user.
        """
        if self.booking is None:
            return

        # booking may be a Booking instance or a PK; assume relation is set
        try:
            booking_obj = self.booking
        except Exception:
            booking_obj = None

        if booking_obj:
            if booking_obj.listing_id != self.listing_id:
                raise ValidationError({'listing': _('Listing của review phải khớp với listing của booking.')})
            if getattr(booking_obj, 'user_id', None) != getattr(self, 'user_id', None):
                raise ValidationError({'user': _('User của review phải khớp với user của booking.')})

    def __str__(self):
        return f"Đánh giá {self.review_id} - {self.listing.title}"

    class Meta:
        db_table = 'reviews'
        verbose_name = "Đánh giá chỗ ở"
        verbose_name_plural = "Đánh giá chỗ ở"


class ReviewMedia(models.Model):
    media_id = models.BigAutoField(primary_key=True)
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='media')
    media_url = models.URLField(max_length=255, verbose_name='Link Media')
    media_type = models.CharField(max_length=10, choices=(('image', 'Ảnh'), ('video', 'Video')),
                                  verbose_name='Loại media')

    def __str__(self):
        return f"Media cho Review {self.review.review_id}"

    class Meta:
        db_table = 'review_media'
        verbose_name = "Ảnh/Video đánh giá"
        verbose_name_plural = "Ảnh/Video đánh giá"


class ReviewAnalysis(models.Model):
    analysis_id = models.BigAutoField(primary_key=True)
    review = models.OneToOneField(Review, on_delete=models.CASCADE, related_name='analysis')
    sentiment = models.CharField(max_length=10, choices=(('positive', 'Tích cực'), ('negative', 'Tiêu cực'), ('neutral', 'Trung tính')),
                                 verbose_name='Cảm xúc')
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Độ tin cậy')
    analyzed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Phân tích Review {self.review.review_id}: {self.sentiment}"

    class Meta:
        db_table = 'review_analyses'
        verbose_name = "Phân tích đánh giá AI"
        verbose_name_plural = "Phân tích đánh giá AI"


class ReviewClassification(models.Model):
    id = models.BigAutoField(primary_key=True)
    spam_status = models.BooleanField(default=False)
    review = models.OneToOneField(Review, on_delete=models.CASCADE)

    def __str__(self):
        return f"Phân loại review {self.review.review_id} - spam={self.spam_status}"

    class Meta:
        db_table = 'review_classifications'
        verbose_name = "Phân loại đánh giá"
        verbose_name_plural = "Phân loại đánh giá"
