"""Add useful indexes for performance.

Non-destructive migration adding indexes on Listing.price_per_night,
Booking(listing, check_in) and Review.created_at.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0004_review_classification"),
    ]

    operations = [
        migrations.AddIndex(
            model_name='listing',
            index=models.Index(fields=['price_per_night'], name='listing_price_idx'),
        ),
        migrations.AddIndex(
            model_name='booking',
            index=models.Index(fields=['listing', 'check_in'], name='booking_listing_checkin_idx'),
        ),
        migrations.AddIndex(
            model_name='review',
            index=models.Index(fields=['created_at'], name='review_created_idx'),
        ),
    ]
