from django.urls import path
from .views import *

urlpatterns = [

    path('base/', dashboard_base_page, name=''),

    # login urls
    path('', login_page, name='login_page'),
    path('login/', user_login, name='user_login'),
    path('logout/', user_logout, name='logout'),
]
