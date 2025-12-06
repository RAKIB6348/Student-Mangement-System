from django.contrib import admin
from .models import AdminProfile


@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):

    # List page view
    list_display = (
        'admin_user_id',
        'user',
        'first_name',
        'last_name',
        'phone',
        'email',
        'designation',
        'gender',
        'created_at'
    )

    # Right-side filters
    list_filter = ('gender', 'designation', 'created_at')

    # Search support
    search_fields = (
        'admin_user_id',
        'user__username',
        'first_name',
        'last_name',
        'email',
        'phone'
    )

    ordering = ('id',)

    # Form UI layout inside Admin
    fieldsets = (
        ("Admin User", {
            'fields': ('user', 'admin_user_id')
        }),
        ("Personal Details", {
            'fields': ('first_name', 'last_name', 'gender', 'email', 'phone')
        }),
        ("Job Details", {
            'fields': ('designation', 'address')
        }),
        ("Profile Image", {
            'fields': ('profile_pic',)
        }),
        ("Timestamps", {
            'fields': ('created_at', 'updated_at')
        }),
    )

    readonly_fields = ('admin_user_id', 'created_at', 'updated_at')   # ID auto-fill hobe edit na
