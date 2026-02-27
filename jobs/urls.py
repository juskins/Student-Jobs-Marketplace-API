from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    JobViewSet, JobApplicationViewSet, 
    JobListView, JobDetailView, JobCreateView, JobUpdateView, JobDeleteView,
    StudentApplicationsView, JobApplicantsView, JobApplyView
)

router = DefaultRouter()
router.register(r'listings', JobViewSet, basename='job-api')
router.register(r'applications', JobApplicationViewSet, basename='application-api')

urlpatterns = [
    path('', JobListView.as_view(), name='job-list'),
    path('<int:pk>/', JobDetailView.as_view(), name='job-detail'),
    path('create/', JobCreateView.as_view(), name='job-create'),
    path('<int:pk>/update/', JobUpdateView.as_view(), name='job-update'),
    path('<int:pk>/delete/', JobDeleteView.as_view(), name='job-delete'),
    path('my-applications/', StudentApplicationsView.as_view(), name='student-applications'),
    path('<int:pk>/applicants/', JobApplicantsView.as_view(), name='job-applicants'),
    path('<int:pk>/apply/', JobApplyView.as_view(), name='job-apply'),
    path('api/', include(router.urls)),
]
