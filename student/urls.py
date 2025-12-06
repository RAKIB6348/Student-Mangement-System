from django.urls import path
from .views import *

urlpatterns = [
    path('student-list/', student_list, name='student_list'),
    path('student-create/', student_create, name='student_create'),
]
