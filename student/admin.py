from django.contrib import admin
from .models import StudentInfo


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
        "guardian_phone",
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
                       "blood_group", "phone", "email", "profile_pic")
        }),
        ("Guardian Info", {
            "fields": ("guardian_name", "guardian_phone", "guardian_email",
                       "guardian_relation", "guardian_address")
        }),
        ("Address", {
            "fields": ("present_address", "permanent_address")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at")
        }),
    )
