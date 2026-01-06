import secrets
import string
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from account.models import User
from academic.models import Session, Class, Section
from django.db.models import Q
from teacher.models import AttendanceRecord, Assignment, AssignmentSubmission

from .models import StudentInfo, StudentNotification, StudentFeedback, StudentLeave, StudentResult
from .forms import StudentFeedbackForm, StudentLeaveForm, AssignmentSubmissionForm

# Helpers
def _parse_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


# Create your views here.
def student_list(request):

    students = StudentInfo.objects.all()

    context = {
        "students": students,
    }

    return render(request, "Student/student_list.html", context)


def student_detail(request, id):
    student = get_object_or_404(
        StudentInfo.objects.select_related('klass', 'session', 'section', 'user'),
        id=id
    )

    context = {
        "student": student,
    }
    return render(request, "Student/student_detail.html", context)


def student_create(request):
    # Get all classes, sessions, and sections for the dropdowns
    classes = Class.objects.all()
    sessions = Session.objects.all()
    sections = Section.objects.all()

    if request.method == 'POST':
        try:
            # Get form data
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            gender = request.POST.get('gender')
            date_of_birth = request.POST.get('date_of_birth') or None
            klass_id = request.POST.get('klass')
            session_id = request.POST.get('session')
            section_id = request.POST.get('section') or None
            religion = request.POST.get('religion') or None
            joining_date = request.POST.get('joining_date') or None
            phone = request.POST.get('phone') or None
            blood_group = request.POST.get('blood_group') or None

            # Parent information
            father_name = request.POST.get('father_name') or None
            father_occupation = request.POST.get('father_occupation') or None
            father_mobile = request.POST.get('father_mobile') or None
            father_email = request.POST.get('father_email') or None
            mother_name = request.POST.get('mother_name') or None
            mother_occupation = request.POST.get('mother_occupation') or None
            mother_mobile = request.POST.get('mother_mobile') or None
            mother_email = request.POST.get('mother_email') or None

            # Address
            present_address = request.POST.get('present_address') or None
            permanent_address = request.POST.get('permanent_address') or None

            # Profile picture
            profile_pic = request.FILES.get('profile_pic')

            # Auto-generate a secure password
            # Password will contain uppercase, lowercase, digits, and special characters
            alphabet = string.ascii_letters + string.digits + string.punctuation
            password = ''.join(secrets.choice(alphabet) for i in range(12))

            # Auto-generate username (student1, student2, student3, ...)
            last_student_user = User.objects.filter(
                user_type='Student',
                username__startswith='student'
            ).order_by('-id').first()

            if last_student_user and last_student_user.username.startswith('student'):
                # Extract the number from the last username
                try:
                    last_number = int(last_student_user.username.replace('student', ''))
                    username = f'student{last_number + 1}'
                except ValueError:
                    # If extraction fails, count all student users and add 1
                    count = User.objects.filter(user_type='Student').count()
                    username = f'student{count + 1}'
            else:
                # First student
                username = 'student1'

            # Create User account first
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,  # Password will be hashed by create_user
                first_name=first_name,
                last_name=last_name,
                user_type='Student',
                gender=gender,
                phone=phone,
            )

            # Get foreign key objects
            klass = Class.objects.get(id=klass_id)
            session = Session.objects.get(id=session_id)
            section = Section.objects.get(id=section_id) if section_id else None

            # Create StudentInfo record
            student = StudentInfo.objects.create(
                user=user,
                first_name=first_name,
                last_name=last_name,
                gender=gender,
                date_of_birth=date_of_birth,
                klass=klass,
                session=session,
                section=section,
                religion=religion,
                joining_date=joining_date,
                phone=phone,
                email=email,
                blood_group=blood_group,
                father_name=father_name,
                father_occupation=father_occupation,
                father_mobile=father_mobile,
                father_email=father_email,
                mother_name=mother_name,
                mother_occupation=mother_occupation,
                mother_mobile=mother_mobile,
                mother_email=mother_email,
                present_address=present_address,
                permanent_address=permanent_address,
                profile_pic=profile_pic,
            )

            messages.success(request, f'Student {first_name} {last_name} added successfully! Student ID: {student.student_user_id} | Username: {username} | Password: {password}')
            return redirect('student_list')

        except Class.DoesNotExist:
            messages.error(request, 'Invalid Class ID. Please enter a valid class ID.')
        except Session.DoesNotExist:
            messages.error(request, 'Invalid Session ID. Please enter a valid session ID.')
        except Section.DoesNotExist:
            messages.error(request, 'Invalid Section ID. Please enter a valid section ID.')
        except Exception as e:
            messages.error(request, f'Error creating student: {str(e)}')

    context = {
        'classes': classes,
        'sessions': sessions,
        'sections': sections,
    }
    return render(request, 'Student/add_student.html', context)


