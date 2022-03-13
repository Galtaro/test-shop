from datetime import timedelta
from json import dumps

from django_celery_beat.models import PeriodicTask, ClockedSchedule


def create_task_send_notification(email_delivery_notification, delivery_date_time, order, email):
    """Create task for send notification before delivery. """

    date_time_notification = delivery_date_time - timedelta(
        hours=email_delivery_notification.hour_before_delivery)
    clocked_schedule = ClockedSchedule.objects.create(clocked_time=date_time_notification)
    PeriodicTask.objects.create(
        name="send_notification",
        task="product.tasks.send_delivery_notification",
        kwargs=dumps(
            {'order_id': order.id,
                'email': email,
                'clocked_id': clocked_schedule.id,
                'delivery_date_time': delivery_date_time.strftime('%Y-%m-%dT%H:%M:%S')
             }
            ),
        clocked=clocked_schedule,
        one_off=True
    )