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


#===================== change password ========================
@login_required
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # Validation
        if not current_password or not new_password or not confirm_password:
            messages.error(request, 'All fields are required!')
            return render(request, 'Profile/change_password.html')

        # Check if current password is correct
        if not request.user.check_password(current_password):
            messages.error(request, 'Current password is incorrect!')
            return render(request, 'Profile/change_password.html')

        # Check if new password and confirm password match
        if new_password != confirm_password:
            messages.error(request, 'New password and confirm password do not match!')
            return render(request, 'Profile/change_password.html')

        # Check password length
        if len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters long!')
            return render(request, 'Profile/change_password.html')

        # Check if new password is same as current password
        if current_password == new_password:
            messages.error(request, 'New password cannot be the same as current password!')
            return render(request, 'Profile/change_password.html')

        # Update password
        try:
            request.user.set_password(new_password)
            request.user.save()

            # Re-login the user to maintain session
            login(request, request.user)

            messages.success(request, 'Password changed successfully!')
            return redirect('profile_page')
        except Exception as e:
            messages.error(request, f'Error changing password: {str(e)}')
            return render(request, 'Profile/change_password.html')

    return render(request, 'Profile/change_password.html')


