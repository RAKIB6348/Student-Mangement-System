import json
import secrets
import string
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from account.models import User
from academic.models import Class, Section, Session, Subject
from student.models import StudentFeedback, StudentInfo, StudentLeave, StudentNotification
from teacher.models import (
    Attendance,
    AttendanceRecord,
    Feedback,
    TeacherInfo,
    TeacherLeave,
    TeacherNotification,
)

from .models import AdminProfile


def _parse_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _generate_admin_username():
    prefix = 'admin'
    next_number = 1
    last_admin_user = (
        User.objects.filter(user_type='Admin', username__startswith=prefix)
        .order_by('-id')
        .first()
    )

    if last_admin_user and last_admin_user.username.startswith(prefix):
        try:
            last_number = int(last_admin_user.username.replace(prefix, ''))
            next_number = last_number + 1
        except ValueError:
            next_number = User.objects.filter(user_type='Admin').count() + 1

    username = f'{prefix}{next_number}'
    while User.objects.filter(username=username).exists():
        next_number += 1
        username = f'{prefix}{next_number}'
    return username


def _generate_admin_password(length=12):
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(length))


# Create your views here.
def register_admin(request):
    generated_username = None
    generated_password = None

    if request.method == 'POST':
        generated_username = request.POST.get('generated_username') or _generate_admin_username()
        generated_password = request.POST.get('generated_password') or _generate_admin_password()
        try:
            # Get form data - Account Info
            email = request.POST.get('email')

            # Get form data - Personal Info
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            gender = request.POST.get('gender')
            phone = request.POST.get('phone') or None
            designation = request.POST.get('designation') or None
            address = request.POST.get('address') or None
            profile_pic = request.FILES.get('profile_pic')

            # Check if email already exists
            if User.objects.filter(email=email).exists():
                messages.error(request, f'Email "{email}" already exists!')
            else:
                username_to_use = generated_username or _generate_admin_username()
                if User.objects.filter(username=username_to_use).exists():
                    username_to_use = _generate_admin_username()

                password_to_use = generated_password or _generate_admin_password()

                # Create User account first
                user = User.objects.create_user(
                    username=username_to_use,
                    email=email,
                    password=password_to_use,
                    first_name=first_name,
                    last_name=last_name,
                    user_type='Admin',
                    gender=gender,
                    phone=phone,
                    address=address,
                    profile_pic=profile_pic,
                )

                # Create AdminProfile record
                admin_profile = AdminProfile.objects.create(
                    user=user,
                    first_name=first_name,
                    last_name=last_name,
                    gender=gender,
                    phone=phone,
                    email=email,
                    designation=designation,
                    address=address,
                    profile_pic=profile_pic,
                )

                messages.success(
                    request,
                    f'Admin {first_name} {last_name} registered successfully! '
                    f'Admin ID: {admin_profile.admin_user_id} | Username: {username_to_use} | Password: {password_to_use}'
                )
                return redirect('admin_home_page')

        except Exception as e:
            messages.error(request, f'Error registering admin: {str(e)}')
    else:
        generated_username = _generate_admin_username()
        generated_password = _generate_admin_password()

    context = {
        'generated_username': generated_username,
        'generated_password': generated_password,
    }
    return render(request, 'Admin/register_admin.html', context)


def admin_list(request):
    """Display list of all admins"""
    admins = AdminProfile.objects.all().select_related('user').order_by('-created_at')

    context = {
        'admins': admins,
    }

    return render(request, 'Admin/admin_list.html', context)


def admin_detail(request, id):
    admin = get_object_or_404(
        AdminProfile.objects.select_related('user'),
        id=id
    )

    context = {
        "admin": admin,
    }
    return render(request, 'Admin/admin_detail.html', context)


@login_required
def admin_home_page(request):
    
    student_count = StudentInfo.objects.all().count()
    teacher_count = TeacherInfo.objects.all().count()
    class_count = Class.objects.all().count()
    subject_count = Subject.objects.all().count()

    class_student_data = (
        StudentInfo.objects.filter(klass__isnull=False)
        .values('klass__name', 'klass__class_code')
        .annotate(total=Count('id'))
        .order_by('klass__class_code', 'klass__name')
    )

    class_student_labels = [entry['klass__name'] for entry in class_student_data]
    class_student_counts = [entry['total'] for entry in class_student_data]

    context = {
        'student_count': student_count,
        'teacher_count': teacher_count,
        'class_count': class_count,
        'subject_count': subject_count,
        'class_student_labels': json.dumps(class_student_labels),
        'class_student_counts': json.dumps(class_student_counts),
    }

    return render(request, 'Admin/home.html', context)


