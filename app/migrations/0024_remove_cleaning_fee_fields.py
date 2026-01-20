from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0023_remove_safety_fields_from_listing"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="booking",
            name="cleaning_fee",
        ),
        migrations.RemoveField(
            model_name="listing",
            name="cleaning_fee",
        ),
    ]
