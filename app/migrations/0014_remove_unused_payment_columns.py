"""
Remove unused columns from payments table.
These columns are not defined in the Payment model and contain only NULL values.
"""
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0013_add_missing_fields_safely'),
    ]

    def drop_unused_columns(apps, schema_editor):
        """Drop unused payment columns that are not in the model."""
        columns_to_drop = [
            'details',
            'card_brand',
            'provider',
            'metadata',
            'created_at',
        ]
        
        table = 'payments'
        with schema_editor.connection.cursor() as cursor:
            for col in columns_to_drop:
                # Check if column exists before dropping
                cursor.execute(
                    """
                    SELECT COUNT(*) 
                    FROM information_schema.COLUMNS 
                    WHERE TABLE_SCHEMA=DATABASE() 
                    AND TABLE_NAME=%s 
                    AND COLUMN_NAME=%s
                    """,
                    [table, col],
                )
                exists = cursor.fetchone()[0]
                
                if exists:
                    print(f"Dropping column: {col}")
                    cursor.execute(f"ALTER TABLE `{table}` DROP COLUMN `{col}`")
                else:
                    print(f"Column {col} does not exist, skipping")

    operations = [
        migrations.RunPython(drop_unused_columns, migrations.RunPython.noop),
    ]
