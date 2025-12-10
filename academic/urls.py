from django.urls import path
from .views import *

urlpatterns = [
    
    # subject urls
    path('add-subject/', add_subject, name='add_subject'),
    path('subject-list/', subject_list, name='subject_list'),
    path('edit-subject/', edit_subject, name='edit_subject'),

    # class urls
    path('add-class/', add_class, name='add_class'),
    path('class-list/', class_list, name='class_list'),

    # section urls
    path('add-section/', add_section, name='add_section'),
    path('section-list/', section_list, name='section_list'),
    
    
    
    # session urls
    path('add-session/', add_session, name='add_session'),
    path('session-list/', session_list, name='session_list'),
   
]