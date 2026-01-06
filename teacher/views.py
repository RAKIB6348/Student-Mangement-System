from datetime import datetime, date
from urllib.parse import urlencode

import secrets
import string

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction, IntegrityError
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from account.models import User
from academic.models import Class, Section, Session, Subject
from decimal import Decimal, InvalidOperation

from student.models import StudentInfo, StudentResult

from .forms import TeacherFeedbackForm, TeacherLeaveForm, StudentResultForm, TeacherAssignmentForm
from .models import (
    Attendance,
    AttendanceRecord,
    Feedback,
    TeacherInfo,
    TeacherLeave,
    TeacherNotification,
    Assignment,
    AssignmentSubmission,
)


def _parse_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


# Create your views here.
def teacher_list(request):
    teachers = TeacherInfo.objects.all()

    context = {
        "teachers": teachers,
    }

    return render(request, 'Teacher/teacher_list.html', context)


def teacher_detail(request, id):
    teacher = get_object_or_404(
        TeacherInfo.objects.select_related('user'),
        id=id
    )

    context = {
        "teacher": teacher,
    }
    return render(request, 'Teacher/teacher_detail.html', context)



def add_teacher(request):
    if request.method == 'POST':
        try:
            # Get form data - Account Info
            email = request.POST.get('email')

            # Get form data - Personal Info
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            gender = request.POST.get('gender')
            date_of_birth = request.POST.get('date_of_birth') or None
            phone = request.POST.get('phone') or None
            profile_pic = request.FILES.get('profile_pic')

            # Get form data - Job Info
            designation = request.POST.get('designation') or None
            joining_date = request.POST.get('joining_date') or None
            qualification = request.POST.get('qualification') or None
            experience = request.POST.get('experience') or None

            # Get form data - Address Info
            present_address = request.POST.get('present_address') or None
            permanent_address = request.POST.get('permanent_address') or None

            # Check if email already exists
            if User.objects.filter(email=email).exists():
                messages.error(request, f'Email "{email}" already exists!')
                return render(request, 'Teacher/add_teacher.html')

            # Auto-generate a secure password
            alphabet = string.ascii_letters + string.digits + string.punctuation
            password = ''.join(secrets.choice(alphabet) for i in range(12))

            # Auto-generate username (teacher1, teacher2, teacher3, ...)
            last_teacher_user = User.objects.filter(
                user_type='Teacher',
                username__startswith='teacher'
            ).order_by('-id').first()

            if last_teacher_user and last_teacher_user.username.startswith('teacher'):
                # Extract the number from the last username
                try:
                    last_number = int(last_teacher_user.username.replace('teacher', ''))
                    username = f'teacher{last_number + 1}'
                except ValueError:
                    # If extraction fails, count all teacher users and add 1
                    count = User.objects.filter(user_type='Teacher').count()
                    username = f'teacher{count + 1}'
            else:
                # First teacher
                username = 'teacher1'

            # Create User account first
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type='Teacher',
                gender=gender,
                phone=phone,
                profile_pic=profile_pic,
            )

            # Create TeacherInfo record
            teacher = TeacherInfo.objects.create(
                user=user,
                first_name=first_name,
                last_name=last_name,
                gender=gender,
                date_of_birth=date_of_birth,
                phone=phone,
                email=email,
                designation=designation,
                joining_date=joining_date,
                qualification=qualification,
                experience=experience,
                present_address=present_address,
                permanent_address=permanent_address,
                profile_pic=profile_pic,
            )

            messages.success(request, f'Teacher {first_name} {last_name} added successfully! Teacher ID: {teacher.teacher_user_id} | Username: {username} | Password: {password}')
            return redirect('teacher_list')

        except Exception as e:
            messages.error(request, f'Error creating teacher: {str(e)}')

    return render(request, 'Teacher/add_teacher.html')


@login_required
def teacher_dashboard(request):

    return render(request, "Teacher/home.html")


