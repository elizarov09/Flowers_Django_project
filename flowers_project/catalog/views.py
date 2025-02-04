# Импорты
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Flower, CartItem, Order, OrderItem, Review
from .forms import OrderForm, ReviewForm
from django.db.models import Avg
import requests
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Настройки бота
TELEGRAM_BOT_TOKEN = '7474070494:AAEMoP1LWznzTq0Kt2zULf606xVoLbtoD8k'
CHAT_ID = 48829372

# Синхронная функция для отправки сообщений в Telegram
def send_telegram_message(order, cart_items):
    try:
        message = f"Новый заказ!\n\n" \
                  f"Пользователь: {order.user.username}\n" \
                  f"Адрес доставки: {order.delivery_address}\n" \
                  f"Дата доставки: {order.delivery_date}\n" \
                  f"Время доставки: {order.delivery_time}\n" \
                  f"Комментарий: {order.comment or 'Нет комментария'}\n\n" \
                  f"Товары:\n"

        total_cost = 0

        for item in cart_items:
            # Логирование для проверки наличия элементов в корзине
            logger.info(f"Обработка элемента корзины: {item.flower.name}, Количество: {item.quantity}, Цена: {item.flower.price}")

            # Добавление информации о товаре в сообщение
            message += f"- {item.flower.name} x {item.quantity} ({item.flower.price} руб.)\n"
            total_cost += item.total_price()

        message += f"\nОбщая стоимость: {total_cost} руб."

        # Отправка текстового сообщения с информацией о заказе
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": message}
        response = requests.post(url, data=data)

        if response.status_code == 200:
            logger.info("Сообщение успешно отправлено в Telegram.")
        else:
            logger.error(f"Ошибка при отправке сообщения в Telegram: {response.text}")
    except Exception as ex:
        logger.error(f"Ошибка при отправке сообщения в Telegram: {ex}")

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