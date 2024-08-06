# catalog/urls.py

from django.urls import path
from .views import flower_catalog, add_to_cart, view_cart, remove_from_cart, order_confirmation, order_history, repeat_order, add_review, reviews, flower_detail
from . import views

urlpatterns = [
    path('', flower_catalog, name='flower_catalog'),
    path('add-to-cart/<int:flower_id>/', add_to_cart, name='add_to_cart'),
    path('cart/', view_cart, name='view_cart'),
    path('order-confirmation/', order_confirmation, name='order_confirmation'),
    path('order-history/', order_history, name='order_history'),
    path('remove-from-cart/<int:item_id>/', remove_from_cart, name='remove_from_cart'),
    path('repeat-order/<int:order_id>/', repeat_order, name='repeat_order'),
    path('add-review/<int:order_id>/', views.add_review, name='add_review'),  # Новый маршрут
    path('reviews/', views.reviews, name='reviews'),
    path('flower/<int:flower_id>/', flower_detail, name='flower_detail'),
]