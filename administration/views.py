from django.shortcuts import render

# Create your views here.
def register_admin(request):

    return render(request, 'Admin/register_admin.html')



def admin_home_page(request):
    
    return render(request, 'Admin/home.html')