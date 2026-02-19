from django.db import models
from accounts.models import EmployerProfile, StudentProfile

class Job(models.Model):
    LOCATION_CHOICES = (
        ('on-campus', 'On-campus'),
        ('nearby', 'Nearby'),
    )
    JOB_TYPE_CHOICES = (
        ('part-time', 'Part-time'),
        ('internship', 'Internship'),
        ('temporary', 'Temporary'),
    )
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('closed', 'Closed'),
    )

    employer = models.ForeignKey(EmployerProfile, on_delete=models.CASCADE, related_name='jobs')
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=20, choices=LOCATION_CHOICES)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES)
    required_skills = models.TextField()
    salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    deadline = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')

    def __str__(self):
        return self.title

class JobApplication(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='applications')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    cover_letter = models.TextField(blank=True, null=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True) # Or URLField if external
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')

    class Meta:
        unique_together = ('student', 'job')

    def __str__(self):
        return f"{self.student.full_name} - {self.job.title}"
