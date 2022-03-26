from django.contrib.auth import get_user_model
from django.core.mail import send_mass_mail
from django.conf import settings
from celery import shared_task
from django.template.loader import render_to_string
from django.utils.html import strip_tags

User = get_user_model()

@shared_task
def send_promotional_offers():
    recipient_list = list(User.objects.filter(receive_promotional_offers=True).values_list("email", flat=True))
    subject = 'Stock news'
    html_message = render_to_string('mail_template.html', {'context': 'values'})
    plain_message = strip_tags(html_message)
    message = 'Current promotions of this period'
    email_from = settings.EMAIL_HOST_USER
    send_mass_mail(subject, message, email_from, recipient_list)
