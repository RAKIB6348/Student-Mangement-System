from django.db import models
from account.models import User
from academic.models import Class, Section, Session, Subject
from student.models import StudentInfo

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
        verbose_name_plural = "Teacher" 
        

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
    subject = models.CharField(max_length=250, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Notifications"

    def __str__(self):
        return f"{self.teacher_id.first_name} {self.teacher_id.last_name}"


# ============================ leave =============================

class TeacherLeave(models.Model):
    LEAVE_TYPE = (
        ("Casual", "Casual"),
        ("Sick", "Sick"),
        ("Annual", "Annual"),
        ("Paid", "Paid Leave"),
        ("Unpaid", "Unpaid Leave"),
    )
    
    STATUS = (
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
    )
    
    teacher = models.ForeignKey(
        TeacherInfo,
        on_delete=models.CASCADE
    )
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    
    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="Pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.teacher.first_name} {self.teacher.last_name}"
    



 # =================== Teacher Feedback =========================

class Feedback(models.Model):
    teacher = models.ForeignKey(
        TeacherInfo,
        on_delete=models.CASCADE,
        related_name="feedback_entries"
    )
    feedback = models.TextField()
    feedback_reply = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.teacher.first_name} {self.teacher.last_name}"


class Attendance(models.Model):
    teacher = models.ForeignKey(
        TeacherInfo,
        on_delete=models.CASCADE,
        related_name="attendance_sessions",
    )
    klass = models.ForeignKey(
        Class,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="attendances",
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="attendances",
    )
    session = models.ForeignKey(
        Session,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="attendances",
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="attendances",
    )
    date = models.DateField()
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('teacher', 'klass', 'section', 'session', 'subject', 'date')
        ordering = ['-date', '-created_at']
        verbose_name = "Attendance Entry"
        verbose_name_plural = "Attendance Entries"

    def __str__(self):
        klass_name = self.klass.name if self.klass else "N/A"
        subject_name = self.subject.name if self.subject else "No Subject"
        return f"{self.date} - {klass_name} ({subject_name})"


class AttendanceRecord(models.Model):
    STATUS_PRESENT = "Present"
    STATUS_ABSENT = "Absent"

    STATUS_CHOICES = [
        (STATUS_PRESENT, "Present"),
        (STATUS_ABSENT, "Absent"),
    ]

    attendance = models.ForeignKey(
        Attendance,
        on_delete=models.CASCADE,
        related_name="records",
    )
    student = models.ForeignKey(
        StudentInfo,
        on_delete=models.CASCADE,
        related_name="attendance_records",
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_PRESENT,
    )
    remark = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    marked_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('attendance', 'student')
        ordering = ['student__roll_no', 'student__first_name']
        verbose_name = "Attendance Record"
        verbose_name_plural = "Attendance Records"

    def __str__(self):
        return f"{self.student} - {self.attendance.date} ({self.status})"


class Assignment(models.Model):
    teacher = models.ForeignKey(
        TeacherInfo,
        on_delete=models.CASCADE,
        related_name="assignments",
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    klass = models.ForeignKey(
        Class,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assignments",
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assignments",
    )
    session = models.ForeignKey(
        Session,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assignments",
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assignments",
    )
    due_date = models.DateField()
    attachment = models.FileField(upload_to='assignments/resources/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.klass} - {self.subject})"


class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name="submissions",
    )
    student = models.ForeignKey(
        StudentInfo,
        on_delete=models.CASCADE,
        related_name="assignment_submissions",
    )
    submission_file = models.FileField(upload_to='assignments/submissions/', blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('assignment', 'student')
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.assignment.title} - {self.student.first_name}"
