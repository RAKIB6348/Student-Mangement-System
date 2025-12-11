from django.urls import path
from .views import *

urlpatterns = [
    
    # subject urls
    path('add-subject/', add_subject, name='add_subject'),
    path('subject-list/', subject_list, name='subject_list'),
    path('edit-subject/<int:subject_id>/', edit_subject, name='edit_subject'),
    path('delete-subject/<int:subject_id>/', delete_subject, name='delete_subject'),

    # class urls
    path('add-class/', add_class, name='add_class'),
    path('class-list/', class_list, name='class_list'),
    path('edit-class/<int:class_id>/', edit_class, name='edit_class'),
    path('delete-class/<int:class_id>/', delete_class, name='delete_class'),

    # section urls
    path('add-section/', add_section, name='add_section'),
    path('section-list/', section_list, name='section_list'),
    path('edit-section/<int:section_id>/', edit_section, name='edit_section'),
    path('delete-section/<int:section_id>/', delete_section, name='delete_section'),
    
    
    
    # session urls
    path('add-session/', add_session, name='add_session'),
    path('session-list/', session_list, name='session_list'),
    path('edit-session/<int:session_id>/', edit_session, name='edit_session'),
    path('delete-session/<int:session_id>/', delete_session, name='delete_session'),
   
]