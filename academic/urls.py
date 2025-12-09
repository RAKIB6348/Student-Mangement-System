from django.urls import path
from .views import *

urlpatterns = [
    
    # subject urls
    path('add-subject/', add_subject, name='add_subject'),
    path('subject-list/', subject_list, name='subject_list'),
    path('edit-subject/', edit_subject, name='edit_subject'),
    
    path('add-section/', add_section, name='add_section'),
    path('add-session/', add_session, name='add_session'),
    path('add-class/', add_class, name='add_class'),
]