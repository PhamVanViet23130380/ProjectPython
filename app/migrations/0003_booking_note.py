"""Add `note` field to Booking.

Non-destructive migration adding an optional `note` TextField.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0002_listing_amenities_verification"),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='note',
            field=models.TextField(blank=True, default='', null=True),
        ),
    ]
