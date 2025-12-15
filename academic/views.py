"""
Academic Module Views
=====================
This module contains all view functions for managing academic entities
including subjects, sections, sessions, and classes.

Author: Student Management System
Created: 2024
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Subject, Section, Session, Class

# ============================================================================
# SUBJECT VIEWS
# ============================================================================

def subject_list(request):
    subjects = Subject.objects.all().order_by('-created_at')
    context = {
        'subjects': subjects
    }
    return render(request, 'Academic/subject/subject_list.html', context)


def subject_detail(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    context = {
        'subject': subject
    }
    return render(request, 'Academic/subject/subject_detail.html', context)


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


def edit_subject(request, subject_id):
    try:
        subject = Subject.objects.get(id=subject_id)
    except Subject.DoesNotExist:
        messages.error(request, 'Subject not found!')
        return redirect('subject_list')

    if request.method == 'POST':
        try:
            # Get form data
            name = request.POST.get('name')
            code = request.POST.get('code')

            # Validate that fields are not empty
            if not name or not code:
                messages.error(request, 'Both Subject Name and Subject Code are required!')
                return render(request, 'Academic/subject/edit_subject.html', {'subject': subject})

            # Check if subject code already exists (excluding current subject)
            if Subject.objects.filter(code=code).exclude(id=subject_id).exists():
                messages.error(request, f'Subject with code "{code}" already exists!')
                return render(request, 'Academic/subject/edit_subject.html', {'subject': subject})

            # Update Subject record
            subject.name = name
            subject.code = code
            subject.save()

            messages.success(request, f'Subject "{name}" updated successfully!')
            return redirect('subject_list')

        except Exception as e:
            messages.error(request, f'Error updating subject: {str(e)}')

    context = {
        'subject': subject
    }
    return render(request, 'Academic/subject/edit_subject.html', context)


def delete_subject(request, subject_id):
    try:
        subject = Subject.objects.get(id=subject_id)
        subject_name = subject.name
        subject.delete()
        messages.success(request, f'Subject "{subject_name}" deleted successfully!')
    except Subject.DoesNotExist:
        messages.error(request, 'Subject not found!')
    except Exception as e:
        messages.error(request, f'Error deleting subject: {str(e)}')

    return redirect('subject_list')


# ============================================================================
# SECTION VIEWS
# ============================================================================

def section_list(request):
    sections = Section.objects.all().order_by('-created_at')
    context = {
        'sections': sections
    }
    return render(request, 'Academic/section/section_list.html', context)


def section_detail(request, section_id):
    section = get_object_or_404(Section, id=section_id)
    context = {
        'section': section
    }
    return render(request, 'Academic/section/section_detail.html', context)


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


def edit_section(request, section_id):
    try:
        section = Section.objects.get(id=section_id)
    except Section.DoesNotExist:
        messages.error(request, 'Section not found!')
        return redirect('section_list')

    if request.method == 'POST':
        try:
            # Get form data
            name = request.POST.get('name')

            # Validate that field is not empty
            if not name:
                messages.error(request, 'Section name is required!')
                return render(request, 'Academic/section/edit_section.html', {'section': section})

            # Update Section record
            section.name = name
            section.save()

            messages.success(request, f'Section "{name}" updated successfully!')
            return redirect('section_list')

        except Exception as e:
            messages.error(request, f'Error updating section: {str(e)}')

    context = {
        'section': section
    }
    return render(request, 'Academic/section/edit_section.html', context)


def delete_section(request, section_id):
    try:
        section = Section.objects.get(id=section_id)
        section_name = section.name
        section.delete()
        messages.success(request, f'Section "{section_name}" deleted successfully!')
    except Section.DoesNotExist:
        messages.error(request, 'Section not found!')
    except Exception as e:
        messages.error(request, f'Error deleting section: {str(e)}')

    return redirect('section_list')


# ============================================================================
# SESSION VIEWS
# ============================================================================

def session_list(request):
    sessions = Session.objects.all().order_by('-created_at')
    context = {
        'sessions': sessions
    }
    return render(request, 'Academic/session/session_list.html', context)


def session_detail(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    context = {
        'session': session
    }
    return render(request, 'Academic/session/session_detail.html', context)


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


def edit_session(request, session_id):
    try:
        session = Session.objects.get(id=session_id)
    except Session.DoesNotExist:
        messages.error(request, 'Session not found!')
        return redirect('session_list')

    if request.method == 'POST':
        try:
            # Get form data
            name = request.POST.get('name')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')

            # Validate that fields are not empty
            if not name or not start_date or not end_date:
                messages.error(request, 'All fields are required!')
                return render(request, 'Academic/session/edit_session.html', {'session': session})

            # Check if session name already exists (excluding current session)
            if Session.objects.filter(name=name).exclude(id=session_id).exists():
                messages.error(request, f'Session "{name}" already exists!')
                return render(request, 'Academic/session/edit_session.html', {'session': session})

            # Validate that start_date is before end_date
            from datetime import datetime
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            if start >= end:
                messages.error(request, 'Start date must be before end date!')
                return render(request, 'Academic/session/edit_session.html', {'session': session})

            # Update Session record
            session.name = name
            session.start_date = start_date
            session.end_date = end_date
            session.save()

            messages.success(request, f'Academic Session "{name}" updated successfully!')
            return redirect('session_list')

        except Exception as e:
            messages.error(request, f'Error updating session: {str(e)}')

    context = {
        'session': session
    }
    return render(request, 'Academic/session/edit_session.html', context)


def delete_session(request, session_id):
    try:
        session = Session.objects.get(id=session_id)
        session_name = session.name
        session.delete()
        messages.success(request, f'Academic Session "{session_name}" deleted successfully!')
    except Session.DoesNotExist:
        messages.error(request, 'Session not found!')
    except Exception as e:
        messages.error(request, f'Error deleting session: {str(e)}')

    return redirect('session_list')


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
    classes = Class.objects.all().order_by('-created_at')
    context = {
        'classes': classes
    }
    return render(request, 'Academic/class/class_list.html', context)


def class_detail(request, class_id):
    class_obj = get_object_or_404(Class, id=class_id)
    context = {
        'klass': class_obj
    }
    return render(request, 'Academic/class/class_detail.html', context)


def edit_class(request, class_id):
    try:
        class_obj = Class.objects.get(id=class_id)
    except Class.DoesNotExist:
        messages.error(request, 'Class not found!')
        return redirect('class_list')

    if request.method == 'POST':
        try:
            # Get form data
            name = request.POST.get('name')
            class_code = request.POST.get('class_code')

            # Validate that fields are not empty
            if not name or not class_code:
                messages.error(request, 'Both Class Name and Class Code are required!')
                return render(request, 'Academic/class/edit_class.html', {'class': class_obj})

            # Validate class_code is a number between 1-99
            try:
                class_code_int = int(class_code)
                if class_code_int < 1 or class_code_int > 99:
                    messages.error(request, 'Class Code must be between 1 and 99!')
                    return render(request, 'Academic/class/edit_class.html', {'class': class_obj})
            except ValueError:
                messages.error(request, 'Class Code must be a valid number!')
                return render(request, 'Academic/class/edit_class.html', {'class': class_obj})

            # Check if class name already exists (excluding current class)
            if Class.objects.filter(name=name).exclude(id=class_id).exists():
                messages.error(request, f'Class with name "{name}" already exists!')
                return render(request, 'Academic/class/edit_class.html', {'class': class_obj})

            # Update Class record
            class_obj.name = name
            class_obj.class_code = class_code_int
            class_obj.save()

            messages.success(request, f'Class "{name}" updated successfully!')
            return redirect('class_list')

        except Exception as e:
            messages.error(request, f'Error updating class: {str(e)}')

    context = {
        'class': class_obj
    }
    return render(request, 'Academic/class/edit_class.html', context)


def delete_class(request, class_id):
    try:
        class_obj = Class.objects.get(id=class_id)
        class_name = class_obj.name
        class_obj.delete()
        messages.success(request, f'Class "{class_name}" deleted successfully!')
    except Class.DoesNotExist:
        messages.error(request, 'Class not found!')
    except Exception as e:
        messages.error(request, f'Error deleting class: {str(e)}')

    return redirect('class_list')
