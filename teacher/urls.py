from django.urls import path
from .views import *

urlpatterns = [
    path('teacher-list', teacher_list, name='teacher_list'),
    path('teacher-detail/<int:id>/', teacher_detail, name='teacher_detail'),
    path('teacher-create/', add_teacher, name='add_teacher'),
    path('teacher-edit/<int:id>/', teacher_edit, name='teacher_edit'),
    path('teacher-delete/<int:id>/', teacher_delete, name='teacher_delete'),

    path('dashboard/', teacher_dashboard, name='teacher_dashboard'),
    path('take-attendance/', take_attendance, name='take_attendance'),
    path('attendance-history/', view_update_attendance, name='view_update_attendance'),
    
    path('notifications/', teacher_notification, name='teacher_notification'),
    path('apply-leave/', apply_leave, name='apply_leave'),

    path('feedback/', teacher_feedback, name='teacher_feedback'),

]