@login_required
@require_http_methods(["GET", "POST"])
def take_attendance(request):
    if request.user.user_type != 'Teacher':
        return HttpResponseForbidden('Only teachers can take attendance.')

    teacher = get_object_or_404(TeacherInfo, user=request.user)
    classes = Class.objects.all().order_by('class_code')
    sections = Section.objects.all().order_by('name')
    sessions = Session.objects.all().order_by('-start_date')
    subjects = Subject.objects.all().order_by('name')

    selected_class_id = _parse_int(request.GET.get('klass') or request.POST.get('klass'))
    selected_section_id = _parse_int(request.GET.get('section') or request.POST.get('section'))
    selected_session_id = _parse_int(request.GET.get('session') or request.POST.get('session'))
    selected_subject_id = _parse_int(request.GET.get('subject') or request.POST.get('subject'))
    selected_date = request.GET.get('date') or request.POST.get('attendance_date') or date.today().isoformat()

    try:
        selected_date_obj = datetime.strptime(selected_date, "%Y-%m-%d").date()
    except ValueError:
        selected_date_obj = date.today()
        selected_date = selected_date_obj.isoformat()
        messages.error(request, "Invalid date provided. Using today's date instead.")

    filter_ready = bool(selected_class_id and selected_session_id and selected_subject_id)

    students = []
    existing_attendance = None
    attendance_note = ''
    filter_submitted = False
    valid_statuses = {choice[0] for choice in AttendanceRecord.STATUS_CHOICES}

    def _student_queryset():
        qs = StudentInfo.objects.filter(
            klass_id=selected_class_id,
            session_id=selected_session_id,
        )
        if selected_section_id:
            qs = qs.filter(section_id=selected_section_id)
        return qs.select_related('klass', 'section').order_by('roll_no', 'first_name', 'last_name')

    if request.method == 'POST':
        if not filter_ready:
            messages.error(request, 'Class, Session, and Subject are required before submitting attendance.')
        else:
            students_qs = _student_queryset()
            student_list = list(students_qs)
            if not student_list:
                messages.warning(request, 'No students found for the selected filters.')
            else:
                note_value = request.POST.get('note', '').strip() or None
                attendance, _ = Attendance.objects.get_or_create(
                    teacher=teacher,
                    klass_id=selected_class_id,
                    session_id=selected_session_id,
                    section_id=selected_section_id,
                    subject_id=selected_subject_id,
                    date=selected_date_obj,
                )
                if attendance.note != note_value:
                    attendance.note = note_value
                    attendance.save(update_fields=['note', 'updated_at'])

                records = []
                for student in student_list:
                    status = request.POST.get(f'status_{student.id}', AttendanceRecord.STATUS_PRESENT)
                    if status not in valid_statuses:
                        status = AttendanceRecord.STATUS_PRESENT
                    remark = request.POST.get(f'remark_{student.id}', '').strip() or None
                    records.append(AttendanceRecord(
                        attendance=attendance,
                        student=student,
                        status=status,
                        remark=remark,
                    ))

                with transaction.atomic():
                    AttendanceRecord.objects.filter(attendance=attendance).delete()
                    AttendanceRecord.objects.bulk_create(records)

                messages.success(
                    request,
                    f"Attendance saved for {selected_date_obj.strftime('%d %b %Y')}."
                )

                query_params = {
                    'klass': selected_class_id,
                    'session': selected_session_id,
                    'subject': selected_subject_id,
                    'date': selected_date_obj.strftime('%Y-%m-%d'),
                }
                if selected_section_id:
                    query_params['section'] = selected_section_id
                return redirect(f"{reverse('take_attendance')}?{urlencode(query_params)}")

        # Preserve selections and entered data when errors occur.
        if filter_ready:
            students_qs = _student_queryset()
            students = list(students_qs)
            status_map = {
                student.id: request.POST.get(f'status_{student.id}', AttendanceRecord.STATUS_PRESENT)
                for student in students
            }
            remark_map = {
                student.id: request.POST.get(f'remark_{student.id}', '')
                for student in students
            }
            for student in students:
                student.current_status = status_map.get(student.id, AttendanceRecord.STATUS_PRESENT)
                student.current_remark = remark_map.get(student.id, '')
            attendance_note = request.POST.get('note', '').strip()
            filter_submitted = True

    else:  # GET
        if filter_ready:
            students_qs = _student_queryset()
            students = list(students_qs)
            existing_attendance = Attendance.objects.filter(
                teacher=teacher,
                klass_id=selected_class_id,
                session_id=selected_session_id,
                section_id=selected_section_id,
                subject_id=selected_subject_id,
                date=selected_date_obj,
            ).prefetch_related('records__student').first()

            if existing_attendance:
                status_map = {
                    record.student_id: record.status
                    if record.status in valid_statuses else AttendanceRecord.STATUS_PRESENT
                    for record in existing_attendance.records.all()
                }
                remark_map = {
                    record.student_id: record.remark or ''
                    for record in existing_attendance.records.all()
                }
                attendance_note = existing_attendance.note or ''
            else:
                status_map = {}
                remark_map = {}

            for student in students:
                student.current_status = status_map.get(student.id, AttendanceRecord.STATUS_PRESENT)
                student.current_remark = remark_map.get(student.id, '')
            filter_submitted = True

    selected_class = Class.objects.filter(id=selected_class_id).first() if selected_class_id else None
    selected_section = Section.objects.filter(id=selected_section_id).first() if selected_section_id else None
    selected_session = Session.objects.filter(id=selected_session_id).first() if selected_session_id else None
    selected_subject = Subject.objects.filter(id=selected_subject_id).first() if selected_subject_id else None

    context = {
        'classes': classes,
        'sections': sections,
        'sessions': sessions,
        'subjects': subjects,
        'students': students,
        'selected_class_id': selected_class_id,
        'selected_section_id': selected_section_id,
        'selected_session_id': selected_session_id,
        'selected_subject_id': selected_subject_id,
        'selected_date': selected_date,
        'attendance_note': attendance_note,
        'filter_submitted': filter_submitted,
        'selected_class': selected_class,
        'selected_section': selected_section,
        'selected_session': selected_session,
        'selected_subject': selected_subject,
        'status_choices': AttendanceRecord.STATUS_CHOICES,
    }
    return render(request, 'Teacher/take_attendance.html', context)


