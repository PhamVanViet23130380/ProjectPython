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
        pending_qs = Booking.objects.filter(booking_status='pending', created_at__lte=cutoff)
        pending_total = pending_qs.count()

        for b in pending_qs:
            b.booking_status = 'cancelled'
            b.save(update_fields=['booking_status'])

        today = timezone.localdate()
        in_progress_qs = Booking.objects.filter(
            booking_status='confirmed',
            check_in__lte=today,
            check_out__gte=today
        )
        in_progress_total = in_progress_qs.count()
        in_progress_qs.update(booking_status='in_progress')

        completed_qs = Booking.objects.filter(
            booking_status__in=['confirmed', 'in_progress'],
            check_out__lt=today
        )
        completed_total = completed_qs.count()
        completed_qs.update(booking_status='completed')

        self.stdout.write(self.style.SUCCESS(
            f'Expired pending: {pending_total} (TTL={ttl_minutes} minutes); '
            f'in_progress: {in_progress_total}; completed: {completed_total}.'
        ))
