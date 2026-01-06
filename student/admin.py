from django.contrib import admin
from .models import StudentInfo, StudentNotification, StudentFeedback, StudentLeave, StudentResult


@admin.register(StudentInfo)
class StudentInfoAdmin(admin.ModelAdmin):
    list_display = (
        "student_user_id",
        "user",
        "first_name",
        "last_name",
        "klass",
        "section",
        "session",
        "roll_no",
        "created_at",
    )
    search_fields = (
        "student_user_id",
        "admission_no",
        "first_name",
        "last_name",
        "phone",
        "father_name",
        "mother_name",
        "father_mobile",
        "mother_mobile",
        "user__username",
        "user__email",
    )
    
    readonly_fields = (
        "student_user_id",
        "admission_no",
        "created_at",
        "updated_at",
        # যদি roll_no non-editable হয় (editable=False), 
        # তাও এখানে রাখা safe (এখানে form-er অংশ না, শুধু read-only দেখাবে)
        "roll_no",
    )

    fieldsets = (
        ("User Link & IDs", {
            "fields": ("user", "student_user_id", "admission_no")
        }),
        ("Academic Info", {
            # roll_no এখানে থেকে তুলে দিলাম 👇
            "fields": ("session", "klass", "section")
        }),
        ("Personal Info", {
            "fields": ("first_name", "last_name", "gender", "date_of_birth",
                       "blood_group", "religion", "joining_date", "phone", "email", "profile_pic")
        }),
        ("Parent Info", {
            "fields": (
                "father_name",
                "father_occupation",
                "father_mobile",
                "father_email",
                "mother_name",
                "mother_occupation",
                "mother_mobile",
                "mother_email",
            )
        }),
        ("Address", {
            "fields": ("present_address", "permanent_address")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at")
        }),
    )


@admin.register(StudentNotification)
class StudentNotificationAdmin(admin.ModelAdmin):
    list_display = ("student", "subject", "created_at")
    search_fields = ("student__first_name", "student__last_name", "subject")
    autocomplete_fields = ("student",)


@admin.register(StudentFeedback)
class StudentFeedbackAdmin(admin.ModelAdmin):
    list_display = ("student", "created_at", "updated_at", "has_reply")
    search_fields = ("student__first_name", "student__last_name", "feedback")
    autocomplete_fields = ("student",)

    def has_reply(self, obj):
        return bool(obj.feedback_reply)

    has_reply.boolean = True


@admin.register(StudentLeave)
class StudentLeaveAdmin(admin.ModelAdmin):
    list_display = ("student", "leave_type", "start_date", "end_date", "status", "created_at")
    list_filter = ("leave_type", "status")
    search_fields = ("student__first_name", "student__last_name", "reason")
    autocomplete_fields = ("student",)


@admin.register(StudentResult)
class StudentResultAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "subject",
        "exam_type",
        "obtained_marks",
        "total_marks",
        "grade",
        "session",
        "recorded_at",
    )
    list_filter = ("exam_type", "session", "klass", "subject")
    search_fields = (
        "student__first_name",
        "student__last_name",
        "student__student_user_id",
        "subject__name",
    )
    autocomplete_fields = ("student", "session", "klass", "section", "subject")
