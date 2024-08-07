# flowers_project/urls.py

from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from catalog.admin import admin_site

urlpatterns = [
    path('admin/', admin_site.urls),
    path('accounts/', include('accounts.urls')),
    path('catalog/', include('catalog.urls')),
    path('', include('main.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)