# catalog/admin.py

from django.contrib import admin
from .models import Flower, CartItem, Order

@admin.register(Flower)
class FlowerAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')
    search_fields = ('name',)

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'flower', 'quantity')
    search_fields = ('user__username', 'flower__name')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'delivery_address', 'get_status_display', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__username', 'delivery_address')
    ordering = ('-created_at',)
