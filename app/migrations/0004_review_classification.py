"""Create ReviewClassification model to mark spam reviews.

Non-destructive migration: adds `ReviewClassification` with OneToOne to `Review`.
"""
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0003_booking_note"),
    ]

    operations = [
        migrations.CreateModel(
            name='ReviewClassification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('spam_status', models.BooleanField(default=False)),
                ('review', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='app.review')),
            ],
            options={
                'db_table': 'review_classifications',
                'verbose_name': 'Phân loại đánh giá',
                'verbose_name_plural': 'Phân loại đánh giá',
            },
        ),
    ]
