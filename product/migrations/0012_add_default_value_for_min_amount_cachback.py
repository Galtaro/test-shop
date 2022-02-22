from django.db import migrations


def create_defaults(apps, schema_editor):
    UseCashbackAmount = apps.get_model("product", "UseCashbackAmount")
    UseCashbackAmount.objects.create(
        min_amount_use_cashback=100
    )


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0011_usecashbackamount_and_more'),
    ]
    operations = [
        migrations.RunPython(create_defaults)
    ]
