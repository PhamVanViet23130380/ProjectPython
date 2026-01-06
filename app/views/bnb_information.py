# # from django.shortcuts import render, get_object_or_404
# # from django.db.models import Avg
# # from django.utils import timezone

# # from app.models import Review, Booking

# # def listing_detail(request, listing_id):
# #     """Show detailed page for a single listing (bnb).

# #     Loads related address, images, amenities and reviews. Keeps queries
# #     defensive so the view still works if some relations are missing.
# #     Renders `app/pages/listing_detail.html` (create template if missing).
# #     """
# #     try:
# #         from models import Listing
# #     except Exception:
# #         # If models can't be imported, render an error-like page without raising
# #         return render(request, 'templates/app/guest/chitietnoio.html', {'error': 'Listing model unavailable'})
# #     listing = get_object_or_404(Listing, pk=listing_id)

# #     # related objects (use safe attribute access)
# #     address = getattr(listing, 'listingaddress', None)
# #     images = list(getattr(listing, 'images', []).all()) if hasattr(listing, 'images') else []
# #     amenities = list(getattr(listing, 'amenities', []).all()) if hasattr(listing, 'amenities') else []

# #     # reviews and aggregated rating
# #     reviews_qs = getattr(listing, 'reviews', None)
# #     reviews = list(reviews_qs.all()) if reviews_qs is not None else []
# #     avg_rating = None
# #     try:
# #         avg_rating = reviews_qs.aggregate(avg=Avg('rating'))['avg'] if reviews_qs is not None else None
# #     except Exception:
# #         avg_rating = None


# #     # ====== LOGIC ĐƯỢC PHÉP ĐÁNH GIÁ ======
# #     can_review = False

# #     if request.user.is_authenticated:
# #         has_completed_booking = Booking.objects.filter(
# #             listing=listing,
# #             user=request.user,
# #             check_out__lt=timezone.now(),
# #             booking_status='completed'
# #         ).exists()

# #         already_reviewed = Review.objects.filter(
# #             listing=listing,
# #             user=request.user
# #         ).exists()

# #         can_review = has_completed_booking and not already_reviewed
# #     # =====================================

# #     context = {
# #         'listing': listing,
# #         'address': address,
# #         'images': images,
# #         'amenities': amenities,
# #         'reviews': reviews,
# #         'avg_rating': avg_rating,
# #         'can_review': can_review,
# #     }

# #     return render(request, 'templates/app/guest/chitietnoio.html', context)


# from django.shortcuts import render, get_object_or_404, redirect
# from django.db.models import Avg
# from django.http import HttpResponseForbidden

# from app.models import Listing, Booking, Review
# from app.sentiment import analyze_sentiment
# from django.utils import timezone
# from app.models import ReviewAnalysis


# def listing_detail(request, listing_id):

#     listing = get_object_or_404(Listing, pk=listing_id)

#     reviews = listing.reviews.select_related("user", "analysis").all()
#     avg_rating = reviews.aggregate(avg=Avg("rating"))["avg"]

#     booking = None
#     can_review = False
#     review_status = None

#     # ====== XÁC ĐỊNH BOOKING ======
#     if request.user.is_authenticated:
#         today = timezone.localdate()

#         # TÌM BOOKING COMPLETED CHƯA CÓ REVIEW
#         booking = Booking.objects.filter(
#             listing=listing,
#             user=request.user,
#             booking_status="completed",
#             check_out__lt=today,
#             review__isnull=True   
#         ).order_by("-check_out").first()

#         if booking:
#             can_review = True
#             review_status = "pending_review"
#         else:
#             # Nếu user có booking completed nhưng tất cả đã review
#             has_completed = Booking.objects.filter(
#                 listing=listing,
#                 user=request.user,
#                 booking_status="completed",
#                 check_out__lt=today
#             ).exists()

#             if has_completed:
#                 review_status = "reviewed"

#     # ====== SUBMIT REVIEW ======
#     if request.method == "POST":
#         if not can_review or booking is None:
#             return HttpResponseForbidden("Không có booking hợp lệ để đánh giá")

#         rating = int(request.POST.get("rating"))
#         comment = request.POST.get("comment", "").strip()

#         # 1. Tạo review → PHẢI gán biến
#         review = Review.objects.create(
#             booking=booking,
#             listing=listing,
#             user=request.user,
#             rating=rating,
#             comment=comment
# )
#         # 2. Chạy ViSoBERT
#         sentiment, confidence = analyze_sentiment(comment)

#         # 3. Lưu kết quả phân tích
#         ReviewAnalysis.objects.create(
#             review=review,
#             sentiment=sentiment,
#             confidence_score=confidence
# )

#         return redirect(request.path)

#     return render(request, "app/guest/chitietnoio.html", {
#         "listing": listing,
#         "reviews": reviews,
#         "avg_rating": avg_rating,
#         "can_review": can_review,
#         "review_status": review_status
#     })



# # from django.shortcuts import redirect, get_object_or_404
# # from django.contrib.auth.decorators import login_required

