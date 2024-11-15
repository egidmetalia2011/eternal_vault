from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from .models import UserProfile

def notify_admin_for_mail(user_profile):
    subject = 'Reminder: Physical mail rquired for Encrypted Key'
    message = (
        f"User '{user_profile.first_name}' has reached their target date.\n\n"
        f"Please send the physical mail with the encrypted key.\n\n"
        f"Details:\n"
        f"Recipient Name: {user_profile.recipient_name}\n"
        f"Home Address: {user_profile.home_address}\n"
        f"Target Date: {user_profile.target_date}\n"
    )
    send_mail(
        subject,
        message,
        'no-reply@eternalvault.com',
        [settings.ADMIN_EMAIL],
        fail_silently=False,
    )

def check_and_notify_admin():
    """Periodically check if any user have reached their tager date and send reminder to the admin email for physical mail"""
    today = timezone.now().date()
    profiles_to_notify = UserProfile.objects.filter(target_date__lte=today)

    for profile in profiles_to_notify:
        notify_admin_for_mail(profile)