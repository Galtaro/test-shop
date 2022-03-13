from django.contrib import admin
from rest_framework.exceptions import ValidationError

from product.models import Item, EmailDeliveryNotification


class ItemAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "price", "image")
    list_display_links = ("title", "description", "price")
    search_fields = ("title", )


class EmailDeliveryNotificationAdmin(admin.ModelAdmin):
    list_display = ("hour_before_delivery", "title")
    ordering = ("hour_before_delivery",)

    def save_model(self, request, obj, form, change):
        if obj.hour_before_delivery <= 0:
            raise ValidationError({
                "detail": "Enter a value greater than or equal to one"
            }, code='invalid')
        obj.save()

    def delete_model(self, request, obj):
        if obj.id == 1:
            raise ValidationError({
                "detail": "You cannot delete this entry"
            }, code='invalid')
        obj.delete()


admin.site.register(Item, ItemAdmin)
admin.site.register(EmailDeliveryNotification, EmailDeliveryNotificationAdmin)