@login_required
def attendance_overview(request):
    if request.user.user_type != 'Admin':
        return HttpResponseForbidden('Only admins can view attendance data.')

    classes = Class.objects.all().order_by('class_code')
    sections = Section.objects.all().order_by('name')
    sessions = Session.objects.all().order_by('-start_date')
    subjects = Subject.objects.all().order_by('name')
    teachers = TeacherInfo.objects.all().order_by('first_name', 'last_name')

    filter_values = {
        'klass': request.GET.get('klass', ''),
        'section': request.GET.get('section', ''),
        'session': request.GET.get('session', ''),
        'subject': request.GET.get('subject', ''),
        'teacher': request.GET.get('teacher', ''),
        'date': request.GET.get('date', ''),
    }

    klass_id = _parse_int(filter_values['klass'])
    section_id = _parse_int(filter_values['section'])
    session_id = _parse_int(filter_values['session'])
    subject_id = _parse_int(filter_values['subject'])
    teacher_id = _parse_int(filter_values['teacher'])

    attendances = (
        Attendance.objects.select_related('teacher', 'klass', 'section', 'session', 'subject')
        .prefetch_related('records__student')
        .order_by('-date', '-created_at')
    )

    if klass_id:
        attendances = attendances.filter(klass_id=klass_id)
    if section_id:
        attendances = attendances.filter(section_id=section_id)
    if session_id:
        attendances = attendances.filter(session_id=session_id)
    if subject_id:
        attendances = attendances.filter(subject_id=subject_id)
    if teacher_id:
        attendances = attendances.filter(teacher_id=teacher_id)

    selected_date_value = filter_values['date']
    if selected_date_value:
        try:
            selected_date = datetime.strptime(selected_date_value, "%Y-%m-%d").date()
            attendances = attendances.filter(date=selected_date)
        except ValueError:
            messages.error(request, 'Invalid date filter. Showing results without the date filter.')
            filter_values['date'] = ''

    attendance_list = []
    total_records = 0
    total_present = 0
    total_absent = 0

    for attendance in attendances:
        records = list(attendance.records.all())
        attendance.summary_total = len(records)
        attendance.summary_present = sum(
            1 for record in records if record.status == AttendanceRecord.STATUS_PRESENT
        )
        attendance.summary_absent = sum(
            1 for record in records if record.status == AttendanceRecord.STATUS_ABSENT
        )
        total_records += attendance.summary_total
        total_present += attendance.summary_present
        total_absent += attendance.summary_absent
        attendance_list.append(attendance)

    overall_summary = {
        'sessions': len(attendance_list),
        'records': total_records,
        'present': total_present,
        'absent': total_absent,
    }

    selected_attendance_id = _parse_int(request.GET.get('attendance_id'))
    selected_attendance = None
    selected_records = []
    selected_summary = None

    if selected_attendance_id:
        selected_attendance = next(
            (att for att in attendance_list if att.id == selected_attendance_id),
            None
        )
        if selected_attendance:
            selected_records = list(
                selected_attendance.records.select_related('student', 'student__section')
                .order_by('student__roll_no', 'student__first_name', 'student__last_name')
            )
            selected_summary = {
                'total': selected_attendance.summary_total,
                'present': selected_attendance.summary_present,
                'absent': selected_attendance.summary_absent,
            }
        else:
            messages.warning(request, 'The selected attendance entry was not found in the current filters.')

    context = {
        'classes': classes,
        'sections': sections,
        'sessions': sessions,
        'subjects': subjects,
        'teachers': teachers,
        'attendances': attendance_list,
        'filters': filter_values,
        'overall_summary': overall_summary,
        'selected_attendance': selected_attendance,
        'selected_records': selected_records,
        'selected_summary': selected_summary,
    }
    return render(request, 'Admin/attendance_overview.html', context)


