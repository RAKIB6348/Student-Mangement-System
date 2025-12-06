from django.urls import path
from .views import *

urlpatterns = [
    path('add-subject/', add_subject, name='add_subject'),
]