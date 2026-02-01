from decimal import Decimal, ROUND_HALF_UP

from django.db import migrations


def _quantize(v):
    return v.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def forwards_fill_base_and_fee(apps, schema_editor):
    Booking = apps.get_model('app', 'Booking')

    qs = Booking.objects.select_related('listing')
    for booking in qs.iterator():
        try:
            if not booking.check_in or not booking.check_out:
                continue
            nights = (booking.check_out - booking.check_in).days
            if nights <= 0:
                continue

            listing = getattr(booking, 'listing', None)
            if not listing:
                continue

            price_per_night = getattr(listing, 'price_per_night', None)
            if price_per_night is None:
                continue

            base = _quantize(Decimal(str(price_per_night)) * Decimal(nights))
            service_fee = _quantize(base * Decimal('0.20'))

            Booking.objects.filter(pk=booking.pk).update(
                base_price=base,
                service_fee=service_fee,
            )
        except Exception:
            # keep migration resilient to bad rows
            continue


def backwards_clear_base_and_fee(apps, schema_editor):
    Booking = apps.get_model('app', 'Booking')
    Booking.objects.update(base_price=None, service_fee=None)


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0030_reviewclassification_reason'),
    ]

    operations = [
        migrations.RunPython(forwards_fill_base_and_fee, backwards_clear_base_and_fee),
        migrations.RemoveField(
            model_name='booking',
            name='total_price',
        ),
    ]
