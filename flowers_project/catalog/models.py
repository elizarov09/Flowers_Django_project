# catalog/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

class Flower(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    image = models.ImageField(upload_to='flowers/', blank=True, null=True, verbose_name="Изображение")

    def __str__(self):
        return self.name

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    flower = models.ForeignKey(Flower, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.flower.name} x {self.quantity}"

    def total_price(self):
        return self.flower.price * self.quantity

class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Ожидает обработки'),
        ('PROCESSING', 'В обработке'),
        ('SHIPPING', 'В доставке'),
        ('COMPLETED', 'Выполнен'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', verbose_name="Статус")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    delivery_address = models.CharField(max_length=255)
    delivery_date = models.DateField(default=timezone.now)
    delivery_time = models.TimeField(default=timezone.now)  # Добавляем время доставки
    comment = models.TextField(blank=True, null=True, verbose_name="Комментарий")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Order {self.id} by {self.user.username}'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    flower = models.ForeignKey(Flower, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.flower.name} x {self.quantity}"

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='reviews')
    text = models.TextField(verbose_name="Отзыв", default="")  # Добавьте default=""
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Review by {self.user.username} for Order {self.order.id}'

class FlowerRating(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='flower_ratings')
    flower = models.ForeignKey(Flower, on_delete=models.CASCADE, related_name='ratings')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Рейтинг"
    )

    def __str__(self):
        return f'Rating {self.rating} for {self.flower.name} in Review {self.review.id}'