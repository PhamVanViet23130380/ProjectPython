from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Avg
from django.http import HttpResponseForbidden
from django.utils import timezone
from app.models import Listing, Booking, Review, ReviewAnalysis, ReviewMedia, ReviewClassification
from django.db.models import Q
import re
# Giả định bạn đã có hàm này trong sentiment.py
from app.sentiment import analyze_sentiment 

import os
from django.core.files.storage import default_storage

def handle_uploaded_file(f):
    path = default_storage.save(f"reviews/{f.name}", f)
    return default_storage.url(path)


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
    # reviews = listing.reviews.select_related("user", "analysis").all().order_by("-created_at")
    
    reviews = listing.reviews.filter(Q(reviewclassification__spam_status=False) |Q(reviewclassification__isnull=True)).select_related("user", "analysis").prefetch_related("media").order_by("-created_at")
    avg_rating = reviews.aggregate(avg=Avg("rating"))["avg"] or 0

    # Đếm số đánh giá tích cực và tiêu cực
    positive_count = 0
    negative_count = 0
    for r in reviews:
        try:
            if r.analysis:
                sentiment = r.analysis.sentiment
                if sentiment in ['pos', 'positive']:
                    positive_count += 1
                elif sentiment in ['neg', 'negative']:
                    negative_count += 1
        except Exception:
            pass

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
            reviews = listing.reviews.filter(
            reviewclassification__spam_status=False
                ).select_related(
                    "user", "analysis"
                ).prefetch_related(
                    "media"
                )

            # sau khi tạo new_review
            # ===== LƯU ẢNH / VIDEO REVIEW =====
            files = request.FILES.getlist("media")

            for f in files:
                ReviewMedia.objects.create(
                    review=new_review,
                    media=f,
                    media_type="image" if f.content_type.startswith("image") else "video"
                )



            # Chạy AI ViSoBERT phân tích cảm xúc
            # CHONG SPAM
            spam_reasons = []

            # 1. Lap tu
            words = comment.lower().split()
            if len(words) >= 6:
                unique_ratio = len(set(words)) / len(words)
                if unique_ratio < 0.3:
                    spam_reasons.append("tu_lap_lai")
                    spam_reasons.append("noi_dung_vo_nghia")

            # 5. Chua link
            url_pattern = r"(https?://|www\.)\S+"
            if re.search(url_pattern, comment.lower()):
                spam_reasons.append("gan_link")

            spam = ("gan_link" in spam_reasons or len(spam_reasons) >= 2)

            sentiment = "neu"
            confidence = 0.0
            try:
                sentiment_raw, raw_confidence = analyze_sentiment(comment)

                # Chuan hoa nhan sentiment
                sentiment_raw = sentiment_raw.lower()

                if sentiment_raw in ["positive", "pos"]:
                    sentiment = "pos"
                elif sentiment_raw in ["neutral", "neu"]:
                    sentiment = "neu"
                elif sentiment_raw in ["negative", "neg"]:
                    sentiment = "neg"
                else:
                    sentiment = "neu"

                confidence = round(raw_confidence, 2)
            except Exception as e:
                print(f"Loi AI: {e}")

            ReviewAnalysis.objects.create(
                review=new_review,
                sentiment=sentiment,
                confidence_score=confidence
            )

            ReviewClassification.objects.update_or_create(
                review=new_review,
                defaults={"spam_status": spam, "reason": spam_reasons}
            )

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
        "positive_count": positive_count,
        "negative_count": negative_count,
        "can_review": can_review,
        "review_status": review_status,
        "review_count": reviews.count(),
    }

    return render(request, "app/guest/chitietnoio.html", context)