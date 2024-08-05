# catalog/views.py

from django.shortcuts import redirect, get_object_or_404
from .models import CartItem  # Предположим, что у вас есть модель CartItem для элементов корзины

from django.shortcuts import render, get_object_or_404, redirect  # Добавьте redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Flower, CartItem

def flower_catalog(request):
    flowers = Flower.objects.all()
    print(f"Количество цветов: {flowers.count()}")  # Вывод отладочной информации в консоль сервера
    return render(request, 'catalog/flower_catalog.html', {'flowers': flowers})

@login_required
def add_to_cart(request, flower_id):
    flower = get_object_or_404(Flower, id=flower_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, flower=flower)
    if not created:
        cart_item.quantity += 1
    cart_item.save()
    messages.success(request, f"Товар '{flower.name}' добавлен в корзину.")
    return redirect('flower_catalog')

@login_required
def view_cart(request):
    if request.method == 'POST':
        # Обновление количества товаров
        for item in CartItem.objects.filter(user=request.user):
            quantity = request.POST.get(f'quantity_{item.id}')
            if quantity:
                item.quantity = int(quantity)
                item.save()
        messages.success(request, "Корзина обновлена.")

    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.total_price() for item in cart_items)
    return render(request, 'catalog/cart.html', {'cart_items': cart_items, 'total': total})


def remove_from_cart(request, item_id):
    # Получаем элемент корзины или возвращаем 404, если его нет
    cart_item = get_object_or_404(CartItem, id=item_id)

    # Удаляем элемент из корзины
    cart_item.delete()

    # Перенаправляем обратно на страницу корзины
    return redirect('view_cart')
