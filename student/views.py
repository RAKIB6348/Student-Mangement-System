from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

# Create your views here.
def student_list(request):

    return HttpResponse("This is a student list page")



def student_create(request):

    return render(request, 'Student/add_student.html')


@login_required
def student_dashboard(request):

    return render(request, 'Student/student_dashboard.html')