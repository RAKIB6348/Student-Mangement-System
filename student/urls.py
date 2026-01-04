from django.urls import path
from .views import *

urlpatterns = [
    path('student-list/', student_list, name='student_list'),
    path('student-detail/<int:id>/', student_detail, name='student_detail'),
    path('student-create/', student_create, name='student_create'),
    path('student-edit/<int:id>/', student_edit, name='student_edit'),
    path('student-delete/<int:id>/', student_delete, name='student_delete'),

    path('dashboard/', student_dashboard, name='student_dashboard'),
    path('notifications/', student_notification, name='student_notification'),
    path('feedback/', student_feedback, name='student_feedback'),
    path('leave/', student_apply_leave, name='student_apply_leave'),
]
