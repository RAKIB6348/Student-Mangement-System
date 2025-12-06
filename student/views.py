from django.shortcuts import render, HttpResponse

# Create your views here.
def student_list(request):

    return HttpResponse("This is a student list page")



def student_create(request):

    return HttpResponse("This is a student create page")