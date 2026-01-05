from django.contrib import admin
from .models import (
    TeacherInfo,
    TeacherNotification,
    TeacherLeave,
    Feedback,
    Attendance,
    AttendanceRecord,
)


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
admin.site.register(Feedback)


class AttendanceRecordInline(admin.TabularInline):
    model = AttendanceRecord
    extra = 0
    readonly_fields = ('student', 'status', 'marked_at')


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('date', 'teacher', 'klass', 'section', 'session', 'subject', 'created_at')
    list_filter = ('date', 'klass', 'section', 'session', 'subject')
    search_fields = ('teacher__first_name', 'teacher__last_name', 'klass__name', 'subject__name')
    inlines = [AttendanceRecordInline]
    readonly_fields = ('created_at', 'updated_at')


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('attendance', 'student', 'status', 'marked_at')
    list_filter = ('status',)
    search_fields = ('student__first_name', 'student__last_name', 'attendance__klass__name')
