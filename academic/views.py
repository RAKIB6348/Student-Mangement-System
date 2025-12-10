"""
Academic Module Views
=====================
This module contains all view functions for managing academic entities
including subjects, sections, sessions, and classes.

Author: Student Management System
Created: 2024
"""

from django.shortcuts import render

# ============================================================================
# SUBJECT VIEWS
# ============================================================================

def subject_list(request):
    
    return render(request, 'Academic/subject/subject_list.html')


def add_subject(request):
    
    return render(request, 'Academic/subject/add_subject.html')


def edit_subject(request):
   
    return render(request, 'Academic/subject/edit_subject.html')


# ============================================================================
# SECTION VIEWS
# ============================================================================

def section_list(request):
    
    return render(request, 'Academic/section/section_list.html')


def add_section(request):
    
    return render(request, 'Academic/section/add_section.html')


# ============================================================================
# SESSION VIEWS
# ============================================================================

def session_list(request):
    
    return render(request, 'Academic/session/session_list.html')


def add_session(request):
    
    return render(request, 'Academic/session/add_session.html')


# ============================================================================
# CLASS VIEWS
# ============================================================================

def add_class(request):
    
    return render(request, 'Academic/class/add_class.html')


def class_list(request):
    
    return render(request, 'Academic/class/class_list.html')
