from django.contrib import admin
from .models import Subject, Session, Section, Class

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'created_at', 'updated_at')
    search_fields = ('name', 'code')


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'created_at', 'updated_at')
    search_fields = ('name',)
    ordering = ('-updated_at', '-start_date')



@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)
    ordering = ('-updated_at',)


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'class_code', 'created_at', 'updated_at')   # Table columns
    search_fields = ('name', 'class_code')                # Search support
