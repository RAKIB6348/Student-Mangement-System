from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.http import HttpResponse
from .models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site



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


#===================== forgot password ========================
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        # Validation
        if not email:
            messages.error(request, 'Email is required!')
            return render(request, 'forgot_password.html')

        # Check if user with this email exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Don't reveal if email exists or not for security
            messages.success(request, 'If your email is registered, you will receive a password reset link shortly.')
            return render(request, 'forgot_password.html')

        # Generate password reset token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # Build reset password URL
        current_site = get_current_site(request)
        reset_url = f"{request.scheme}://{current_site.domain}/reset-password/{uid}/{token}/"

        # Send email
        subject = 'Password Reset Request - Student Management System'
        message = f"""
Hello {user.first_name} {user.last_name},

You requested to reset your password for your Student Management System account.

Please click the link below to reset your password:
{reset_url}

This link will expire in 24 hours.

If you did not request this password reset, please ignore this email.

User ID: {user.user_id}
Username: {user.username}

Best regards,
Student Management System Team
        """

        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            messages.success(request, 'Password reset link has been sent to your email address.')
        except Exception as e:
            # If email fails, show the reset link directly (for development)
            messages.warning(request, f'Could not send email. Reset link: {reset_url}')
            print(f"Email error: {str(e)}")

        return render(request, 'forgot_password.html')

    return render(request, 'forgot_password.html')


#===================== reset password ========================
def reset_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    # Check if token is valid
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            # Validation
            if not new_password or not confirm_password:
                messages.error(request, 'All fields are required!')
                return render(request, 'reset_password.html', {'validlink': True})

            # Check if passwords match
            if new_password != confirm_password:
                messages.error(request, 'Passwords do not match!')
                return render(request, 'reset_password.html', {'validlink': True})

            # Check password length
            if len(new_password) < 8:
                messages.error(request, 'Password must be at least 8 characters long!')
                return render(request, 'reset_password.html', {'validlink': True})

            # Update password
            try:
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password has been reset successfully! You can now login with your new password.')
                return redirect('login_page')
            except Exception as e:
                messages.error(request, f'Error resetting password: {str(e)}')
                return render(request, 'reset_password.html', {'validlink': True})

        # GET request - show reset password form
        context = {
            'validlink': True,
            'user': user,
        }
        return render(request, 'reset_password.html', context)
    else:
        # Invalid token
        messages.error(request, 'This password reset link is invalid or has expired.')
        return render(request, 'reset_password.html', {'validlink': False})


