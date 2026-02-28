from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm, UserProfileForm, StudentProfileForm, EmployerProfileForm
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import User, StudentProfile, EmployerProfile
from .serializers import UserSerializer, StudentProfileSerializer, EmployerProfileSerializer

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user

class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        response = super().form_valid(form)
        # We could auto-login here, but success_url points to login
        return response

@login_required
def profile(request):
    user = request.user
    if user.role == 'student':
        profile_data = getattr(user, 'student_profile', None)
    else:
        profile_data = getattr(user, 'employer_profile', None)
    
    return render(request, 'accounts/profile.html', {
        'user': user,
        'profile': profile_data
    })

@login_required
def profile_edit(request):
    user = request.user
    if user.role == 'student':
        profile_instance = getattr(user, 'student_profile', None)
        ProfileFormClass = StudentProfileForm
    else:
        profile_instance = getattr(user, 'employer_profile', None)
        ProfileFormClass = EmployerProfileForm

    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, request.FILES, instance=user)
        profile_form = ProfileFormClass(request.POST, request.FILES, instance=profile_instance)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            # Save profile without committing to associate with user if it's new
            new_profile = profile_form.save(commit=False)
            if profile_instance is None:
                new_profile.user = user
            new_profile.save()
            return redirect('profile')
    else:
        user_form = UserProfileForm(instance=user)
        profile_form = ProfileFormClass(instance=profile_instance)

    return render(request, 'accounts/profile_edit.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

class UserRegistrationView(viewsets.GenericViewSet, viewsets.mixins.CreateModelMixin):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

class StudentProfileViewSet(viewsets.ModelViewSet):
    queryset = StudentProfile.objects.all()
    serializer_class = StudentProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'employer':
            # Employers should only view student profiles when an application is submitted.
            # This logic will be handled more specifically in JobApplication views, 
            # but for this ViewSet, we restricted it to the student's own profile 
            # OR if the employers needs it. For now, let's stick to the requirement:
            # "Employers should only view student profiles when an application is submitted."
            return StudentProfile.objects.filter(applications__job__employer__user=user).distinct()
        return StudentProfile.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class EmployerProfileViewSet(viewsets.ModelViewSet):
    queryset = EmployerProfile.objects.all()
    serializer_class = EmployerProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
