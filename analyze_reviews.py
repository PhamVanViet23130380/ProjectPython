"""Script để phân tích sentiment cho các review cũ chưa được phân tích."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PythonAirBnb.settings')
django.setup()

from app.models import Review, ReviewAnalysis
from app.sentiment import analyze_sentiment
from decimal import Decimal, ROUND_HALF_UP

def analyze_pending_reviews():
    reviews_without_analysis = Review.objects.filter(analysis__isnull=True)
    count = reviews_without_analysis.count()
    print(f'Tim thay {count} review chua co phan tich')
    
    for review in reviews_without_analysis:
        try:
            sentiment, confidence = analyze_sentiment(review.comment)
            conf_dec = Decimal(str(confidence)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            ReviewAnalysis.objects.create(
                review=review,
                sentiment=sentiment,
                confidence_score=conf_dec
            )
            print(f'Da phan tich review {review.review_id}: {sentiment} ({conf_dec})')
        except Exception as e:
            print(f'Loi review {review.review_id}: {e}')

if __name__ == '__main__':
    analyze_pending_reviews()
