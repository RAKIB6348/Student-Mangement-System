from django.contrib import admin
from .models import TeacherInfo, TeacherNotification, TeacherLeave


@admin.register(TeacherInfo)
class TeacherInfoAdmin(admin.ModelAdmin):

    # Admin list display + created_at added
    list_display = (
        'teacher_user_id',
        'user',
        'first_name',
        'last_name',
        'gender',
        'phone',
        'email',
        'designation',
        'joining_date',
        'created_at',
    )


    search_fields = (
        'teacher_user_id',
        'user__username',
        'first_name',
        'last_name',
        'email',
        'phone',
        'designation',
    )

    ordering = ('id',)

    fieldsets = (
        ("Teacher User", {
            'fields': ('user', 'teacher_user_id')
        }),
        ("Personal Information", {
            'fields': ('first_name', 'last_name', 'gender', 'date_of_birth', 'email', 'phone', 'profile_pic')
        }),
        ("Job Information", {
            'fields': ('designation', 'joining_date', 'qualification', 'experience')
        }),
        ("Address Information", {
            'fields': ('present_address', 'permanent_address')
        }),
        ("Timestamps", {
            'fields': ('created_at',)
        }),
    )

    readonly_fields = ('teacher_user_id', 'created_at')  # both generated → no manual edit



admin.site.register(TeacherNotification)
admin.site.register(TeacherLeave)
