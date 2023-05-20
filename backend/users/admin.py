from django.contrib import admin

from .models import Following, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "username",
        "email",
        "first_name",
        "last_name",
    )
    list_filter = (
        "email",
        "username",
    )
    search_fields = (
        "username",
        "email",
    )


@admin.register(Following)
class FollowingAdmin(admin.ModelAdmin):
    list_display = (
        "follower",
        "following",
    )
