from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task(name="send_email_to_user")
def send_email_task(subject, message, recipient_list):
    send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)
