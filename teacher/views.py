from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from .models import TeacherInfo, TeacherNotification, TeacherLeave, Feedback
from account.models import User
import secrets
import string
from django.views.decorators.http import require_http_methods

from .forms import TeacherLeaveForm, TeacherFeedbackForm


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
