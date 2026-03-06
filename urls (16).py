"""
python manage.py setup_zoaria

One-time setup command that:
1. Runs all migrations
2. Seeds reference data (species, breeds, feeding guidelines)
3. Creates a default superuser if SUPERUSER_EMAIL/PASSWORD env vars are set
4. Creates sample Celery beat periodic tasks in the database
"""
import os
from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Run full ZOARIA initial setup: migrate, seed, create superuser, register beat tasks'

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('\n🔧 ZOARIA Setup Starting...\n'))

        # 1. Migrate
        self.stdout.write('  → Running migrations...')
        call_command('migrate', '--noinput', verbosity=0)
        self.stdout.write(self.style.SUCCESS('  ✓ Migrations complete'))

        # 2. Seed reference data
        self.stdout.write('  → Seeding reference data...')
        call_command('seed_db', verbosity=0)
        self.stdout.write(self.style.SUCCESS('  ✓ Reference data seeded'))

        # 3. Create superuser from env vars
        email    = os.environ.get('SUPERUSER_EMAIL')
        password = os.environ.get('SUPERUSER_PASSWORD')
        if email and password:
            from apps.users.models import User
            if not User.objects.filter(email=email).exists():
                User.objects.create_superuser(email=email, password=password)
                self.stdout.write(self.style.SUCCESS(f'  ✓ Superuser created: {email}'))
            else:
                self.stdout.write(f'  → Superuser {email} already exists, skipping')

        # 4. Register periodic tasks in Celery beat DB scheduler
        try:
            from django_celery_beat.models import PeriodicTask, CrontabSchedule
            import json

            # Daily reminders at 08:00
            daily_sched, _ = CrontabSchedule.objects.get_or_create(
                minute='0', hour='8', day_of_week='*',
                day_of_month='*', month_of_year='*')
            PeriodicTask.objects.update_or_create(
                name='Send due reminders (daily)',
                defaults={'task': 'apps.tasks.reminders.send_due_reminders',
                          'crontab': daily_sched, 'args': json.dumps([])})

            # Hourly appointment reminders
            hourly_sched, _ = CrontabSchedule.objects.get_or_create(
                minute='0', hour='*', day_of_week='*',
                day_of_month='*', month_of_year='*')
            PeriodicTask.objects.update_or_create(
                name='Send appointment reminders (hourly)',
                defaults={'task': 'apps.tasks.reminders.send_appointment_reminders',
                          'crontab': hourly_sched, 'args': json.dumps([])})

            # Weekly digest Mondays 09:00
            weekly_sched, _ = CrontabSchedule.objects.get_or_create(
                minute='0', hour='9', day_of_week='1',
                day_of_month='*', month_of_year='*')
            PeriodicTask.objects.update_or_create(
                name='Weekly owner digest (Monday)',
                defaults={'task': 'apps.tasks.reminders.send_weekly_digest',
                          'crontab': weekly_sched, 'args': json.dumps([])})

            self.stdout.write(self.style.SUCCESS('  ✓ Celery beat periodic tasks registered'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  ⚠ Could not register beat tasks: {e}'))

        self.stdout.write(self.style.SUCCESS('\n✅ ZOARIA setup complete!\n'))
