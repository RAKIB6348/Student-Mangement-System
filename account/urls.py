from django.urls import path
from .views import *

urlpatterns = [

    path('base/', dashboard_base_page, name='base'),

    # login urls
    path('', login_page, name='login_page'),
    path('login/', user_login, name='user_login'),
    path('logout/', user_logout, name='logout'),


    # profile
    path('profile/', profile_page, name='profile_page'),
    path('change-password/', change_password, name='change_password'),

    # password reset
    path('forgot-password/', forgot_password, name='forgot_password'),
    path('reset-password/<uidb64>/<token>/', reset_password, name='reset_password'),
]
