import time

from django.core.management.base import BaseCommand

from engagement_api.tasks import check_follower_counts


class Command(BaseCommand):
    help = 'Check follower counts for all profiles and send milestone alerts'

    def add_arguments(self, parser):
        parser.add_argument(
            '--once',
            action='store_true',
            help='Run check once and exit (default: run periodically)',
        )
        parser.add_argument(
            '--interval',
            type=int,
            default=300,
            help='Interval in seconds between checks (default: 300)',
        )

    def handle(self, *args, **options):
        if options['once']:
            self.stdout.write('Running follower count check once...')
            check_follower_counts()
            self.stdout.write(self.style.SUCCESS('Check completed!'))
        else:
            interval = options['interval']
            self.stdout.write(
                self.style.SUCCESS(
                    f'Starting periodic follower count checks (interval: {interval}s)...'
                )
            )
            self.stdout.write('Press Ctrl+C to stop.')

            try:
                while True:
                    check_follower_counts()
                    self.stdout.write(f'Check completed. Waiting {interval}s for next check...')
                    time.sleep(interval)
            except KeyboardInterrupt:
                self.stdout.write(self.style.SUCCESS('\nStopped periodic checks.'))