@login_required
def student_dashboard(request):

    return render(request, 'Student/student_dashboard.html')


@login_required
def student_attendance(request):
    if request.user.user_type != 'Student':
        return HttpResponseForbidden('Only students can view this page.')

    student = get_object_or_404(StudentInfo, user=request.user)

    base_records = AttendanceRecord.objects.filter(student=student)
    subject_choices = base_records.filter(
        attendance__subject__isnull=False
    ).values_list('attendance__subject_id', 'attendance__subject__name').distinct()
    subject_options = sorted(
        [
            {'id': subject_id, 'name': subject_name}
            for subject_id, subject_name in subject_choices
            if subject_id is not None
        ],
        key=lambda item: item['name'] or ''
    )

    records = base_records.select_related(
        'attendance__teacher',
        'attendance__klass',
        'attendance__section',
        'attendance__session',
        'attendance__subject',
    )

    start_date_value = request.GET.get('start_date', '')
    end_date_value = request.GET.get('end_date', '')
    subject_value = request.GET.get('subject', '')
    status_value = request.GET.get('status', '')

    def _parse_date(value):
        try:
            return datetime.strptime(value, '%Y-%m-%d').date()
        except (TypeError, ValueError):
            return None

    start_date_obj = _parse_date(start_date_value) if start_date_value else None
    if start_date_value and not start_date_obj:
        messages.error(request, 'Invalid start date. Ignoring this filter.')
        start_date_value = ''
    if start_date_obj:
        records = records.filter(attendance__date__gte=start_date_obj)

    end_date_obj = _parse_date(end_date_value) if end_date_value else None
    if end_date_value and not end_date_obj:
        messages.error(request, 'Invalid end date. Ignoring this filter.')
        end_date_value = ''
    if end_date_obj:
        records = records.filter(attendance__date__lte=end_date_obj)

    subject_id = None
    if subject_value:
        try:
            subject_id = int(subject_value)
        except (TypeError, ValueError):
            messages.error(request, 'Invalid subject filter. Showing all subjects.')
            subject_value = ''
        else:
            records = records.filter(attendance__subject_id=subject_id)

    valid_statuses = {choice[0] for choice in AttendanceRecord.STATUS_CHOICES}
    if status_value and status_value not in valid_statuses:
        messages.error(request, 'Invalid status filter. Showing all records.')
        status_value = ''
    elif status_value:
        records = records.filter(status=status_value)

    record_list = list(records.order_by('-attendance__date', '-attendance__created_at'))

    total_classes = len(record_list)
    present_count = sum(1 for rec in record_list if rec.status == AttendanceRecord.STATUS_PRESENT)
    absent_count = sum(1 for rec in record_list if rec.status == AttendanceRecord.STATUS_ABSENT)
    attendance_percentage = round((present_count / total_classes) * 100, 2) if total_classes else 0.0

    context = {
        'student': student,
        'records': record_list,
        'summary': {
            'total': total_classes,
            'present': present_count,
            'absent': absent_count,
            'percentage': attendance_percentage,
        },
        'filters': {
            'start_date': start_date_value,
            'end_date': end_date_value,
            'subject': subject_value,
            'status': status_value,
        },
        'subject_options': subject_options,
        'status_choices': AttendanceRecord.STATUS_CHOICES,
    }
    return render(request, 'Student/attendance.html', context)


@login_required
def student_results(request):
    if request.user.user_type != 'Student':
        return HttpResponseForbidden('Only students can view this page.')

    student = get_object_or_404(StudentInfo, user=request.user)

    base_qs = StudentResult.objects.filter(student=student).select_related(
        'subject', 'session', 'klass', 'section'
    ).order_by('-recorded_at', '-id')

    session_options = (
        base_qs.filter(session__isnull=False)
        .values_list('session_id', 'session__name')
        .distinct()
    )
    subject_options = (
        base_qs.filter(subject__isnull=False)
        .values_list('subject_id', 'subject__name')
        .distinct()
    )

    filters = {
        'session': request.GET.get('session') or '',
        'subject': request.GET.get('subject') or '',
        'exam_type': request.GET.get('exam_type') or '',
    }

    results = base_qs

    session_id = _parse_int(filters['session'])
    if filters['session'] and session_id is None:
        messages.error(request, 'Invalid session filter ignored.')
        filters['session'] = ''
    elif session_id:
        results = results.filter(session_id=session_id)

    subject_id = _parse_int(filters['subject'])
    if filters['subject'] and subject_id is None:
        messages.error(request, 'Invalid subject filter ignored.')
        filters['subject'] = ''
    elif subject_id:
        results = results.filter(subject_id=subject_id)

    valid_exam_types = {choice[0] for choice in StudentResult.EXAM_TYPES}
    if filters['exam_type'] and filters['exam_type'] not in valid_exam_types:
        messages.error(request, 'Invalid exam type filter ignored.')
        filters['exam_type'] = ''
    elif filters['exam_type']:
        results = results.filter(exam_type=filters['exam_type'])

    result_list = list(results)
    percentages = [res.percentage() for res in result_list if res.percentage() is not None]
    avg_percentage = round(sum(percentages) / len(percentages), 2) if percentages else None

    context = {
        'student': student,
        'results': result_list,
        'filters': filters,
        'session_options': sorted(session_options, key=lambda item: item[1]),
        'subject_options': sorted(subject_options, key=lambda item: item[1]),
        'exam_type_options': StudentResult.EXAM_TYPES,
        'summary': {
            'total': len(result_list),
            'average_percentage': avg_percentage,
        },
    }
    return render(request, 'Student/view_results.html', context)


