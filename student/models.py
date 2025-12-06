from django.db import models
from django.utils import timezone
from account.models import User
from academic.models import Section, Class, Session

class StudentInfo(models.Model):
    GENDER = [
        ("Male", "Male"),
        ("Female", "Female"),
        ("Other", "Other"),
    ]
    BLOOD_GROUP = [
        ("A+", "A+"),
        ("A-", "A-"),
        ("B+", "B+"),
        ("B-", "B-"),
        ("O+", "O+"),
        ("O-", "O-"),
        ("AB+", "AB+"),
        ("AB-", "AB-"),
    ]
    
    # ---------------- User Link ---------------- #
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': 'Student'},
        related_name="student_profile",
    )
    student_user_id = models.CharField(
        unique=True,
        max_length=15,
        editable=False,
        blank=True,
        null=True,
        db_index=True,
        verbose_name="Student User ID",
    )
    admission_no = models.CharField(
        max_length=12,
        unique=True,
        editable=False,
        blank=True,
        null=True,
        db_index=True,
        verbose_name="Admission Number"
    )
    
    # ---------------- Academic Info ---------------- #
    session = models.ForeignKey(
        Session,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="students",
    )
    klass = models.ForeignKey(
        Class,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="students",
        verbose_name="Class",
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="students",
    )
    roll_no = models.PositiveIntegerField(
        null=True,
        blank=True,
        editable=False,  # Make it auto-generated
        verbose_name="Roll Number",
    )
    
    # ---------------- Personal Info ---------------- #
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name  = models.CharField(max_length=50, blank=True, null=True)
    gender     = models.CharField(max_length=10, choices=GENDER, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    blood_group   = models.CharField(
        max_length=3,
        choices=BLOOD_GROUP,
        blank=True,
        null=True,
    )
    phone      = models.CharField(max_length=15, blank=True, null=True)
    email      = models.EmailField(blank=True, null=True)
    
    # ---------------- Guardian Info ---------------- #
    guardian_name   = models.CharField(max_length=100, blank=True, null=True)
    guardian_phone  = models.CharField(max_length=15, blank=True, null=True)
    guardian_email  = models.EmailField(blank=True, null=True)
    guardian_relation = models.CharField(max_length=50, blank=True, null=True)
    guardian_address  = models.TextField(blank=True, null=True)
    
    # ---------------- Address & Misc ---------------- #
    present_address  = models.TextField(blank=True, null=True)
    permanent_address = models.TextField(blank=True, null=True)
    profile_pic = models.ImageField(upload_to="students/", blank=True, null=True)
    
    # ---------------- Timestamps ---------------- #
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # ---------------- Auto Generate IDs ---------------- #
    def save(self, *args, **kwargs):
        now = timezone.now()
        year = now.strftime("%y")   # 2025 -> "25"
        month = now.strftime("%m")  # 03 -> "03"
        
        # ============================================
        # Generate student_user_id (YYMMCC0001)
        # ============================================
        if not self.student_user_id and self.klass:
            # Get class_code (2 digits max)
            class_code = f"{self.klass.class_code:02d}"  # e.g., 1 -> "01", 10 -> "10"
            
            # Prefix: YYMM + class_code (e.g., "250301" for year=25, month=03, class=01)
            prefix = f"{year}{month}{class_code}"
            
            # Find last student with this prefix
            last = StudentInfo.objects.filter(
                student_user_id__startswith=prefix
            ).order_by("-student_user_id").first()
            
            # Increment counter
            if last:
                # Extract last 4 digits and increment
                counter = int(last.student_user_id[-4:]) + 1
            else:
                counter = 1
            
            # Generate student_user_id: prefix + 4-digit counter
            # Format: YYMM + CC + 0001 (e.g., "2503010001")
            self.student_user_id = f"{prefix}{counter:04d}"
            
            # Update User.user_id with the same student_user_id
            if self.user:
                self.user.user_id = self.student_user_id
                self.user.save(update_fields=['user_id'])
        
        # ============================================
        # Generate admission_no (ADM-YYMM-0001)
        # ============================================
        if not self.admission_no:
            # Prefix: ADM-YYMM (e.g., "ADM-2503")
            admission_prefix = f"ADM-{year}{month}"
            
            # Find last admission number with this prefix
            last_admission = StudentInfo.objects.filter(
                admission_no__startswith=admission_prefix
            ).order_by("-admission_no").first()
            
            # Increment counter
            if last_admission:
                # Extract last 4 digits after the last hyphen
                last_counter = int(last_admission.admission_no.split('-')[-1])
                counter = last_counter + 1
            else:
                counter = 1
            
            # Generate admission_no: ADM-YYMM-0001
            self.admission_no = f"{admission_prefix}-{counter:04d}"
        
        # ============================================
        # Auto-set roll_no from last 4 digits of student_user_id
        # ============================================
        if self.student_user_id and not self.roll_no:
            # Extract last 4 digits and convert to integer
            self.roll_no = int(self.student_user_id[-4:])
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    class Meta:
        verbose_name = "Student Info"
        verbose_name_plural = "Students Info"
        ordering = ["session", "klass", "section", "roll_no"]