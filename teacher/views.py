from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
def teacher_list(request):

    return render(request, 'Teacher/teacher_list.html')



def add_teacher(request):

    return render(request, 'Teacher/add_teacher.html')


@login_required
def teacher_dashboard(request):
    
    return render(request, "Teacher/teacher_dashboard.html")