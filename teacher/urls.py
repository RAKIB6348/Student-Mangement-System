from django.urls import path
from .views import *

urlpatterns = [
    path('teacher-list', teacher_list, name='teacher_list'),
]
