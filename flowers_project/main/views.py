# main/views.py

from django.shortcuts import render
from catalog.models import Flower  # Импортируйте модель Flower из приложения catalog

def home(request):
    flowers = Flower.objects.all()  # Загрузите все объекты Flower
    return render(request, 'main/home.html', {'flowers': flowers})  # Передайте их в шаблон
