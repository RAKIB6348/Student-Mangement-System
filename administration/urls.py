from django.urls import path
from .views import *

urlpatterns = [
    path('dashboard/', admin_home_page, name='admin_home_page'),

    path('register-admin/', register_admin, name='register_admin'),
    path('admin-list/', admin_list, name='admin_list'),
]
