from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('employer', 'Employer'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return self.email

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    department = models.CharField(max_length=255)
    year_of_study = models.IntegerField()
    skills = models.TextField()
    resume_url = models.URLField(blank=True, null=True)
    availability = models.TextField()

    def __str__(self):
        return self.full_name

class EmployerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employer_profile')
    organization_name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    location = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.organization_name
