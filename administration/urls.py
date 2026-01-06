from django.urls import path
from .views import *

urlpatterns = [
    path('dashboard/', admin_home_page, name='admin_home_page'),

    path('register-admin/', register_admin, name='register_admin'),
    path('admin-list/', admin_list, name='admin_list'),
    path('admin-detail/<int:id>/', admin_detail, name='admin_detail'),
    path('admin-edit/<int:id>/', admin_edit, name='admin_edit'),
    path('admin-delete/<int:id>/', admin_delete, name='admin_delete'),

    path('attendance/', attendance_overview, name='admin_attendance'),
    path('send-teacher-notification/', send_teacher_notification, name='send_teacher_notification'),
    path('view-teacher-notifications/', view_teacher_notifications, name='view_teacher_notifications'),
    path('send-student-notification/', send_student_notification, name='send_student_notification'),
    path('view-student-notifications/', view_student_notifications, name='view_student_notifications'),
    path('teacher-leave/', teacher_leave, name='teacher_leave'),
    path('student-leave/', student_leave, name='student_leave'),
    path('teacher-feedback/', teacher_feedback_admin, name='teacher_feedback_admin'),
    path('student-feedback/', student_feedback_admin, name='student_feedback_admin'),
]
