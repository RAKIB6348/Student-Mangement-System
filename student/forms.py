from django import forms

from .models import StudentFeedback


class StudentFeedbackForm(forms.ModelForm):
    class Meta:
        model = StudentFeedback
        fields = ["feedback"]
        widgets = {
            "feedback": forms.Textarea(
                attrs={
                    "rows": 4,
                    "class": "form-control",
                    "placeholder": "Share your feedback or concern...",
                }
            )
        }
