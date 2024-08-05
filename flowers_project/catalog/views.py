# Импорты
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Flower, CartItem, Order
from .forms import OrderForm
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
    flowers = Flower.objects.all()
    print(f"Количество цветов: {flowers.count()}")  # Отладочная информация
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
