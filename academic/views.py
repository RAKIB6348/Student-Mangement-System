from django.shortcuts import render

#===================== subject ===============================
def subject_list(request):
    
    return render(request, 'Academic/subject/subject_list.html')


def add_subject(request):

    return render(request, 'Academic/subject/add_subject.html')


def edit_subject(request):
    
    
    return render(request, 'Academic/subject/edit_subject.html')

#===================== section =============================

def add_section(request):

    return render(request, 'Academic/add_section.html')

#======================= session ==========================

def add_session(request):

    return render(request, 'Academic/add_session.html')


#========================= class ======================================
def add_class(request):
    return render(request, 'Academic/class/add_class.html')


def class_list(request):

    return render(request, 'Academic/class/class_list.html')
