"""
ZOARIA Celery Tasks - Phase 2 / 5A
Reminders, appointment notifications, welcome email, weekly digest
"""
import logging
from datetime import date, timedelta
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

logger = logging.getLogger(__name__)


def _profile_name(user, fallback='there'):
    try:
        return user.profile.name or fallback
    except Exception:
        return fallback


def _fmt_date(d):
    return d.strftime('%B %d, %Y') if d else '-'


def _send(subject, body, to):
    try:
        send_mail(
            subject=subject, message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to] if isinstance(to, str) else to,
            fail_silently=True,
        )
    except Exception as exc:
        logger.warning(f'Email failed to {to}: {exc}')


# 1. Daily reminder task
@shared_task(name='apps.tasks.reminders.send_due_reminders', bind=True, max_retries=3)
def send_due_reminders(self):
    from apps.calendar_app.models import Reminder
    from apps.notifications.models import Notification
    today = date.today()
    due = Reminder.objects.filter(sent=False, reminder_date__lte=today).select_related(
        'pet', 'pet__owner', 'pet__owner__profile')
    sent_count = 0
    for reminder in due:
        try:
            owner = reminder.pet.owner
            pet_name = reminder.pet.name
            r_type = reminder.get_reminder_type_display()
            title = reminder.title or r_type
            due_str = _fmt_date(reminder.reminder_date)
            Notification.send(user=owner, title=f'Reminder: {title} for {pet_name}',
                message=f'{r_type} for {pet_name} is due today ({due_str}).',
                notification_type=reminder.reminder_type)
            _send(
                subject=f'[ZOARIA] Reminder: {title} for {pet_name}',
                body=(f'Hi {_profile_name(owner)},\n\n'
                      f"{pet_name}'s {r_type.lower()} is due today.\n\n"
                      f'Due: {due_str}\nPet: {pet_name}\nNotes: {reminder.notes or "None"}\n\n'
                      f'{settings.FRONTEND_URL}/pets/{reminder.pet.id}?tab=calendar\n\n- ZOARIA'),
                to=owner.email)
            reminder.sent = True
            reminder.save(update_fields=['sent'])
            sent_count += 1
            if reminder.repeat_interval_days:
                reschedule_repeating_reminder.delay(reminder.id)
        except Exception as exc:
            logger.error(f'Reminder {reminder.id} failed: {exc}')
    logger.info(f'send_due_reminders: {sent_count} sent')
    return {'sent': sent_count}


# 2. Reschedule repeating reminders
@shared_task(name='apps.tasks.reminders.reschedule_repeating_reminder')
def reschedule_repeating_reminder(reminder_id: int):
    from apps.calendar_app.models import Reminder
    try:
        r = Reminder.objects.get(id=reminder_id)
        if not r.repeat_interval_days:
            return
        next_date = r.reminder_date + timedelta(days=r.repeat_interval_days)
        Reminder.objects.create(pet=r.pet, reminder_type=r.reminder_type,
            reminder_date=next_date, repeat_interval_days=r.repeat_interval_days,
            title=r.title, notes=r.notes, sent=False)
        logger.info(f'Reminder {reminder_id} rescheduled to {next_date}')
    except Reminder.DoesNotExist:
        logger.warning(f'Reminder {reminder_id} not found')


# 3. Hourly appointment reminder (24h window)
@shared_task(name='apps.tasks.reminders.send_appointment_reminders', bind=True, max_retries=3)
def send_appointment_reminders(self):
    from apps.calendar_app.models import Appointment
    from apps.notifications.models import Notification
    now = timezone.now()
    window_start = now + timedelta(hours=23, minutes=30)
    window_end = now + timedelta(hours=24, minutes=30)
    upcoming = Appointment.objects.filter(
        appointment_time__gte=window_start, appointment_time__lte=window_end,
        status__in=['pending', 'confirmed'],
    ).select_related('owner', 'owner__profile', 'vet', 'vet__profile', 'pet')
    count = 0
    for appt in upcoming:
        try:
            pet_name = appt.pet.name
            appt_str = appt.appointment_time.strftime('%B %d, %Y at %H:%M UTC')
            vet_name = f"Dr. {_profile_name(appt.vet, appt.vet.email)}"
            owner_name = _profile_name(appt.owner)
            Notification.send(user=appt.owner,
                title=f'Appointment tomorrow: {pet_name}',
                message=f'Appointment with {vet_name} for {pet_name} is tomorrow at {appt_str}.',
                notification_type='appointment')
            _send(
                subject=f'[ZOARIA] Appointment tomorrow - {pet_name}',
                body=(f'Hi {owner_name},\n\n'
                      f"Reminder: {pet_name}'s appointment with {vet_name} is tomorrow.\n\n"
                      f'{appt_str}\nNotes: {appt.notes or "None"}\n\n'
                      f'{settings.FRONTEND_URL}/appointments\n\n- ZOARIA'),
                to=appt.owner.email)
            Notification.send(user=appt.vet,
                title=f'Appointment tomorrow: {pet_name} ({owner_name})',
                message=f'Appointment with {owner_name} for {pet_name} tomorrow at {appt_str}.',
                notification_type='appointment')
            _send(
                subject=f'[ZOARIA] Appointment tomorrow - {pet_name}',
                body=(f'Hi {vet_name},\n\n'
                      f'Reminder: appointment with {owner_name} ({pet_name}) is tomorrow.\n\n'
                      f'{appt_str}\nNotes: {appt.notes or "None"}\n\n'
                      f'{settings.FRONTEND_URL}/vet\n\n- ZOARIA'),
                to=appt.vet.email)
            count += 1
        except Exception as exc:
            logger.error(f'Appt reminder failed for {appt.id}: {exc}')
    logger.info(f'send_appointment_reminders: {count} processed')
    return {'processed': count}


