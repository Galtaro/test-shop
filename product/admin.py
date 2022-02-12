from django.contrib import admin
from product.models import Item


class ItemAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "price", "image")
    list_display_links = ("title", "description", "price")
    search_fields = ("title", )


admin.site.register(Item, ItemAdmin)