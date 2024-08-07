# Импорты
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Flower, CartItem, Order, OrderItem, Review
from .forms import OrderForm, ReviewForm
from django.db.models import Avg
from django.contrib.auth.decorators import user_passes_test
from django.db.models import F, Sum
from django.utils import timezone
from datetime import datetime, timedelta
from .utils import send_telegram_message

# Настройка логирования
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Основные представления
def flower_catalog(request):
    flowers = Flower.objects.annotate(avg_rating=Avg('ratings__rating'))
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
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.total_price() for item in cart_items)

    if request.method == 'POST':
        # Обновление количества товаров
        for item in cart_items:
            quantity = request.POST.get(f'quantity_{item.id}')
            if quantity:
                item.quantity = int(quantity)
                item.save()

        # Проверка на оформление заказа
        if 'place_order' in request.POST:
            order_form = OrderForm(request.POST)
            if order_form.is_valid():
                order = order_form.save(commit=False)
                order.user = request.user
                order.save()

                # Сохранение товаров в OrderItem
                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        flower=item.flower,
                        quantity=item.quantity
                    )

                # Отправка информации в Telegram
                send_telegram_message(order, cart_items)

                # Удаляем товары из корзины после отправки сообщения
                cart_items.delete()

                messages.success(request, "Ваш заказ успешно оформлен!")
                return redirect('order_confirmation')
        else:
            order_form = OrderForm()

        messages.success(request, "Корзина обновлена.")

    else:
        order_form = OrderForm()

    return render(request, 'catalog/cart.html', {
        'cart_items': cart_items,
        'total': total,
        'order_form': order_form
    })

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.delete()
    return redirect('view_cart')

def order_confirmation(request):
    return render(request, 'catalog/order_confirmation.html')


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'catalog/order_history.html', {'orders': orders})


# catalog/views.py

# catalog/views.py

@login_required
def repeat_order(request, order_id):
    # Получаем оригинальный заказ
    original_order = get_object_or_404(Order, id=order_id, user=request.user)

    logger.info(f"Повтор заказа: {original_order.id}, Пользователь: {original_order.user.username}")

    # Удаляем текущие товары из корзины пользователя
    CartItem.objects.filter(user=request.user).delete()

    # Добавляем товары из OrderItem в корзину
    for item in original_order.order_items.all():
        logger.info(f"Добавление товара в корзину: {item.flower.name}, Количество: {item.quantity}")
        CartItem.objects.create(
            user=request.user,
            flower=item.flower,
            quantity=item.quantity
        )

    messages.success(request, "Товары из заказа добавлены в вашу корзину.")
    return redirect('view_cart')


@login_required
def add_review(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.order = order
            review.user = request.user
            review.save()

            # Сохранение рейтингов для каждого букета в заказе
            for item in order.order_items.all():
                rating = request.POST.get(f'rating_{item.flower.id}')
                if rating:
                    review.flower_ratings.create(flower=item.flower, rating=int(rating))

            messages.success(request, "Ваш отзыв успешно добавлен.")
            return redirect('order_history')
    else:
        form = ReviewForm()

    return render(request, 'catalog/add_review.html', {
        'form': form,
        'order': order
    })

def reviews(request):
    reviews = Review.objects.all().order_by('-created_at')
    return render(request, 'catalog/reviews.html', {'reviews': reviews})


def flower_detail(request, flower_id):
    flower = get_object_or_404(Flower.objects.annotate(avg_rating=Avg('ratings__rating')), id=flower_id)
    reviews = Review.objects.filter(flower_ratings__flower=flower).order_by('-created_at')
    return render(request, 'catalog/flower_detail.html', {'flower': flower, 'reviews': reviews})

# Функция проверки, является ли пользователь администратором
def is_admin(user):
    return user.is_authenticated and user.is_staff


@user_passes_test(is_admin)
def admin_report(request):
    # Получаем параметры даты из запроса или используем последние 30 дней по умолчанию
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    if start_date_str and end_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    else:
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)

    # Фильтруем заказы за выбранный период
    orders = Order.objects.filter(created_at__date__range=[start_date, end_date])

    # Рассчитываем метрики
    order_data = orders.annotate(
        total_price=Sum(F('order_items__flower__price') * F('order_items__quantity'))
    ).values('id', 'user__username', 'created_at', 'total_price', 'status')

    daily_revenue = sum(order['total_price'] or 0 for order in order_data)
    order_count = len(order_data)
    average_order_value = daily_revenue / order_count if order_count > 0 else 0

    context = {
        'start_date': start_date,
        'end_date': end_date,
        'daily_revenue': daily_revenue,
        'order_count': order_count,
        'average_order_value': average_order_value,
        'orders': order_data,
    }

    return render(request, 'catalog/admin_report.html', context)