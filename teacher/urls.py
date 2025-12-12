from django.urls import path
from .views import *

urlpatterns = [
    path('teacher-list', teacher_list, name='teacher_list'),
    path('teacher-create/', add_teacher, name='add_teacher'),
    path('teacher-edit/<int:id>/', teacher_edit, name='teacher_edit'),
    path('teacher-delete/<int:id>/', teacher_delete, name='teacher_delete'),

    path('dashboard/', teacher_dashboard, name='teacher_dashboard'),
]
