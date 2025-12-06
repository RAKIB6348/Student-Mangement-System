from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('', include('account.urls')),
    path('administration/', include('administration.urls')),
    path('academic/', include('academic.urls')),
    path('student/', include('student.urls')),
    path('teacher/', include('teacher.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
