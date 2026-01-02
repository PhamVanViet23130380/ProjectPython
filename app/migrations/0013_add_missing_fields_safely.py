# Generated manually - safely add fields that may already exist
from django.db import migrations, models, connection


def check_column_exists(table_name, column_name):
    """Check if a column exists in the database."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = %s
            AND COLUMN_NAME = %s
        """, [table_name, column_name])
        return cursor.fetchone()[0] > 0


def add_booking_fields(apps, schema_editor):
    """Add booking fields if they don't exist."""
    db_alias = schema_editor.connection.alias
    
    if not check_column_exists('bookings', 'guests'):
        schema_editor.execute(
            "ALTER TABLE bookings ADD COLUMN guests INT NOT NULL DEFAULT 1"
        )
    
    if not check_column_exists('bookings', 'base_price'):
        schema_editor.execute(
            "ALTER TABLE bookings ADD COLUMN base_price DECIMAL(10, 2) NULL"
        )
    
    if not check_column_exists('bookings', 'service_fee'):
        schema_editor.execute(
            "ALTER TABLE bookings ADD COLUMN service_fee DECIMAL(10, 2) NULL"
        )
    
    if not check_column_exists('bookings', 'cleaning_fee'):
        schema_editor.execute(
            "ALTER TABLE bookings ADD COLUMN cleaning_fee DECIMAL(10, 2) NULL"
        )


def add_payment_fields(apps, schema_editor):
    """Add payment fields if they don't exist."""
    if not check_column_exists('payments', 'transaction_id'):
        schema_editor.execute(
            "ALTER TABLE payments ADD COLUMN transaction_id VARCHAR(255) NULL UNIQUE"
        )


def add_listing_fields(apps, schema_editor):
    """Add listing fields if they don't exist."""
    if not check_column_exists('listings', 'cleaning_fee'):
        schema_editor.execute(
            "ALTER TABLE listings ADD COLUMN cleaning_fee DECIMAL(10, 2) NOT NULL DEFAULT 0"
        )
    
    if not check_column_exists('listings', 'extra_guest_fee'):
        schema_editor.execute(
            "ALTER TABLE listings ADD COLUMN extra_guest_fee DECIMAL(10, 2) NULL"
        )
    
    if not check_column_exists('listings', 'weekend_multiplier'):
        schema_editor.execute(
            "ALTER TABLE listings ADD COLUMN weekend_multiplier DECIMAL(3, 2) NOT NULL DEFAULT 1.00"
        )


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0012_remove_payment_ui_fields'),
    ]
    
    # Disable atomic to allow DDL in RunPython
    atomic = False

    operations = [
        migrations.RunPython(add_booking_fields, migrations.RunPython.noop),
        migrations.RunPython(add_payment_fields, migrations.RunPython.noop),
        migrations.RunPython(add_listing_fields, migrations.RunPython.noop),
    ]
