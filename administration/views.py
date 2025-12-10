from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import AdminProfile
from account.models import User

# Create your views here.
def register_admin(request):
    if request.method == 'POST':
        try:
            # Get form data - Account Info
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            # Get form data - Personal Info
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            gender = request.POST.get('gender')
            phone = request.POST.get('phone') or None
            designation = request.POST.get('designation') or None
            address = request.POST.get('address') or None
            profile_pic = request.FILES.get('profile_pic')

            # Validate passwords
            if password != confirm_password:
                messages.error(request, 'Passwords do not match!')
                return render(request, 'Admin/register_admin.html')

            if len(password) < 8:
                messages.error(request, 'Password must be at least 8 characters long!')
                return render(request, 'Admin/register_admin.html')

            # Check if username already exists
            if User.objects.filter(username=username).exists():
                messages.error(request, f'Username "{username}" already exists!')
                return render(request, 'Admin/register_admin.html')

            # Check if email already exists
            if User.objects.filter(email=email).exists():
                messages.error(request, f'Email "{email}" already exists!')
                return render(request, 'Admin/register_admin.html')

            # Create User account first
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type='Admin',
                gender=gender,
                phone=phone,
                address=address,
                profile_pic=profile_pic,
            )

            # Create AdminProfile record
            admin_profile = AdminProfile.objects.create(
                user=user,
                first_name=first_name,
                last_name=last_name,
                gender=gender,
                phone=phone,
                email=email,
                designation=designation,
                address=address,
                profile_pic=profile_pic,
            )

            messages.success(request, f'Admin {first_name} {last_name} registered successfully! Admin ID: {admin_profile.admin_user_id}')
            return redirect('admin_home_page')

        except Exception as e:
            messages.error(request, f'Error registering admin: {str(e)}')

    return render(request, 'Admin/register_admin.html')


def admin_list(request):
    """Display list of all admins"""
    admins = AdminProfile.objects.all().select_related('user').order_by('-created_at')

    context = {
        'admins': admins,
    }

    return render(request, 'Admin/admin_list.html', context)


@login_required
def admin_home_page(request):

    return render(request, 'Admin/home.html')