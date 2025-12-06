from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
def register_admin(request):

    return render(request, 'Admin/register_admin.html')


@login_required
def admin_home_page(request):
    
    return render(request, 'Admin/home.html')