# 4. Welcome email
@shared_task(name='apps.tasks.reminders.send_welcome_email')
def send_welcome_email(user_id: int):
    from apps.users.models import User
    try:
        user = User.objects.select_related('profile').get(id=user_id)
        name = _profile_name(user)
        if user.role == 'owner':
            role_msg = 'You can now add pets, book appointments, and track health records.'
            cta = f'{settings.FRONTEND_URL}/dashboard'
        else:
            role_msg = 'Your account is under review. You will be notified once approved.'
            cta = f'{settings.FRONTEND_URL}/vet'
        _send(
            subject='Welcome to ZOARIA',
            body=(f'Hi {name},\n\nWelcome to ZOARIA - the complete veterinary ecosystem.\n\n'
                  f'{role_msg}\n\nGet started: {cta}\n\n- The ZOARIA Team'),
            to=user.email)
    except Exception as exc:
        logger.error(f'Welcome email failed for {user_id}: {exc}')


# 5. Weekly digest
@shared_task(name='apps.tasks.reminders.send_weekly_digest')
def send_weekly_digest():
    from apps.users.models import User
    from apps.calendar_app.models import Reminder, Appointment
    today = date.today()
    week_end = today + timedelta(days=7)
    owners = User.objects.filter(role='owner', is_active=True).prefetch_related(
        'pets', 'pets__breed', 'profile')
    sent = 0
    for owner in owners:
        try:
            pets = list(owner.pets.all())
            if not pets:
                continue
            reminders = list(Reminder.objects.filter(
                pet__owner=owner, sent=False,
                reminder_date__gte=today, reminder_date__lte=week_end,
            ).select_related('pet').order_by('reminder_date'))
            appts = list(Appointment.objects.filter(
                owner=owner, status__in=['pending', 'confirmed'],
                appointment_time__date__gte=today, appointment_time__date__lte=week_end,
            ).select_related('vet', 'vet__profile', 'pet').order_by('appointment_time'))
            warnings = [p for p in pets if p.weight_status in ('overweight', 'underweight')]
            if not reminders and not appts and not warnings:
                continue
            lines = [f"Hi {_profile_name(owner)},\n", "Your ZOARIA weekly summary:\n"]
            if warnings:
                lines.append('WEIGHT ALERTS:')
                for p in warnings:
                    lines.append(f'  - {p.name} is {p.weight_status} ({p.weight} kg)')
                lines.append('')
            if reminders:
                lines.append('REMINDERS DUE THIS WEEK:')
                for r in reminders:
                    lines.append(f'  - {r.pet.name}: {r.get_reminder_type_display()} on {_fmt_date(r.reminder_date)}')
                lines.append('')
            if appts:
                lines.append('UPCOMING APPOINTMENTS:')
                for a in appts:
                    vn = f"Dr. {_profile_name(a.vet, a.vet.email)}"
                    lines.append(f"  - {a.pet.name} with {vn} on {_fmt_date(a.appointment_time.date())}")
                lines.append('')
            lines.append(f'Dashboard: {settings.FRONTEND_URL}/dashboard\n\n- The ZOARIA Team')
            _send(subject='[ZOARIA] Weekly pet health summary',
                  body='\n'.join(lines), to=owner.email)
            sent += 1
        except Exception as exc:
            logger.error(f'Weekly digest failed for {owner.id}: {exc}')
    logger.info(f'send_weekly_digest: {sent} sent')
    return {'sent': sent}
