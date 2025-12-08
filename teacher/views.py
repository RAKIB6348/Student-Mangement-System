from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def teacher_list(request):

    return HttpResponse('This is a teacher list page')



def add_teacher(request):

    return render(request, 'Teacher/add_teacher.html')