from django import forms

from student.models import StudentResult

from .models import TeacherLeave, Feedback, Assignment


class TeacherLeaveForm(forms.ModelForm):
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"})
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"})
    )

    class Meta:
        model = TeacherLeave
        fields = ["leave_type", "start_date", "end_date", "reason"]
        widgets = {
            "leave_type": forms.Select(attrs={"class": "form-control"}),
            "reason": forms.Textarea(
                attrs={"rows": 4, "class": "form-control", "placeholder": "Why do you need the leave?"}
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
            # Keep validation simple but user-friendly.
            raise forms.ValidationError("Start date cannot be later than end date.")

        return cleaned_data


class TeacherFeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
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


class StudentResultForm(forms.ModelForm):
    class Meta:
        model = StudentResult
        fields = [
            "student",
            "session",
            "klass",
            "section",
            "subject",
            "exam_type",
            "total_marks",
            "obtained_marks",
            "grade",
            "remarks",
        ]
        widgets = {
            "remarks": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "exam_type": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            existing_class = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing_class} form-control".strip()

        for name in ["total_marks", "obtained_marks"]:
            self.fields[name].widget = forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "min": "0"}
            )

    def clean(self):
        cleaned_data = super().clean()
        total = cleaned_data.get("total_marks")
        obtained = cleaned_data.get("obtained_marks")

        if total is not None and total <= 0:
            self.add_error("total_marks", "Total marks must be greater than zero.")

        if obtained is not None and obtained < 0:
            self.add_error("obtained_marks", "Obtained marks cannot be negative.")

        if (
            total is not None
            and obtained is not None
            and total > 0
            and obtained > total
        ):
            self.add_error(
                "obtained_marks",
                "Obtained marks cannot be greater than total marks.",
            )

        return cleaned_data

    def save(self, commit=True):
        result = super().save(commit=False)
        student = result.student

        if student:
            result.session = result.session or student.session
            result.klass = result.klass or student.klass
            result.section = result.section or student.section

        if commit:
            result.save()
        return result


class TeacherAssignmentForm(forms.ModelForm):
    due_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Assignment
        fields = [
            'title',
            'description',
            'klass',
            'section',
            'session',
            'subject',
            'due_date',
            'attachment',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            existing = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f"{existing} form-control".strip()
