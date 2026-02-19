from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StudentProfileViewSet, EmployerProfileViewSet, UserRegistrationView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register(r'register', UserRegistrationView, basename='register')
router.register(r'student-profiles', StudentProfileViewSet)
router.register(r'employer-profiles', EmployerProfileViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
