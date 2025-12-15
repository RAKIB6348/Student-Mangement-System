from django.urls import path
from .views import *

urlpatterns = [
    
    # subject urls
    path('add-subject/', add_subject, name='add_subject'),
    path('subject-list/', subject_list, name='subject_list'),
    path('subject-detail/<int:subject_id>/', subject_detail, name='subject_detail'),
    path('edit-subject/<int:subject_id>/', edit_subject, name='edit_subject'),
    path('delete-subject/<int:subject_id>/', delete_subject, name='delete_subject'),

    # class urls
    path('add-class/', add_class, name='add_class'),
    path('class-list/', class_list, name='class_list'),
    path('class-detail/<int:class_id>/', class_detail, name='class_detail'),
    path('edit-class/<int:class_id>/', edit_class, name='edit_class'),
    path('delete-class/<int:class_id>/', delete_class, name='delete_class'),

    # section urls
    path('add-section/', add_section, name='add_section'),
    path('section-list/', section_list, name='section_list'),
    path('section-detail/<int:section_id>/', section_detail, name='section_detail'),
    path('edit-section/<int:section_id>/', edit_section, name='edit_section'),
    path('delete-section/<int:section_id>/', delete_section, name='delete_section'),
    
    
    
    # session urls
    path('add-session/', add_session, name='add_session'),
    path('session-list/', session_list, name='session_list'),
    path('session-detail/<int:session_id>/', session_detail, name='session_detail'),
    path('edit-session/<int:session_id>/', edit_session, name='edit_session'),
    path('delete-session/<int:session_id>/', delete_session, name='delete_session'),
   
]
