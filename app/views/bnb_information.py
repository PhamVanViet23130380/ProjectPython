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

    # 3. Lấy đánh giá và tích hợp AI Sentiment
    reviews = listing.reviews.select_related("user", "analysis").all().order_by("-created_at")
    avg_rating = reviews.aggregate(avg=Avg("rating"))["avg"] or 0

    # 4. Logic kiểm tra quyền đánh giá (Chỉ khách đã ở xong mới được đánh giá)
    booking_to_review = None
    can_review = False
    review_status = None

    if request.user.is_authenticated:
        today = timezone.localdate()

        # Tìm booking đã hoàn tất (Completed), đã trả phòng và chưa có review
        booking_to_review = Booking.objects.filter(
            listing=listing,
            user=request.user,
            booking_status="completed", # Hoặc "confirmed" tùy status bạn đặt
            check_out__lt=today,
            review__isnull=True   
        ).order_by("-check_out").first()

        if booking_to_review:
            can_review = True
            review_status = "pending_review"
        else:
            # Kiểm tra nếu đã từng review rồi
            has_reviewed = Review.objects.filter(listing=listing, user=request.user).exists()
            if has_reviewed:
                review_status = "reviewed"

    # 5. Xử lý khi khách gửi đánh giá (POST)
    if request.method == "POST":
        if not can_review or booking_to_review is None:
            return HttpResponseForbidden("Bạn không có quyền đánh giá phòng này.")

        rating = int(request.POST.get("rating", 5))
        comment = request.POST.get("comment", "").strip()

        if comment:
            # Lưu Review vào DB
            new_review = Review.objects.create(
                booking=booking_to_review,
                listing=listing,
                user=request.user,
                rating=rating,
                comment=comment
            )
            
            # Chạy AI ViSoBERT phân tích cảm xúc
            try:
                sentiment_raw, raw_confidence = analyze_sentiment(comment)

                sentiment_raw = sentiment_raw.lower()

                sentiment = sentiment_raw


                confidence = round(raw_confidence, 2)

                ReviewAnalysis.objects.create(
                    review=new_review,
                    sentiment=sentiment,
                    confidence_score=confidence
                )


            except Exception as e:
                print(f"Lỗi AI: {e}")

            return redirect(request.path)

    context = {
        "listing": listing,
        "address": address,
        "images": images,
        "amenities": all_amenities,
        "basic_amenities": basic_amenities,
        "featured_amenities": featured_amenities,
        "safety_amenities": safety_amenities,
        "host": listing.host,
        "reviews": reviews,
        "avg_rating": avg_rating,
        "can_review": can_review,
        "review_status": review_status,
        "review_count": reviews.count(),
    }

    return render(request, "app/guest/chitietnoio.html", context)