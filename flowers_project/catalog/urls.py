# catalog/urls.py

from django.urls import path
from .views import flower_catalog, add_to_cart, view_cart

urlpatterns = [
    path('', flower_catalog, name='flower_catalog'),
    path('add-to-cart/<int:flower_id>/', add_to_cart, name='add_to_cart'),
    path('cart/', view_cart, name='view_cart'),
]
