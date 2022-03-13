from django.db import migrations


def create_defaults(apps, schema_editor):
    EmailDeliveryNotification = apps.get_model("product", "EmailDeliveryNotification")
    EmailDeliveryNotification.objects.create(
        hour_before_delivery=None,
        title="Do not deliver notification"
    )


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0022_alter_emaildeliverynotification_hour_before_delivery'),
    ]
    operations = [
        migrations.RunPython(create_defaults)
    ]