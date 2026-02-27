from django import forms
from .models import Job, JobApplication

class JobForm(forms.ModelForm):
    # ... existing JobForm code ...
    class Meta:
        model = Job
        fields = ['title', 'description', 'location', 'job_type', 'required_skills', 'salary', 'deadline', 'status']
        widgets = {
            'deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['cover_letter', 'resume']
        widgets = {
            'cover_letter': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Tell the employer why you are a good fit...'}),
        }
