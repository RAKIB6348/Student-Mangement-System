from django.contrib import admin
from .models import TeacherInfo


@admin.register(TeacherInfo)
class TeacherInfoAdmin(admin.ModelAdmin):

    # Admin list display + created_at added
    list_display = (
        'teacher_user_id',
        'user',
        'first_name',
        'last_name',
        'phone',
        'email',
        'designation',
        'joining_date',
        'created_at',     # 👈 newly added column
    )


    search_fields = (
        'teacher_user_id',
        'user__username',
        'first_name',
        'last_name',
        'email',
        'phone',
    )

    ordering = ('id',)

    fieldsets = (
        ("Teacher User", {
            'fields': ('user', 'teacher_user_id')
        }),
        ("Personal Information", {
            'fields': ('first_name', 'last_name', 'gender', 'email', 'phone')
        }),
        ("Job Information", {
            'fields': ('designation', 'joining_date')
        }),
        ("Address & Photo", {
            'fields': ('address', 'profile_pic')
        }),
        ("Timestamps", {
            'fields': ('created_at',)
        }),
    )

    readonly_fields = ('teacher_user_id', 'created_at')  # both generated → no manual edit
