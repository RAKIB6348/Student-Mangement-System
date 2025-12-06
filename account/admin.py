from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    # ✅ List view
    list_display = (
        "username",
        "first_name",
        "last_name",
        "email",
        "user_type",
        "user_id",
        "is_superuser",
        "is_staff",
        "is_active",
    )

    search_fields = ("username", "email", "user_id", "first_name", "last_name")
    ordering = ("id",)

    # ✅ Make user_id readonly
    readonly_fields = ("user_id",)

    # ✅ Edit page (Change User)
    fieldsets = UserAdmin.fieldsets + (
        ("Extra Info", {
            "fields": ("user_type", "user_id"),
        }),
    )

    # ✅ Add page (Create User)
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "password1", "password2", "user_type"),
        }),
    )