@login_required
def view_update_attendance(request):
    if request.user.user_type != 'Teacher':
        return HttpResponseForbidden('Only teachers can view attendance history.')

    teacher = get_object_or_404(TeacherInfo, user=request.user)
    classes = Class.objects.all().order_by('class_code')
    sessions = Session.objects.all().order_by('-start_date')
    subjects = Subject.objects.all().order_by('name')

    selected_class_id = _parse_int(request.GET.get('class'))
    selected_session_id = _parse_int(request.GET.get('session'))
    selected_subject_id = _parse_int(request.GET.get('subject'))
    selected_date = request.GET.get('date')

    attendances = (
        Attendance.objects.filter(teacher=teacher)
        .select_related('klass', 'section', 'session')
        .prefetch_related('records')
        .order_by('-date', '-created_at')
    )

    if selected_class_id:
        attendances = attendances.filter(klass_id=selected_class_id)
    if selected_session_id:
        attendances = attendances.filter(session_id=selected_session_id)
    if selected_subject_id:
        attendances = attendances.filter(subject_id=selected_subject_id)
    if selected_date:
        try:
            filter_date = datetime.strptime(selected_date, "%Y-%m-%d").date()
            attendances = attendances.filter(date=filter_date)
        except ValueError:
            messages.error(request, 'Invalid date filter. Showing all records.')
            selected_date = None

    attendance_list = list(attendances)
    for attendance in attendance_list:
        records = list(attendance.records.all())
        attendance.summary_total = len(records)
        attendance.summary_present = sum(1 for record in records if record.status == AttendanceRecord.STATUS_PRESENT)
        attendance.summary_absent = sum(1 for record in records if record.status == AttendanceRecord.STATUS_ABSENT)

    context = {
        'classes': classes,
        'sessions': sessions,
        'subjects': subjects,
        'attendances': attendance_list,
        'selected_class_id': selected_class_id,
        'selected_session_id': selected_session_id,
        'selected_subject_id': selected_subject_id,
        'selected_date': selected_date,
    }
    return render(request, 'Teacher/view_attendance.html', context)


