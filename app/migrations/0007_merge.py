"""Merge migration to resolve multiple leaf nodes in app migration graph.

Non-destructive: no operations, just merges heads 0005 and 0006.
"""
from django.db import migrations


class Migration(migrations.Migration):

    # Adjusted to remove dependency on missing 0006_create_verification.
    # This merge file now only depends on the current head 0005.
    dependencies = [
        ("app", "0005_indexes_and_constraints"),
    ]

    operations = []