@login_required
def student_assignments(request):
    if request.user.user_type != 'Student':
        return HttpResponseForbidden('Only students can access assignments.')

    student = get_object_or_404(StudentInfo, user=request.user)

    base_assignments = Assignment.objects.select_related(
        'teacher', 'klass', 'section', 'session', 'subject'
    )

    if student.klass:
        base_assignments = base_assignments.filter(klass=student.klass)
    if student.session:
        base_assignments = base_assignments.filter(Q(session__isnull=True) | Q(session=student.session))
    if student.section:
        base_assignments = base_assignments.filter(Q(section__isnull=True) | Q(section=student.section))

    base_assignments = base_assignments.order_by('-created_at')

    assignment_ids = list(base_assignments.values_list('id', flat=True))
    submissions = AssignmentSubmission.objects.filter(student=student, assignment_id__in=assignment_ids)
    submission_map = {submission.assignment_id: submission for submission in submissions}

    inline_forms = {}
    if request.method == 'POST':
        assignment_id = _parse_int(request.POST.get('assignment_id'))
        if assignment_id and assignment_id in assignment_ids:
            assignment = next((a for a in base_assignments if a.id == assignment_id), None)
            if assignment:
                submission_instance = submission_map.get(assignment_id)
                form = AssignmentSubmissionForm(request.POST, request.FILES, instance=submission_instance)
                if form.is_valid():
                    submission = form.save(commit=False)
                    submission.assignment_id = assignment_id
                    submission.student = student
                    submission.save()
                    messages.success(request, 'Assignment submitted successfully.')
                    return redirect('student_assignments')
                else:
                    inline_forms[assignment_id] = form
        else:
            messages.error(request, 'Invalid assignment selected for submission.')

    assignment_list = []
    for assignment in base_assignments:
        assignment.user_submission = submission_map.get(assignment.id)
        assignment.inline_form = inline_forms.get(
            assignment.id,
            AssignmentSubmissionForm(instance=assignment.user_submission)
        )
        assignment_list.append(assignment)

    context = {
        'student': student,
        'assignments': assignment_list,
    }
    return render(request, 'Student/assignments.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def submit_assignment(request, pk):
    if request.user.user_type != 'Student':
        return HttpResponseForbidden('Only students can submit assignments.')

    student = get_object_or_404(StudentInfo, user=request.user)
    assignment = get_object_or_404(
        Assignment.objects.select_related('teacher', 'klass', 'section', 'session', 'subject'),
        pk=pk,
    )

    if assignment.klass and student.klass_id != assignment.klass_id:
        return HttpResponseForbidden('You are not allowed to submit this assignment.')
    if assignment.section and student.section_id != assignment.section_id:
        return HttpResponseForbidden('You are not allowed to submit this assignment.')

    submission = AssignmentSubmission.objects.filter(
        assignment=assignment,
        student=student,
    ).first()

    form = AssignmentSubmissionForm(request.POST or None, request.FILES or None, instance=submission)

    if request.method == 'POST' and form.is_valid():
        submission_obj = form.save(commit=False)
        submission_obj.assignment = assignment
        submission_obj.student = student
        submission_obj.save()
        messages.success(request, 'Assignment submitted successfully.')
        return redirect('student_assignments')

    context = {
        'assignment': assignment,
        'form': form,
        'submission': submission,
    }
    return render(request, 'Student/submit_assignment.html', context)


def student_edit(request, id):
    # Get the student instance or return 404
    student = StudentInfo.objects.select_related('user', 'klass', 'session', 'section').get(id=id)

    # Get all classes, sessions, and sections for the dropdowns
    classes = Class.objects.all()
    sessions = Session.objects.all()
    sections = Section.objects.all()

    if request.method == 'POST':
        try:
            # Get form data
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            gender = request.POST.get('gender')
            date_of_birth = request.POST.get('date_of_birth') or None
            klass_id = request.POST.get('klass')
            session_id = request.POST.get('session')
            section_id = request.POST.get('section') or None
            religion = request.POST.get('religion') or None
            joining_date = request.POST.get('joining_date') or None
            phone = request.POST.get('phone') or None
            blood_group = request.POST.get('blood_group') or None

            # Parent information
            father_name = request.POST.get('father_name') or None
            father_occupation = request.POST.get('father_occupation') or None
            father_mobile = request.POST.get('father_mobile') or None
            father_email = request.POST.get('father_email') or None
            mother_name = request.POST.get('mother_name') or None
            mother_occupation = request.POST.get('mother_occupation') or None
            mother_mobile = request.POST.get('mother_mobile') or None
            mother_email = request.POST.get('mother_email') or None

            # Address
            present_address = request.POST.get('present_address') or None
            permanent_address = request.POST.get('permanent_address') or None

            # Profile picture
            profile_pic = request.FILES.get('profile_pic')

            # Update User account
            student.user.first_name = first_name
            student.user.last_name = last_name
            student.user.email = email
            student.user.gender = gender
            student.user.phone = phone
            student.user.save()

            # Get foreign key objects
            klass = Class.objects.get(id=klass_id)
            session = Session.objects.get(id=session_id)
            section = Section.objects.get(id=section_id) if section_id else None

            # Update StudentInfo record
            student.first_name = first_name
            student.last_name = last_name
            student.gender = gender
            student.date_of_birth = date_of_birth
            student.klass = klass
            student.session = session
            student.section = section
            student.religion = religion
            student.joining_date = joining_date
            student.phone = phone
            student.email = email
            student.blood_group = blood_group
            student.father_name = father_name
            student.father_occupation = father_occupation
            student.father_mobile = father_mobile
            student.father_email = father_email
            student.mother_name = mother_name
            student.mother_occupation = mother_occupation
            student.mother_mobile = mother_mobile
            student.mother_email = mother_email
            student.present_address = present_address
            student.permanent_address = permanent_address

            # Update profile picture only if a new one is uploaded
            if profile_pic:
                student.profile_pic = profile_pic

            student.save()

            messages.success(request, f'Student {first_name} {last_name} updated successfully!')
            return redirect('student_list')

        except Class.DoesNotExist:
            messages.error(request, 'Invalid Class ID. Please select a valid class.')
        except Session.DoesNotExist:
            messages.error(request, 'Invalid Session ID. Please select a valid session.')
        except Section.DoesNotExist:
            messages.error(request, 'Invalid Section ID. Please select a valid section.')
        except Exception as e:
            messages.error(request, f'Error updating student: {str(e)}')

    context = {
        'student': student,
        'classes': classes,
        'sessions': sessions,
        'sections': sections,
    }
    return render(request, 'Student/edit_student.html', context)


def student_delete(request, id):
    try:
        student = StudentInfo.objects.select_related('user').get(id=id)
        student_name = f"{student.first_name} {student.last_name}"

        # Delete the associated user account as well
        user = student.user
        student.delete()
        user.delete()

        messages.success(request, f'Student {student_name} has been deleted successfully!')
    except StudentInfo.DoesNotExist:
        messages.error(request, 'Student not found.')
    except Exception as e:
        messages.error(request, f'Error deleting student: {str(e)}')

    return redirect('student_list')


@login_required
def student_notification(request):
    if request.user.user_type != 'Student':
        return HttpResponseForbidden('Only students can view notifications.')

    student = get_object_or_404(StudentInfo, user=request.user)
    notifications = StudentNotification.objects.filter(student=student).order_by('-created_at')

    return render(request, 'Student/notifications.html', {
        'notifications': notifications,
    })


@login_required
def student_feedback(request):
    if request.user.user_type != 'Student':
        return HttpResponseForbidden('Only students can access feedback.')

    student = get_object_or_404(StudentInfo, user=request.user)
    feedback_entries = StudentFeedback.objects.filter(student=student)

    if request.method == 'POST':
        form = StudentFeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.student = student
            feedback.save()
            messages.success(request, 'Feedback submitted successfully.')
            return redirect('student_feedback')
    else:
        form = StudentFeedbackForm()

    return render(request, 'Student/feedback.html', {
        'form': form,
        'feedback_entries': feedback_entries,
    })


@login_required
def student_apply_leave(request):
    if request.user.user_type != 'Student':
        return HttpResponseForbidden('Only students can apply for leave.')

    student = get_object_or_404(StudentInfo, user=request.user)
    leaves = StudentLeave.objects.filter(student=student).order_by('-created_at')

    if request.method == 'POST':
        form = StudentLeaveForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.student = student
            leave.save()
            messages.success(request, 'Leave request submitted successfully.')
            return redirect('student_apply_leave')
    else:
        form = StudentLeaveForm()

    return render(request, 'Student/apply_leave.html', {
        'form': form,
        'leaves': leaves,
    })
