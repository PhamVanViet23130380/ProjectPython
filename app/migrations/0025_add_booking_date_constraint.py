from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0024_remove_cleaning_fee_fields'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='booking',
            constraint=models.CheckConstraint(
                check=models.Q(check_out__gt=models.F('check_in')),
                name='booking_check_out_gt_check_in',
            ),
        ),
    ]
