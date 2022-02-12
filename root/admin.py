from django.contrib import admin
from root.models import CustomUser


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("username", "is_staff", "display_group", "is_active", "date_joined")
    search_fields = ("is_staff", "is_active")
    ordering = ("is_staff",)


admin.site.register(CustomUser, CustomUserAdmin)

