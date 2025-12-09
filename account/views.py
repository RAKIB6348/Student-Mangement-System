from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.http import HttpResponse
from .models import User
from django.contrib.auth.decorators import login_required



User = get_user_model()

#======================= dashboard page ==================
def dashboard_base_page(request):

    return render(request, 'base.html')



#=========== login page ====================
def login_page(request):

    return render(request, 'login.html')


# ============= User Login ===================
def user_login(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        password = request.POST.get('password')

        # Validation
        if not user_id or not password:
            messages.error(request, "User ID and Password are required.")
            return render(request, 'login.html')

        # Authenticate directly with user_id via the custom backend
        user = authenticate(request, user_id=user_id, password=password)

        if user is None:
            messages.error(request, "Invalid User ID or Password.")
            return render(request, 'login.html')

        # SUCCESS login
        login(request, user)

        # ===== Redirect based on user_type =====
        if user.user_type == 'Admin':
            return redirect("admin_home_page")
        elif user.user_type == 'Teacher':
            return redirect('teacher_dashboard')
        elif user.user_type == 'Student':
            return redirect('student_dashboard')

        messages.error(request, "Invalid User ID or Password.")
        return redirect('login_page')

    # GET request
    return redirect('login_page')



# =========== Logout ====================
def user_logout(request):
    """
    Logout user
    """
    logout(request)
    messages.success(request, 'You have been logged out successfully!')
    return redirect('login_page')




#===================== profile page ========================
@login_required
def profile_page(request):

    user = request.user
    print("User=============================", user)

    context = {
        'user' : user,
    }

    return render(request, 'Profile/profile.html', context)


