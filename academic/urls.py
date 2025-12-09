from django.urls import path
from .views import *

urlpatterns = [
    path('add-subject/', add_subject, name='add_subject'),
    path('add-section/', add_section, name='add_section'),
    path('add-session/', add_session, name='add_session'),
    path('add-class/', add_class, name='add_class'),
]