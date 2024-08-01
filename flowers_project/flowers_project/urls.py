# flowers_project/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('catalog/', include('catalog.urls')),  # Каталог, если он нужен отдельно
    path('', include('main.urls')),  # Главная страница
]
