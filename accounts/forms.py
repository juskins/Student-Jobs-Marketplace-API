from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, StudentProfile, EmployerProfile

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'role', 'first_name', 'last_name')

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'bio', 'profile_picture')

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ('full_name', 'phone_number', 'department', 'year_of_study', 'skills', 'resume', 'availability')

class EmployerProfileForm(forms.ModelForm):
    class Meta:
        model = EmployerProfile
        fields = ('organization_name', 'contact_person', 'phone_number', 'location', 'description')
