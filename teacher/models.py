from django.db import models
from account.models import User

class TeacherInfo(models.Model):

    GENDER = [
        ("Male", "Male"),
        ("Female", "Female"),
        ("Other", "Other"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': 'Teacher'},
        related_name="teacher_profile"
    )

    teacher_user_id = models.CharField(
        unique=True,
        max_length=15,
        editable=False,
        db_index=True,
        blank=True,
        null=True,
        verbose_name="Teacher ID"
    )

    # -------- Personal Information -------- #
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name  = models.CharField(max_length=50, blank=True, null=True)
    gender     = models.CharField(max_length=10, choices=GENDER, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    phone      = models.CharField(max_length=15, blank=True, null=True)
    email      = models.EmailField(blank=True, null=True)

    # -------- Job Related Info -------- #
    designation  = models.CharField(max_length=100, blank=True, null=True)
    joining_date = models.DateField(blank=True, null=True)
    qualification = models.CharField(max_length=200, blank=True, null=True)
    experience = models.CharField(max_length=100, blank=True, null=True)

    # -------- Address Information -------- #
    present_address  = models.TextField(blank=True, null=True)
    permanent_address = models.TextField(blank=True, null=True)

    # -------- Others -------- #
    profile_pic = models.ImageField(upload_to='teachers/', blank=True, null=True)

    # -------- Auto Timestamp -------- #
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        verbose_name_plural = "Teacher Info" 
        

    # -------- Auto Generate Teacher ID -------- #
    def save(self, *args, **kwargs):
        if not self.teacher_user_id and self.user.user_id:
            self.teacher_user_id = self.user.user_id
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    




# ================ notification ==============================

class TeacherNotification(models.Model):
    teacher_id = models.ForeignKey(TeacherInfo, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.teacher_id.first_name} {self.teacher_id.last_name}"
