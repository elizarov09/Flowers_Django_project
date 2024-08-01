# catalog/views.py

from django.shortcuts import render
from .models import Flower  # Убедитесь, что импорт правильный

def flower_catalog(request):
    flowers = Flower.objects.all()  # Получение всех букетов из базы данных
    return render(request, 'catalog/flower_catalog.html', {'flowers': flowers})
