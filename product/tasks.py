from django.core.mail import send_mail
from django.conf import settings
from celery import shared_task

from django_celery_beat.models import ClockedSchedule
from product.models import Order


@shared_task
def send_delivery_notification(order_id, clocked_id, email, delivery_date_time):
    order = Order.objects.get(id=order_id)
    if order.payment_status:
        subject = 'Delivery service'
        message = f'Your order will be delivered {delivery_date_time}. Thank you for choosing us.'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email]
        send_mail(subject, message, email_from, recipient_list)
    ClockedSchedule.objects.get(id=clocked_id).delete()


