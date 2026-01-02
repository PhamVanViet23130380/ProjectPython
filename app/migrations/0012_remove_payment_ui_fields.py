"""Drop leftover payment UI columns from the database without altering Django model state.

We use SeparateDatabaseAndState with RunSQL so this migration will attempt to drop
the physical columns if they exist, but will not modify the in-memory Django model
state (models.py already reflects the desired schema).
"""
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0011_remove_booking_guests_remove_payment_details_and_more"),
    ]

    def _drop_columns(apps, schema_editor):
        cols = [
            'provider',
            'payment_method_id',
            'card_last4',
            'card_exp_month',
            'card_exp_year',
            'billing_postal_code',
            'billing_country',
            'saved',
        ]
        table = 'payments'
        with schema_editor.connection.cursor() as cursor:
            for col in cols:
                cursor.execute(
                    "SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=%s AND COLUMN_NAME=%s",
                    [table, col],
                )
                exists = cursor.fetchone()[0]
                if exists:
                    cursor.execute(f"ALTER TABLE `{table}` DROP COLUMN `{col}`")

    operations = [
        migrations.RunPython(_drop_columns, migrations.RunPython.noop),
    ]
