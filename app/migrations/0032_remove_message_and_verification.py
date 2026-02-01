# Generated manually to remove Message and Verification models

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0031_remove_booking_total_price'),
    ]

    operations = [
        # Xóa bảng messages
        migrations.DeleteModel(
            name='Message',
        ),
        # Xóa bảng verifications
        migrations.DeleteModel(
            name='Verification',
        ),
    ]