def admin_edit(request, id):
    # Get the admin instance or return 404
    admin = AdminProfile.objects.select_related('user').get(id=id)

    if request.method == 'POST':
        try:
            # Get form data - Personal Info
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            gender = request.POST.get('gender')
            phone = request.POST.get('phone') or None
            designation = request.POST.get('designation') or None
            address = request.POST.get('address') or None
            profile_pic = request.FILES.get('profile_pic')

            # Update User account
            admin.user.first_name = first_name
            admin.user.last_name = last_name
            admin.user.email = email
            admin.user.gender = gender
            admin.user.phone = phone
            admin.user.address = address

            # Update profile picture in User model only if new one is uploaded
            if profile_pic:
                admin.user.profile_pic = profile_pic

            admin.user.save()

            # Update AdminProfile record
            admin.first_name = first_name
            admin.last_name = last_name
            admin.email = email
            admin.gender = gender
            admin.phone = phone
            admin.designation = designation
            admin.address = address

            # Update profile picture in AdminProfile model only if new one is uploaded
            if profile_pic:
                admin.profile_pic = profile_pic

            admin.save()

            messages.success(request, f'Admin {first_name} {last_name} updated successfully!')
            return redirect('admin_list')

        except Exception as e:
            messages.error(request, f'Error updating admin: {str(e)}')

    context = {
        'admin': admin,
    }
    return render(request, 'Admin/edit_admin.html', context)


def admin_delete(request, id):
    try:
        admin = AdminProfile.objects.select_related('user').get(id=id)
        admin_name = f"{admin.first_name} {admin.last_name}"

        # Delete the associated user account as well
        user = admin.user
        admin.delete()
        user.delete()

        messages.success(request, f'Admin {admin_name} has been deleted successfully!')
    except AdminProfile.DoesNotExist:
        messages.error(request, 'Admin not found.')
    except Exception as e:
        messages.error(request, f'Error deleting admin: {str(e)}')

    return redirect('admin_list')



#===================== teacher feedback ======================
def send_teacher_notification(request):
    if request.method == 'POST':
        try:
            teacher_id = request.POST.get('teacher_id')
            subject = request.POST.get('subject')
            message = request.POST.get('message')

            if not teacher_id or not subject or not message:
                messages.error(request, 'All fields are required!')
            else:
                teacher = get_object_or_404(TeacherInfo, id=teacher_id)

                TeacherNotification.objects.create(
                    teacher_id=teacher,
                    subject=subject,
                    message=message
                )

                messages.success(
                    request,
                    f'Notification sent successfully to {teacher.first_name} {teacher.last_name}!'
                )

        except Exception as e:
            messages.error(request, f'Error sending notification: {str(e)}')

        return redirect('send_teacher_notification')

    teacher = TeacherInfo.objects.all()

    context = {
        'teacher': teacher,
    }

    return render(request, 'Admin/send_teacher_notification.html', context)


def view_teacher_notifications(request):
    """Display all sent teacher notifications"""
    notifications = TeacherNotification.objects.all().select_related('teacher_id').order_by('-created_at')

    context = {
        'notifications': notifications,
    }

    return render(request, 'Admin/view_teacher_notifications.html', context)


def send_student_notification(request):
    if request.method == 'POST':
        try:
            student_id = request.POST.get('student_id')
            subject = request.POST.get('subject')
            message = request.POST.get('message')

            if not student_id or not subject or not message:
                messages.error(request, 'All fields are required!')
            else:
                student = get_object_or_404(StudentInfo, id=student_id)

                StudentNotification.objects.create(
                    student=student,
                    subject=subject,
                    message=message
                )

                messages.success(
                    request,
                    f'Notification sent successfully to {student.first_name} {student.last_name}!'
                )

        except Exception as e:
            messages.error(request, f'Error sending notification: {str(e)}')

        return redirect('send_student_notification')

    students = StudentInfo.objects.all()

    context = {
        'students': students,
    }

    return render(request, 'Admin/send_student_notification.html', context)


def view_student_notifications(request):
    notifications = StudentNotification.objects.all().select_related('student').order_by('-created_at')

    context = {
        'notifications': notifications,
    }

    return render(request, 'Admin/view_student_notifications.html', context)


