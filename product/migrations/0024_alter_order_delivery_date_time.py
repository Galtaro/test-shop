# Generated by Django 3.2.12 on 2022-03-16 15:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0023_add_default_value_for_delivery_date_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='delivery_date_time',
            field=models.DateTimeField(null=True),
        ),
    ]
