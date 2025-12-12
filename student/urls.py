from django.urls import path
from .views import *

urlpatterns = [
    path('student-list/', student_list, name='student_list'),
    path('student-create/', student_create, name='student_create'),
    path('student-edit/<int:id>/', student_edit, name='student_edit'),
    path('student-delete/<int:id>/', student_delete, name='student_delete'),

    path('dashboard/', student_dashboard, name='student_dashboard'),
]
