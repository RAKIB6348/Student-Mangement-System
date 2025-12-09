from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import StudentInfo

# Create your views here.
def student_list(request):

    students = StudentInfo.objects.all()

    context = {
        "students": students,
    }

    return render(request, "Student/student_list.html", context)



def student_create(request):

    return render(request, 'Student/add_student.html')


@login_required
def student_dashboard(request):

    return render(request, 'Student/student_dashboard.html')
