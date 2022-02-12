from django.db import models
from django.contrib.auth.models import AbstractUser, Group


class CustomUser(AbstractUser):
    phone = models.CharField(max_length=15, verbose_name="phone number", unique=True, null=True, blank=True)

    class Meta(AbstractUser.Meta):
        swappable = 'AUTH_USER_MODEL'

    def display_group(self):
        return ', '.join([group.name for group in self.groups.all()])

    display_group.short_description = 'Group'


def add_customuser_group(signal, sender, instance, created, update_fields, raw, using, **kwargs):
    if created:
        client_group = Group.objects.get(name="Clients")
        instance.groups.add(client_group)
        instance.save()


models.signals.post_save.connect(add_customuser_group, sender=CustomUser)



