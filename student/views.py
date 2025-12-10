from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import StudentInfo
from account.models import User
from academic.models import Session, Class, Section
import secrets
import string

# Create your views here.
def student_list(request):

    students = StudentInfo.objects.all()

    context = {
        "students": students,
    }

    return render(request, "Student/student_list.html", context)



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
