"""
Academic Module Views
=====================
This module contains all view functions for managing academic entities
including subjects, sections, sessions, and classes.

Author: Student Management System
Created: 2024
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Subject, Section, Session, Class

# ============================================================================
# SUBJECT VIEWS
# ============================================================================

def subject_list(request):
    
    return render(request, 'Academic/subject/subject_list.html')


def add_subject(request):
    if request.method == 'POST':
        try:
            # Get form data
            name = request.POST.get('name')
            code = request.POST.get('code')

            # Validate that fields are not empty
            if not name or not code:
                messages.error(request, 'Both Subject Name and Subject Code are required!')
                return render(request, 'Academic/subject/add_subject.html')

            # Check if subject code already exists
            if Subject.objects.filter(code=code).exists():
                messages.error(request, f'Subject with code "{code}" already exists!')
                return render(request, 'Academic/subject/add_subject.html')

            # Create Subject record
            Subject.objects.create(
                name=name,
                code=code
            )

            messages.success(request, f'Subject "{name}" (Code: {code}) added successfully!')
            return redirect('subject_list')

        except Exception as e:
            messages.error(request, f'Error creating subject: {str(e)}')

    return render(request, 'Academic/subject/add_subject.html')


def edit_subject(request):
   
    return render(request, 'Academic/subject/edit_subject.html')


# ============================================================================
# SECTION VIEWS
# ============================================================================

def section_list(request):
    
    return render(request, 'Academic/section/section_list.html')


def add_section(request):
    if request.method == 'POST':
        try:
            # Get form data
            name = request.POST.get('name')

            # Validate that field is not empty
            if not name:
                messages.error(request, 'Section name is required!')
                return render(request, 'Academic/section/add_section.html')

            # Create Section record
            Section.objects.create(name=name)

            messages.success(request, f'Section "{name}" added successfully!')
            return redirect('section_list')

        except Exception as e:
            messages.error(request, f'Error creating section: {str(e)}')

    return render(request, 'Academic/section/add_section.html')


# ============================================================================
# SESSION VIEWS
# ============================================================================

def session_list(request):
    
    return render(request, 'Academic/session/session_list.html')


def add_session(request):
    if request.method == 'POST':
        try:
            # Get form data
            name = request.POST.get('name')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')

            # Validate that fields are not empty
            if not name or not start_date or not end_date:
                messages.error(request, 'All fields are required!')
                return render(request, 'Academic/session/add_session.html')

            # Check if session name already exists
            if Session.objects.filter(name=name).exists():
                messages.error(request, f'Session "{name}" already exists!')
                return render(request, 'Academic/session/add_session.html')

            # Validate that start_date is before end_date
            from datetime import datetime
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            if start >= end:
                messages.error(request, 'Start date must be before end date!')
                return render(request, 'Academic/session/add_session.html')

            # Create Session record
            Session.objects.create(
                name=name,
                start_date=start_date,
                end_date=end_date
            )

            messages.success(request, f'Academic Session "{name}" added successfully!')
            return redirect('session_list')

        except Exception as e:
            messages.error(request, f'Error creating session: {str(e)}')

    return render(request, 'Academic/session/add_session.html')


# ============================================================================
# CLASS VIEWS
# ============================================================================

def add_class(request):
    if request.method == 'POST':
        try:
            # Get form data
            name = request.POST.get('name')
            class_code = request.POST.get('class_code')

            # Validate that fields are not empty
            if not name or not class_code:
                messages.error(request, 'Both Class Name and Class Code are required!')
                return render(request, 'Academic/class/add_class.html')

            # Validate class_code is a number between 1-99
            try:
                class_code_int = int(class_code)
                if class_code_int < 1 or class_code_int > 99:
                    messages.error(request, 'Class Code must be between 1 and 99!')
                    return render(request, 'Academic/class/add_class.html')
            except ValueError:
                messages.error(request, 'Class Code must be a valid number!')
                return render(request, 'Academic/class/add_class.html')

            # Check if class name already exists
            if Class.objects.filter(name=name).exists():
                messages.error(request, f'Class with name "{name}" already exists!')
                return render(request, 'Academic/class/add_class.html')

            # Create Class record
            Class.objects.create(
                name=name,
                class_code=class_code_int
            )

            messages.success(request, f'Class "{name}" (Code: {class_code_int}) added successfully!')
            return redirect('class_list')

        except Exception as e:
            messages.error(request, f'Error creating class: {str(e)}')

    return render(request, 'Academic/class/add_class.html')


def class_list(request):
    
    return render(request, 'Academic/class/class_list.html')
