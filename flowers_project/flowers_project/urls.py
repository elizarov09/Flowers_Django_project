# flowers_project/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),  # Подключаем маршруты из приложения accounts
    path('', include('main.urls')),  # Основная страница или другая логика
]
