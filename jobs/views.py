from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .forms import JobForm, JobApplicationForm
from django.shortcuts import get_object_or_404, render
from django.contrib import messages
from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Job, JobApplication
from .serializers import JobSerializer, JobApplicationSerializer

class HomeView(TemplateView):
    template_name = 'jobs/home.html'

class EmployerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        # Check if user is authenticated and is an employer
        if not (self.request.user.is_authenticated and self.request.user.role == 'employer'):
            return False
        
        # Check if they have actually completed their employer profile
        return hasattr(self.request.user, 'employer_profile')

    def handle_no_permission(self):
        if self.request.user.is_authenticated and self.request.user.role == 'employer':
            from django.contrib import messages
            messages.warning(self.request, "Please complete your Employer Profile details before posting or managing jobs.")
            return redirect('profile_edit')
        return super().handle_no_permission()

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

class StudentApplicationsView(LoginRequiredMixin, ListView):
    model = JobApplication
    template_name = 'jobs/student_applications.html'
    context_object_name = 'applications'

    def get_queryset(self):
        return JobApplication.objects.filter(student=self.request.user.student_profile).order_by('-applied_at')

class JobApplicantsView(LoginRequiredMixin, EmployerRequiredMixin, DetailView):
    model = Job
    template_name = 'jobs/job_applicants.html'
    context_object_name = 'job'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['applications'] = self.object.applications.all().order_by('-applied_at')
        return context

class JobApplyView(LoginRequiredMixin, CreateView):
    model = JobApplication
    form_class = JobApplicationForm
    template_name = 'jobs/job_apply.html'
    success_url = reverse_lazy('student-applications')

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != 'student':
            messages.error(request, "Only students can apply for jobs.")
            return redirect('job-detail', pk=self.kwargs['pk'])
        
        if not hasattr(request.user, 'student_profile'):
            messages.warning(request, "Please complete your Student Profile details before applying for jobs.")
            return redirect('profile_edit')
            
        # Prevent duplicate applications
        if JobApplication.objects.filter(student=request.user.student_profile, job_id=self.kwargs['pk']).exists():
            messages.info(request, "You have already applied for this job.")
            return redirect('job-detail', pk=self.kwargs['pk'])
            
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['job'] = get_object_or_404(Job, pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        form.instance.student = self.request.user.student_profile
        form.instance.job = get_object_or_404(Job, pk=self.kwargs['pk'])
        messages.success(self.request, f"Successfully applied for {form.instance.job.title}!")
        return super().form_valid(form)

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
