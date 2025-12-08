from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def student_list(request):

    return HttpResponse("This is a student list page")



def student_create(request):

    return render(request, 'Student/add_student.html')