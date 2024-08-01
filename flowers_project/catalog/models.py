# catalog/models.py

from django.db import models

class Flower(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    image = models.ImageField(upload_to='flowers/', blank=True, null=True, verbose_name="Изображение")

    def __str__(self):
        return self.name
