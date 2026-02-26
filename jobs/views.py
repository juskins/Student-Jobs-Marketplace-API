from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect
from .forms import JobForm
from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Job, JobApplication
from .serializers import JobSerializer, JobApplicationSerializer

class EmployerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'employer'

class JobListView(ListView):
    model = Job
    template_name = 'jobs/job_list.html'
    context_object_name = 'jobs'
    paginate_by = 10

    def get_queryset(self):
        return Job.objects.filter(status='open').order_by('-created_at')

class JobDetailView(DetailView):
    model = Job
    template_name = 'jobs/job_detail.html'
    context_object_name = 'job'

class JobCreateView(LoginRequiredMixin, EmployerRequiredMixin, CreateView):
    model = Job
    form_class = JobForm
    template_name = 'jobs/job_form.html'
    success_url = reverse_lazy('job-list')

    def form_valid(self, form):
        form.instance.employer = self.request.user.employer_profile
        return super().form_valid(form)

class JobUpdateView(LoginRequiredMixin, EmployerRequiredMixin, UpdateView):
    model = Job
    form_class = JobForm
    template_name = 'jobs/job_form.html'
    success_url = reverse_lazy('job-list')

    def get_queryset(self):
        return Job.objects.filter(employer=self.request.user.employer_profile)

class JobDeleteView(LoginRequiredMixin, EmployerRequiredMixin, DeleteView):
    model = Job
    template_name = 'jobs/job_confirm_delete.html'
    success_url = reverse_lazy('job-list')

    def get_queryset(self):
        return Job.objects.filter(employer=self.request.user.employer_profile)

# DRF ViewSets stay below...

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
