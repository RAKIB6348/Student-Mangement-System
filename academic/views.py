from django.shortcuts import render

# Create your views here.
def subject_list(request):
    
    return render(request, 'Academic/subject/subject_list.html')


def add_subject(request):

    return render(request, 'Academic/subject/add_subject.html')


def edit_subject(request):
    
    
    return render(request, 'Academic/subject/edit_subject.html')



def add_section(request):

    return render(request, 'Academic/add_section.html')



def add_session(request):

    return render(request, 'Academic/add_session.html')




def add_class(request):
    return render(request, 'Academic/add_class.html')