# # from app.models import Listing, Review
# # from app.sentiment import analyze_sentiment


# # @login_required
# # def submit_review(request, listing_id):
# #     if request.method != "POST":
# #         return redirect("listing_detail", listing_id=listing_id)

# #     listing = get_object_or_404(Listing, pk=listing_id)

# #     rating = int(request.POST.get("rating"))
# #     comment = request.POST.get("comment", "").strip()

# #     if not comment:
# #         return redirect("listing_detail", listing_id=listing_id)

# #     review = Review.objects.create(
# #         listing=listing,
# #         user=request.user,
# #         rating=rating,
# #         comment=comment
# #     )

# #     # 👉 ÁP DỤNG ViSoBERT NGAY KHI GỬI
# #     sentiment, confidence = analyze_sentiment(comment)
# #     review.analysis.create(
# #         sentiment=sentiment,
# #         confidence_score=confidence
# #     )

# #     return redirect("listing_detail", listing_id=listing_id)






from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Avg
from django.http import HttpResponseForbidden
from django.utils import timezone
from app.models import Listing, Booking, Review, ReviewAnalysis

# Giả định bạn đã có hàm này trong sentiment.py
from app.sentiment import analyze_sentiment 

def listing_detail(request, listing_id):
    # 1. Lấy thông tin Listing chính và các liên kết (Address, Host)
    # Dùng select_related và prefetch_related để tối ưu tốc độ load (giảm query)
    listing = get_object_or_404(
        Listing.objects.select_related('host', 'listingaddress'), 
        pk=listing_id
    )

    # 2. Lấy danh sách ảnh và tiện nghi (Dữ liệu thật từ Host đã đăng)
    images = listing.images.all()
    all_amenities = listing.amenities.all()
    # Phân loại tiện nghi theo category
    basic_amenities = all_amenities.filter(category='basic')
    featured_amenities = all_amenities.filter(category='featured')
    safety_amenities = all_amenities.filter(category='safety')
    address = getattr(listing, 'listingaddress', None)  # Lấy từ OneToOneField (có thể None)

    reviews = listing.reviews.select_related("user", "analysis").all()
    avg_rating = reviews.aggregate(avg=Avg("rating"))["avg"]

    booking = None
    can_review = False
    review_status = None

    # ====== XÁC ĐỊNH BOOKING ======
    if request.user.is_authenticated:
        today = timezone.localdate()

        # 🔥 TÌM BOOKING COMPLETED CHƯA CÓ REVIEW
        booking = Booking.objects.filter(
            listing=listing,
            user=request.user,
            booking_status="completed",
            check_out__lt=today,
            review__isnull=True   # 👈 MẤU CHỐT
        ).order_by("-check_out").first()

        if booking:
            can_review = True
            review_status = "pending_review"
        else:
            # Nếu user có booking completed nhưng tất cả đã review
            has_completed = Booking.objects.filter(
                listing=listing,
                user=request.user,
                booking_status="completed",
                check_out__lt=today
            ).exists()

            if has_completed:
                review_status = "reviewed"

    # ====== SUBMIT REVIEW ======
    if request.method == "POST":
        if not can_review or booking is None:
            return HttpResponseForbidden("Không có booking hợp lệ để đánh giá")

        rating = int(request.POST.get("rating"))
        comment = request.POST.get("comment", "").strip()

        # 1. Tạo review → PHẢI gán biến
        review = Review.objects.create(
            booking=booking,
            listing=listing,
            user=request.user,
            rating=rating,
            comment=comment
)
        # 2. Chạy ViSoBERT
        sentiment, confidence = analyze_sentiment(comment)

        # 3. Lưu kết quả phân tích
        ReviewAnalysis.objects.create(
            review=review,
            sentiment=sentiment,
            confidence_score=confidence
)
        return redirect(request.path)
    # 6. Tính avatar URL cho host (tránh lỗi ImageField rỗng)
    def get_avatar_url(user, size=100):
        try:
            if user.avatar and user.avatar.name:
                return user.avatar.url
        except (ValueError, AttributeError):
            pass
        return f"https://i.pravatar.cc/{size}?u={user.id}"
    
    host_avatar_url = get_avatar_url(listing.host, 60)
    
    # Thêm avatar URL cho mỗi review
    reviews_with_avatar = []
    for r in reviews:
        r.user_avatar_url = get_avatar_url(r.user, 40)
        reviews_with_avatar.append(r)

    # 7. Đổ dữ liệu vào Context để HTML sử dụng
    context = {
        "listing": listing,
        "address": address,
        "images": images,
        "amenities": all_amenities,
        "basic_amenities": basic_amenities,
        "featured_amenities": featured_amenities,
        "safety_amenities": safety_amenities,
        "host": listing.host,
        "host_avatar_url": host_avatar_url,
        "reviews": reviews_with_avatar,
        "avg_rating": avg_rating,
        "can_review": can_review,
        "review_status": review_status,
        "review_count": reviews.count(),
    }

    return render(request, "app/guest/chitietnoio.html", context)