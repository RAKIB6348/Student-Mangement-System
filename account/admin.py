from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    # LIST VIEW
    list_display = (
        "username",
        "first_name",
        "last_name",
        "email",
        "user_type",
        "user_id",
        "gender",
        "phone",
        "is_superuser",
        "is_staff",
        "is_active",
    )

    search_fields = ("username", "email", "user_id", "first_name", "last_name", "phone")
    ordering = ("id",)

    readonly_fields = ("user_id",)

    # EDIT PAGE (Change User)
    fieldsets = UserAdmin.fieldsets + (
        ("Extra Information", {
            "fields": ("user_type", "user_id", "gender", "phone", "address", "profile_pic"),
        }),
    )

    # ADD PAGE (Create User)
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "username",
                "email",
                "password1",
                "password2",
                "user_type",
                "gender",
                "phone",
                "address",
                "profile_pic",
            ),
        }),
    )
