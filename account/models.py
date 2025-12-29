from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):

    USER_TYPE_CHOICE = [
        ('Admin', 'Admin'),
        ('Teacher', 'Teacher'),
        ('Student', 'Student'),
    ]

    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICE,
        null=True,
        blank=True,
    )

    user_id = models.CharField(
        unique=True,
        max_length=15,
        editable=False,
        db_index=True,
        blank=True,
        null=True,
    )

    profile_pic = models.ImageField(
        upload_to='profile_pics/',
        blank=True,
        null=True,
    )


    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        null=True,
        blank=True,
    )

    phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
    )

    address = models.TextField(
        null=True,
        blank=True,
    )

    def save(self, *args, **kwargs):
        # শুধু প্রথমবার তৈরি হওয়ার সময়েই user_id generate হবে
        if not self.user_id and self.user_type:
            now = timezone.now()
            year = now.strftime("%y")   # 2025 -> "25"
            month = now.strftime("%m")  # 03 -> "03"

            # Role অনুযায়ী digit map
            role_map = {
                "Admin": "99",
                "Teacher": "88",
            }
            role_digit = role_map.get(self.user_type, "0")

            # Final prefix: YYMMR  (e.g. 25031, 25032, 25033)
            prefix = f"{year}{month}{role_digit}"

            # এই prefix দিয়ে শুরু হওয়া সর্বশেষ user খুঁজে বের করি
            last = (
                User.objects
                .filter(user_id__startswith=prefix)
                .order_by("-user_id")
                .first()
            )

            if last and last.user_id and last.user_id[len(prefix):].isdigit():
                counter = int(last.user_id[len(prefix):]) + 1
            else:
                counter = 1

            # Final user_id: YYMMR + 4 digit (e.g. 250310001)
            self.user_id = f"{prefix}{counter:04d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.user_id})"
