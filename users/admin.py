from django.contrib import admin

from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "group_type", "access_level")
    search_fields = ("user__username", "user__email")
    list_filter = ("group_type", "access_level")
