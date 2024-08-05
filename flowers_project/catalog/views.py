# Импорты
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Flower, CartItem, Order
from .forms import OrderForm
from aiogram import Bot
import logging
from asgiref.sync import sync_to_async
import threading
import asyncio

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Настройки бота
TELEGRAM_BOT_TOKEN = '7474070494:AAEMoP1LWznzTq0Kt2zULf606xVoLbtoD8k'
CHAT_ID = 48829372

# Асинхронная функция для отправки сообщений в Telegram
async def send_telegram_message(order, cart_items):
    bot = Bot(token=TELEGRAM_BOT_TOKEN)

    try:
        message = f"Новый заказ!\n\n" \
                  f"Пользователь: {order.user.username}\n" \
                  f"Адрес доставки: {order.delivery_address}\n" \
                  f"Дата и время доставки: {order.delivery_datetime}\n" \
                  f"Комментарий: {order.comment}\n\n" \
                  f"Товары:\n"

        for item in cart_items:
            message += f"- {item.flower.name} x {item.quantity} ({item.flower.price} руб.)\n"

        message += f"\nОбщая стоимость: {sum(item.total_price() for item in cart_items)} руб."

        await bot.send_message(chat_id=CHAT_ID, text=message)
        logger.info("Сообщение успешно отправлено в Telegram.")
    except Exception as ex:
        logger.error(f"Ошибка при отправке сообщения в Telegram: {ex}")
    finally:
        await bot.session.close()

# Функция для запуска асинхронной задачи в потоке
def run_async(func, *args):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(func(*args))

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

                # Удаляем товары из корзины
                cart_items.delete()

                # Запускаем асинхронное отправление сообщения в отдельном потоке
                threading.Thread(target=run_async, args=(send_telegram_message, order, cart_items)).start()

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