def teacher_edit(request, id):
    # Get the teacher instance or return 404
    teacher = TeacherInfo.objects.select_related('user').get(id=id)

    if request.method == 'POST':
        try:
            # Get form data - Account Info
            email = request.POST.get('email')

            # Get form data - Personal Info
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            gender = request.POST.get('gender')
            date_of_birth = request.POST.get('date_of_birth') or None
            phone = request.POST.get('phone') or None
            profile_pic = request.FILES.get('profile_pic')

            # Get form data - Job Info
            designation = request.POST.get('designation') or None
            joining_date = request.POST.get('joining_date') or None
            qualification = request.POST.get('qualification') or None
            experience = request.POST.get('experience') or None

            # Get form data - Address Info
            present_address = request.POST.get('present_address') or None
            permanent_address = request.POST.get('permanent_address') or None

            # Update User account
            teacher.user.first_name = first_name
            teacher.user.last_name = last_name
            teacher.user.email = email
            teacher.user.gender = gender
            teacher.user.phone = phone

            # Update profile picture in User model only if new one is uploaded
            if profile_pic:
                teacher.user.profile_pic = profile_pic

            teacher.user.save()

            # Update TeacherInfo record
            teacher.first_name = first_name
            teacher.last_name = last_name
            teacher.gender = gender
            teacher.date_of_birth = date_of_birth
            teacher.phone = phone
            teacher.email = email
            teacher.designation = designation
            teacher.joining_date = joining_date
            teacher.qualification = qualification
            teacher.experience = experience
            teacher.present_address = present_address
            teacher.permanent_address = permanent_address

            # Update profile picture in TeacherInfo model only if new one is uploaded
            if profile_pic:
                teacher.profile_pic = profile_pic

            teacher.save()

            messages.success(request, f'Teacher {first_name} {last_name} updated successfully!')
            return redirect('teacher_list')

        except Exception as e:
            messages.error(request, f'Error updating teacher: {str(e)}')

    context = {
        'teacher': teacher,
    }
    return render(request, 'Teacher/edit_teacher.html', context)


def teacher_delete(request, id):
    try:
        teacher = TeacherInfo.objects.select_related('user').get(id=id)
        teacher_name = f"{teacher.first_name} {teacher.last_name}"

        # Delete the associated user account as well
        user = teacher.user
        teacher.delete()
        user.delete()

        messages.success(request, f'Teacher {teacher_name} has been deleted successfully!')
    except TeacherInfo.DoesNotExist:
        messages.error(request, 'Teacher not found.')
    except Exception as e:
        messages.error(request, f'Error deleting teacher: {str(e)}')

    return redirect('teacher_list')




@login_required
def teacher_notification(request):
    teacher = get_object_or_404(TeacherInfo, user=request.user)
    notifications = TeacherNotification.objects.filter(
        teacher_id=teacher
    ).order_by('-created_at')

    return render(request, 'Teacher/notifications.html', {
        'notifications': notifications
    })


@login_required
@require_http_methods(["GET", "POST"])
def apply_leave(request):
    teacher = get_object_or_404(TeacherInfo, user=request.user)
    leaves = TeacherLeave.objects.filter(
        teacher=teacher
    ).order_by('-created_at')

    if request.method == 'POST':
        form = TeacherLeaveForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.teacher = teacher
            leave.save()
            messages.success(request, 'Leave request submitted successfully.')
            return redirect('apply_leave')
    else:
        form = TeacherLeaveForm()

    return render(request, 'Teacher/apply_leave.html', {
        'form': form,
        'leaves': leaves,
    })



# ======================== feedback ========================


@login_required
@require_http_methods(["GET", "POST"])
def teacher_feedback(request):
    if request.user.user_type != 'Teacher':
        return HttpResponseForbidden('Only teachers can access feedback.')

    teacher = get_object_or_404(TeacherInfo, user=request.user)
    feedback_entries = Feedback.objects.filter(teacher=teacher)

    if request.method == 'POST':
        form = TeacherFeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.teacher = teacher
            feedback.save()
            messages.success(request, 'Feedback submitted successfully.')
            return redirect('teacher_feedback')
    else:
        form = TeacherFeedbackForm()

    return render(request, 'Teacher/feedback.html', {
        'form': form,
        'feedback_entries': feedback_entries,
    })


