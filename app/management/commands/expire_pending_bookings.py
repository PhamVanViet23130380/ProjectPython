from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from app.models import Booking


class Command(BaseCommand):
    help = 'Expire pending bookings older than TTL (minutes) and mark them cancelled.'

    def add_arguments(self, parser):
        parser.add_argument('--minutes', type=int, default=30, help='TTL in minutes for pending bookings')

    def handle(self, *args, **options):
        ttl_minutes = options.get('minutes', 30)
        cutoff = timezone.now() - timedelta(minutes=ttl_minutes)
        qs = Booking.objects.filter(booking_status='pending', created_at__lte=cutoff)
        total = qs.count()
        if total == 0:
            self.stdout.write(self.style.SUCCESS('No pending bookings to expire.'))
            return

        for b in qs:
            b.booking_status = 'cancelled'
            b.save()

        self.stdout.write(self.style.SUCCESS(f'Expired {total} pending bookings (TTL={ttl_minutes} minutes).'))
