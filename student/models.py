from django.db import models
from django.utils import timezone
from account.models import User
from academic.models import Section, Class, Session, Subject

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
    religion   = models.CharField(max_length=50, blank=True, null=True)
    joining_date = models.DateField(blank=True, null=True)
    phone      = models.CharField(max_length=15, blank=True, null=True)
    email      = models.EmailField(blank=True, null=True)

    # ---------------- Parent Info ---------------- #
    father_name = models.CharField(max_length=100, blank=True, null=True)
    father_occupation = models.CharField(max_length=100, blank=True, null=True)
    father_mobile = models.CharField(max_length=15, blank=True, null=True)
    father_email = models.EmailField(blank=True, null=True)
    mother_name = models.CharField(max_length=100, blank=True, null=True)
    mother_occupation = models.CharField(max_length=100, blank=True, null=True)
    mother_mobile = models.CharField(max_length=15, blank=True, null=True)
    mother_email = models.EmailField(blank=True, null=True)

    # -------- Address Information -------- #
    present_address  = models.TextField(blank=True, null=True)
    permanent_address = models.TextField(blank=True, null=True)

    # ---------------- Profile Picture ---------------- #
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
        verbose_name_plural = "Student"
        ordering = ["session", "klass", "section", "roll_no"]


class StudentNotification(models.Model):
    student = models.ForeignKey(
        StudentInfo,
        on_delete=models.CASCADE,
        related_name="notifications"
    )
    subject = models.CharField(max_length=250, blank=True, null=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Student Notifications"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Notification for {self.student.first_name} {self.student.last_name}"


class StudentFeedback(models.Model):
    student = models.ForeignKey(
        StudentInfo,
        on_delete=models.CASCADE,
        related_name="feedback_entries"
    )
    feedback = models.TextField()
    feedback_reply = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Student Feedback"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Feedback from {self.student.first_name} {self.student.last_name}"


class StudentLeave(models.Model):
    LEAVE_TYPE = (
        ("Casual", "Casual"),
        ("Sick", "Sick"),
        ("Annual", "Annual"),
    )

    STATUS = (
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
    )

    student = models.ForeignKey(
        StudentInfo,
        on_delete=models.CASCADE,
        related_name="leaves"
    )
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student.first_name} {self.student.last_name}"


class StudentResult(models.Model):
    EXAM_TYPES = [
        ("Midterm", "Mid Term"),
        ("Final", "Final"),
        ("Quiz", "Quiz/Test"),
        ("Practical", "Practical"),
        ("Other", "Other"),
    ]

    student = models.ForeignKey(
        StudentInfo,
        on_delete=models.CASCADE,
        related_name="results",
    )
    session = models.ForeignKey(
        Session,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="student_results",
    )
    klass = models.ForeignKey(
        Class,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="student_results",
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="student_results",
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="student_results",
    )
    exam_type = models.CharField(
        max_length=20,
        choices=EXAM_TYPES,
        default="Final",
    )
    total_marks = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        help_text="Maximum marks for this exam or assessment.",
    )
    obtained_marks = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        help_text="Marks obtained by the student.",
    )
    grade = models.CharField(
        max_length=5,
        blank=True,
        null=True,
        help_text="Optional grade or letter representation.",
    )
    remarks = models.TextField(
        blank=True,
        null=True,
    )
    recorded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Student Result"
        verbose_name_plural = "Student Results"
        ordering = ["-recorded_at"]
        unique_together = ("student", "subject", "exam_type", "session")

    def __str__(self):
        subject_name = self.subject.name if self.subject else "N/A"
        return f"{self.student} - {subject_name} ({self.exam_type})"

    def percentage(self):
        if self.total_marks and self.total_marks > 0:
            return float((self.obtained_marks / self.total_marks) * 100)
        return None