@login_required
@require_http_methods(["GET", "POST"])
def add_result(request):
    if request.user.user_type != 'Teacher':
        return HttpResponseForbidden('Only teachers can add results.')

    teacher = get_object_or_404(TeacherInfo, user=request.user)
    classes = Class.objects.all().order_by('class_code')
    sections = Section.objects.all().order_by('name')
    sessions = Session.objects.all().order_by('-start_date')
    subjects = Subject.objects.all().order_by('name')
    exam_type_choices = StudentResult.EXAM_TYPES
    recent_results = (
        StudentResult.objects.select_related('student', 'subject', 'session')
        .order_by('-recorded_at')[:10]
    )

    selected_class_id = _parse_int(request.GET.get('klass') or request.POST.get('klass'))
    selected_section_id = _parse_int(request.GET.get('section') or request.POST.get('section'))
    selected_session_id = _parse_int(request.GET.get('session') or request.POST.get('session'))
    selected_subject_id = _parse_int(request.GET.get('subject') or request.POST.get('subject'))
    selected_exam_type = request.GET.get('exam_type') or request.POST.get('exam_type') or ''
    total_marks_value = request.POST.get('total_marks') if request.method == 'POST' else ''

    selected_class = Class.objects.filter(id=selected_class_id).first() if selected_class_id else None
    selected_section = Section.objects.filter(id=selected_section_id).first() if selected_section_id else None
    selected_session = Session.objects.filter(id=selected_session_id).first() if selected_session_id else None
    selected_subject = Subject.objects.filter(id=selected_subject_id).first() if selected_subject_id else None

    filter_submitted = bool(selected_class_id or selected_session_id or selected_section_id)

    students = []
    if selected_class_id and selected_session_id:
        students_qs = StudentInfo.objects.filter(
            klass_id=selected_class_id,
            session_id=selected_session_id,
        )
        if selected_section_id:
            students_qs = students_qs.filter(section_id=selected_section_id)
        students = list(
            students_qs.select_related('klass', 'section', 'session').order_by(
                'roll_no', 'first_name', 'last_name'
            )
        )

    existing_results_map = {}
    if selected_subject_id and selected_session_id and selected_exam_type:
        existing_qs = StudentResult.objects.filter(
            student__in=students,
            subject_id=selected_subject_id,
            session_id=selected_session_id,
            exam_type=selected_exam_type,
        )
        existing_results_map = {result.student_id: result for result in existing_qs}
        if not total_marks_value and existing_results_map:
            sample = next(iter(existing_results_map.values()))
            total_marks_value = sample.total_marks

    student_errors = {}
    saved_count = 0

    if isinstance(total_marks_value, Decimal):
        total_marks_value = format(total_marks_value.normalize(), 'f').rstrip('0').rstrip('.') or '0'

    if request.method == 'POST':
        if not (selected_class_id and selected_session_id):
            messages.error(request, 'Please select Class and Session before submitting marks.')
        elif not selected_subject:
            messages.error(request, 'Subject is required.')
        elif not selected_exam_type or selected_exam_type not in {choice[0] for choice in exam_type_choices}:
            messages.error(request, 'Please choose a valid exam type.')
        elif not students:
            messages.warning(request, 'No students found for the selected filters.')
        else:
            try:
                total_marks_decimal = Decimal(str(total_marks_value))
            except (InvalidOperation, TypeError):
                messages.error(request, 'Enter a valid Total Marks value.')
            else:
                if total_marks_decimal <= 0:
                    messages.error(request, 'Total Marks must be greater than zero.')
                else:
                    for student in students:
                        raw_marks = request.POST.get(f'marks_{student.id}', '').strip()
                        grade_value = request.POST.get(f'grade_{student.id}', '').strip() or None
                        remark_value = request.POST.get(f'remark_{student.id}', '').strip() or None

                        if raw_marks == '':
                            continue

                        try:
                            obtained_decimal = Decimal(raw_marks)
                        except (InvalidOperation, TypeError):
                            student_errors[student.id] = 'Enter a valid number.'
                            continue

                        if obtained_decimal < 0 or obtained_decimal > total_marks_decimal:
                            student_errors[student.id] = 'Must be between 0 and total marks.'
                            continue

                        result, created = StudentResult.objects.update_or_create(
                            student=student,
                            subject=selected_subject,
                            session=selected_session,
                            exam_type=selected_exam_type,
                            defaults={
                                'klass': selected_class,
                                'section': selected_section,
                                'total_marks': total_marks_decimal,
                                'obtained_marks': obtained_decimal,
                                'grade': grade_value,
                                'remarks': remark_value,
                            },
                        )
                        saved_count += 1
                        existing_results_map[student.id] = result

                    if saved_count:
                        messages.success(
                            request,
                            f"Results saved for {saved_count} student{'s' if saved_count != 1 else ''}.",
                        )
                        query_params = {
                            'klass': selected_class_id,
                            'session': selected_session_id,
                        }
                        if selected_section_id:
                            query_params['section'] = selected_section_id
                        if selected_subject_id:
                            query_params['subject'] = selected_subject_id
                        if selected_exam_type:
                            query_params['exam_type'] = selected_exam_type
                        return redirect(f"{reverse('add_result')}?{urlencode(query_params)}")

    for student in students:
        existing = existing_results_map.get(student.id)
        if request.method == 'POST':
            marks_value = request.POST.get(f'marks_{student.id}', '')
            grade_value = request.POST.get(f'grade_{student.id}', '')
            remark_value = request.POST.get(f'remark_{student.id}', '')
        else:
            marks_value = existing.obtained_marks if existing else ''
            grade_value = existing.grade if existing else ''
            remark_value = existing.remarks if existing else ''

        if isinstance(marks_value, Decimal):
            marks_value = format(marks_value.normalize(), 'f').rstrip('0').rstrip('.') or '0'

        student.current_marks = marks_value
        student.current_grade = grade_value or ''
        student.current_remark = remark_value or ''
        student.error_message = student_errors.get(student.id)
        student.previous_marks = existing.obtained_marks if existing else None
        student.previous_grade = existing.grade if existing else None
        student.previous_timestamp = existing.recorded_at if existing else None

    context = {
        'teacher': teacher,
        'classes': classes,
        'sections': sections,
        'sessions': sessions,
        'subjects': subjects,
        'exam_type_choices': exam_type_choices,
        'selected_class_id': selected_class_id,
        'selected_section_id': selected_section_id,
        'selected_session_id': selected_session_id,
        'selected_subject_id': selected_subject_id,
        'selected_exam_type': selected_exam_type,
        'total_marks_value': total_marks_value,
        'students': students,
        'filter_submitted': filter_submitted,
        'selected_class': selected_class,
        'selected_section': selected_section,
        'selected_session': selected_session,
        'recent_results': recent_results,
        'selected_subject': selected_subject,
    }
    return render(request, 'Teacher/add_result.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def manage_results(request):
    if request.user.user_type != 'Teacher':
        return HttpResponseForbidden('Only teachers can manage results.')

    TeacherInfo.objects.filter(user=request.user).exists()  # ensure teacher exists for context if needed

    classes = Class.objects.all().order_by('class_code')
    sections = Section.objects.all().order_by('name')
    sessions = Session.objects.all().order_by('-start_date')
    subjects = Subject.objects.all().order_by('name')
    exam_type_choices = StudentResult.EXAM_TYPES

    selected_class_id = _parse_int(request.GET.get('klass') or request.POST.get('klass'))
    selected_section_id = _parse_int(request.GET.get('section') or request.POST.get('section'))
    selected_session_id = _parse_int(request.GET.get('session') or request.POST.get('session'))
    selected_subject_id = _parse_int(request.GET.get('subject') or request.POST.get('subject'))
    selected_exam_type = request.GET.get('exam_type') or request.POST.get('exam_type') or ''

    results = StudentResult.objects.select_related(
        'student', 'subject', 'session', 'klass', 'section'
    ).order_by('-recorded_at', 'student__roll_no')

    if selected_class_id:
        results = results.filter(klass_id=selected_class_id)
    if selected_section_id:
        results = results.filter(section_id=selected_section_id)
    if selected_session_id:
        results = results.filter(session_id=selected_session_id)
    if selected_subject_id:
        results = results.filter(subject_id=selected_subject_id)
    if selected_exam_type:
        results = results.filter(exam_type=selected_exam_type)

    result_list = list(results)
    saved_count = 0
    if request.method == 'POST' and result_list:
        for result in result_list:
            marks_value = request.POST.get(f'marks_{result.id}', '').strip()
            grade_value = request.POST.get(f'grade_{result.id}', '').strip() or None
            remark_value = request.POST.get(f'remark_{result.id}', '').strip() or None
            if not marks_value:
                continue
            try:
                obtained_decimal = Decimal(marks_value)
            except (InvalidOperation, TypeError):
                continue
            if obtained_decimal < 0 or obtained_decimal > result.total_marks:
                continue
            if (
                obtained_decimal != result.obtained_marks
                or grade_value != result.grade
                or remark_value != (result.remarks or None)
            ):
                result.obtained_marks = obtained_decimal
                result.grade = grade_value
                result.remarks = remark_value
                result.save(update_fields=['obtained_marks', 'grade', 'remarks', 'updated_at'])
                saved_count += 1

        if saved_count:
            messages.success(
                request,
                f"Updated {saved_count} result{'s' if saved_count != 1 else ''} successfully.",
            )
        else:
            messages.info(request, 'No changes detected to update.')
        redirect_params = []
        for key, value in (
            ('klass', selected_class_id),
            ('section', selected_section_id),
            ('session', selected_session_id),
            ('subject', selected_subject_id),
            ('exam_type', selected_exam_type),
        ):
            if value:
                redirect_params.append(f"{key}={value}")
        redirect_url = reverse('manage_results')
        if redirect_params:
            redirect_url += f"?{'&'.join(map(str, redirect_params))}"
        return redirect(redirect_url)

    context = {
        'classes': classes,
        'sections': sections,
        'sessions': sessions,
        'subjects': subjects,
        'exam_type_choices': exam_type_choices,
        'selected_class_id': selected_class_id,
        'selected_section_id': selected_section_id,
        'selected_session_id': selected_session_id,
        'selected_subject_id': selected_subject_id,
        'selected_exam_type': selected_exam_type,
        'results': result_list,
    }
    return render(request, 'Teacher/manage_results.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def assignment_create(request):
    if request.user.user_type != 'Teacher':
        return HttpResponseForbidden('Only teachers can create assignments.')

    teacher = get_object_or_404(TeacherInfo, user=request.user)
    form = TeacherAssignmentForm(request.POST or None, request.FILES or None)

    if request.method == 'POST' and form.is_valid():
        assignment = form.save(commit=False)
        assignment.teacher = teacher
        assignment.save()
        messages.success(request, 'Assignment created successfully.')
        return redirect('teacher_assignment_list')

    context = {
        'form': form,
    }
    return render(request, 'Teacher/add_assignment.html', context)


@login_required
def teacher_assignment_list(request):
    if request.user.user_type != 'Teacher':
        return HttpResponseForbidden('Only teachers can view assignments.')

    teacher = get_object_or_404(TeacherInfo, user=request.user)
    assignments = Assignment.objects.filter(teacher=teacher).select_related(
        'klass', 'section', 'session', 'subject'
    ).prefetch_related('submissions')

    selected_class_id = _parse_int(request.GET.get('klass'))
    selected_session_id = _parse_int(request.GET.get('session'))
    selected_subject_id = _parse_int(request.GET.get('subject'))

    if selected_class_id:
        assignments = assignments.filter(klass_id=selected_class_id)
    if selected_session_id:
        assignments = assignments.filter(session_id=selected_session_id)
    if selected_subject_id:
        assignments = assignments.filter(subject_id=selected_subject_id)

    assignments = assignments.order_by('-created_at')

    context = {
        'assignments': assignments,
        'classes': Class.objects.all().order_by('class_code'),
        'sessions': Session.objects.all().order_by('-start_date'),
        'subjects': Subject.objects.all().order_by('name'),
        'selected_class_id': selected_class_id,
        'selected_session_id': selected_session_id,
        'selected_subject_id': selected_subject_id,
    }
    return render(request, 'Teacher/assignment_list.html', context)


@login_required
def assignment_detail(request, pk):
    if request.user.user_type != 'Teacher':
        return HttpResponseForbidden('Only teachers can view submissions.')

    assignment = get_object_or_404(
        Assignment.objects.select_related('teacher', 'klass', 'section', 'session', 'subject'),
        pk=pk,
        teacher__user=request.user,
    )
    submissions = assignment.submissions.select_related('student').order_by('-submitted_at')

    context = {
        'assignment': assignment,
        'submissions': submissions,
    }
    return render(request, 'Teacher/assignment_detail.html', context)