@login_required
def teacher_leave(request):
    if request.user.user_type != 'Admin':
        return HttpResponseForbidden('You do not have permission to view teacher leaves.')

    leaves = TeacherLeave.objects.select_related('teacher').order_by('-created_at')

    if request.method == 'POST':
        leave_id = request.POST.get('leave_id')
        action = request.POST.get('status')

        try:
            if not leave_id or not action:
                raise ValueError('Leave and status are required.')

            leave = TeacherLeave.objects.get(id=leave_id)
            if action not in dict(TeacherLeave.STATUS):
                raise ValueError('Invalid status selected.')

            leave.status = action
            leave.save(update_fields=['status'])
            messages.success(request, f'Leave status updated to {action}.')
        except TeacherLeave.DoesNotExist:
            messages.error(request, 'Leave request not found.')
        except Exception as exc:
            messages.error(request, f'Unable to update leave: {exc}')

        return redirect('teacher_leave')

    return render(request, 'Admin/teacher_leave.html', {
        'leaves': leaves,
        'status_choices': TeacherLeave.STATUS,
    })


@login_required
def student_leave(request):
    if request.user.user_type != 'Admin':
        return HttpResponseForbidden('You do not have permission to view student leaves.')

    leaves = StudentLeave.objects.select_related('student').order_by('-created_at')

    if request.method == 'POST':
        leave_id = request.POST.get('leave_id')
        action = request.POST.get('status')

        try:
            if not leave_id or not action:
                raise ValueError('Leave and status are required.')

            leave = StudentLeave.objects.get(id=leave_id)
            if action not in dict(StudentLeave.STATUS):
                raise ValueError('Invalid status selected.')

            leave.status = action
            leave.save(update_fields=['status'])
            messages.success(request, f'Leave status updated to {action}.')
        except StudentLeave.DoesNotExist:
            messages.error(request, 'Leave request not found.')
        except Exception as exc:
            messages.error(request, f'Unable to update leave: {exc}')

        return redirect('student_leave')

    return render(request, 'Admin/student_leave.html', {
        'leaves': leaves,
        'status_choices': StudentLeave.STATUS,
    })


@login_required
def teacher_feedback_admin(request):
    if request.user.user_type != 'Admin':
        return HttpResponseForbidden('You do not have permission to view teacher feedback.')

    if request.method == 'POST':
        feedback_id = request.POST.get('feedback_id')
        reply_text = request.POST.get('feedback_reply', '').strip()

        try:
            feedback_obj = Feedback.objects.get(id=feedback_id)
        except (Feedback.DoesNotExist, TypeError, ValueError):
            messages.error(request, 'Feedback entry not found.')
        else:
            if not reply_text:
                messages.error(request, 'Reply cannot be empty.')
            else:
                feedback_obj.feedback_reply = reply_text
                feedback_obj.save(update_fields=['feedback_reply', 'updated_at'])
                messages.success(request, 'Reply saved successfully.')

        return redirect('teacher_feedback_admin')

    feedback_entries = Feedback.objects.select_related('teacher', 'teacher__user').order_by('-created_at')

    return render(request, 'Admin/teacher_feedback.html', {
        'feedback_entries': feedback_entries,
    })


@login_required
def student_feedback_admin(request):
    if request.user.user_type != 'Admin':
        return HttpResponseForbidden('You do not have permission to view student feedback.')

    if request.method == 'POST':
        feedback_id = request.POST.get('feedback_id')
        reply_text = request.POST.get('feedback_reply', '').strip()

        try:
            feedback_obj = StudentFeedback.objects.get(id=feedback_id)
        except (StudentFeedback.DoesNotExist, TypeError, ValueError):
            messages.error(request, 'Feedback entry not found.')
        else:
            if not reply_text:
                messages.error(request, 'Reply cannot be empty.')
            else:
                feedback_obj.feedback_reply = reply_text
                feedback_obj.save(update_fields=['feedback_reply', 'updated_at'])
                messages.success(request, 'Reply saved successfully.')

        return redirect('student_feedback_admin')

    feedback_entries = StudentFeedback.objects.select_related('student', 'student__user').order_by('-created_at')

    return render(request, 'Admin/student_feedback.html', {
        'feedback_entries': feedback_entries,
    })
