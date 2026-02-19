from rest_framework import serializers
from .models import Job, JobApplication
from accounts.serializers import EmployerProfileSerializer, StudentProfileSerializer

class JobSerializer(serializers.ModelSerializer):
    employer = EmployerProfileSerializer(read_only=True)

    class Meta:
        model = Job
        fields = '__all__'

class JobApplicationSerializer(serializers.ModelSerializer):
    student = StudentProfileSerializer(read_only=True)
    job = JobSerializer(read_only=True)
    job_id = serializers.PrimaryKeyRelatedField(
        queryset=Job.objects.all(), source='job', write_only=True
    )

    class Meta:
        model = JobApplication
        fields = ('id', 'student', 'job', 'job_id', 'cover_letter', 'resume', 'applied_at', 'status')
        read_only_fields = ('applied_at', 'status', 'student')

    def validate(self, data):
        student = self.context['request'].user.student_profile
        job = data['job']
        if JobApplication.objects.filter(student=student, job=job).exists():
            raise serializers.ValidationError("You have already applied for this job.")
        return data
