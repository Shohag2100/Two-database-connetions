# connect_database/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

# Welcome page at root URL
urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Your API routes (only if myapp/urls.py exists)
    # path('api/', include('myapp.urls')),  # ← Comment this until you create myapp/urls.py
    
    path('api-auth/', include('rest_framework.urls')),
    
    # BEAUTIFUL WELCOME PAGE
    path('', TemplateView.as_view(template_name='welcome.html'), name='home'),
]

# Serve media files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)