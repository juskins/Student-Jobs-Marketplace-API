from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    JobViewSet, JobApplicationViewSet, 
    JobListView, JobDetailView, JobCreateView, JobUpdateView, JobDeleteView
)

router = DefaultRouter()
router.register(r'listings', JobViewSet, basename='job-api')
router.register(r'applications', JobApplicationViewSet, basename='application-api')

urlpatterns = [
    path('list/', JobListView.as_view(), name='job-list'),
    path('<int:pk>/', JobDetailView.as_view(), name='job-detail'),
    path('create/', JobCreateView.as_view(), name='job-create'),
    path('<int:pk>/update/', JobUpdateView.as_view(), name='job-update'),
    path('<int:pk>/delete/', JobDeleteView.as_view(), name='job-delete'),
    path('api/', include(router.urls)),
]
