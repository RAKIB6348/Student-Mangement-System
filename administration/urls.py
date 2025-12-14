from django.urls import path
from .views import *

urlpatterns = [
    path('dashboard/', admin_home_page, name='admin_home_page'),

    path('register-admin/', register_admin, name='register_admin'),
    path('admin-list/', admin_list, name='admin_list'),
    path('admin-edit/<int:id>/', admin_edit, name='admin_edit'),
    path('admin-delete/<int:id>/', admin_delete, name='admin_delete'),

    path('send-teacher-notification/', send_teacher_notification, name='send_teacher_notification'),
]
