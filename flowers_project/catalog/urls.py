# catalog/urls.py

from django.urls import path
from .views import flower_catalog  # Импорт функции представления

urlpatterns = [
    path('', flower_catalog, name='flower_catalog'),  # URL для доступа к представлению
]
