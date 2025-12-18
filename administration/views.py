import json
import secrets
import string

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count

from .models import AdminProfile
from account.models import User

from student.models import StudentInfo
from teacher.models import TeacherInfo, TeacherNotification
from academic.models import Subject, Class


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
