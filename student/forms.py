from django import forms
from django.core.exceptions import ValidationError

from .models import StudentFeedback, StudentLeave
from teacher.models import AssignmentSubmission


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


class StudentLeaveForm(forms.ModelForm):
    start_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))

    class Meta:
        model = StudentLeave
        fields = ["leave_type", "start_date", "end_date", "reason"]
        widgets = {
            "leave_type": forms.Select(attrs={"class": "form-control"}),
            "reason": forms.Textarea(
                attrs={
                    "rows": 4,
                    "class": "form-control",
                    "placeholder": "Why do you need the leave?",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ["start_date", "end_date"]:
            self.fields[field].widget.attrs.update({"class": "form-control"})

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start_date")
        end = cleaned_data.get("end_date")
        if start and end and start > end:
            raise forms.ValidationError("Start date cannot be later than end date.")
        return cleaned_data


class AssignmentSubmissionForm(forms.ModelForm):
    class Meta:
        model = AssignmentSubmission
        fields = ['submission_file', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['submission_file'].widget.attrs.update({
            'class': 'form-control-file',
            'accept': 'application/pdf,.pdf',
        })

    def clean_submission_file(self):
        file = self.cleaned_data.get('submission_file')
        if not file:
            return file
        content_type = getattr(file, 'content_type', '')
        if not file.name.lower().endswith('.pdf') or (content_type and content_type != 'application/pdf'):
            raise ValidationError('Please upload a PDF file.')
        return file
