from django.db import models
from account.models import User   # your custom user model

class AdminProfile(models.Model):

    GENDER = [
        ("Male", "Male"),
        ("Female", "Female"),
        ("Other", "Other"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="admin_profile",
        limit_choices_to={'user_type': 'Admin'}  # only admin users allowed
    )

    # 🔹 New field as requested
    admin_user_id = models.CharField(
        max_length=15,
        unique=True,
        blank=True,
        null=True,
        db_index=True,
        verbose_name="Admin User ID"
    )

    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name  = models.CharField(max_length=50, blank=True, null=True)
    gender     = models.CharField(max_length=10, choices=GENDER, blank=True, null=True)

    phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    designation = models.CharField(max_length=100, blank=True, null=True)

    address = models.TextField(blank=True, null=True)
    profile_pic = models.ImageField(upload_to='admins/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        verbose_name_plural = "Admin"

    def save(self, *args, **kwargs):
        if not self.admin_user_id and self.user.user_id:
            self.admin_user_id = self.user.user_id

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name}{self.last_name}"
