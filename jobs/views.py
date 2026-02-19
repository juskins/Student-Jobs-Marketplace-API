from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Job, JobApplication
from .serializers import JobSerializer, JobApplicationSerializer

class IsEmployer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'employer'

class IsStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'student'

class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['job_type', 'location', 'deadline']
    search_fields = ['title', 'description', 'required_skills']
    ordering_fields = ['created_at', 'salary', 'deadline']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsEmployer()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(employer=self.request.user.employer_profile)

class JobApplicationViewSet(viewsets.ModelViewSet):
    queryset = JobApplication.objects.all()
    serializer_class = JobApplicationSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsStudent()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'student':
            return JobApplication.objects.filter(student=user.student_profile)
        elif user.role == 'employer':
            return JobApplication.objects.filter(job__employer=user.employer_profile)
        return JobApplication.objects.none()

    def perform_create(self, serializer):
        serializer.save(student=self.request.user.student_profile)

    def update(self, request, *args, **kwargs):
        # Only employers can update status
        if request.user.role != 'employer':
            return Response({"detail": "Only employers can update application status."}, 
                            status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)
