# catalog/urls.py

from django.urls import path
from .views import flower_catalog, add_to_cart, view_cart, remove_from_cart, order_confirmation, order_history

urlpatterns = [
    path('', flower_catalog, name='flower_catalog'),
    path('add-to-cart/<int:flower_id>/', add_to_cart, name='add_to_cart'),
    path('cart/', view_cart, name='view_cart'),
    path('order-confirmation/', order_confirmation, name='order_confirmation'),
    path('order-history/', order_history, name='order_history'),  # Маршрут для истории заказов
    path('remove-from-cart/<int:item_id>/', remove_from_cart, name='remove_from_cart'),
]
