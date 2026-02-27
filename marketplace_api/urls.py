from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from jobs.views import HomeView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),
    path('accounts/', include('accounts.urls')),
    path('jobs/', include('jobs.urls')),
    path('api/accounts/', include('accounts.urls')),
    path('api/jobs/', include('jobs.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
