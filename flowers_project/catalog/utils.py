import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

def send_telegram_message(order, cart_items):
    try:
        message = f"Заказ №{order.id}\nСтатус заказа: {order.get_status_display()}\n\n" \
                  f"Пользователь: {order.user.username}\n" \
                  f"Адрес доставки: {order.delivery_address}\n" \
                  f"Дата доставки: {order.delivery_date}\n" \
                  f"Время доставки: {order.delivery_time}\n" \
                  f"Комментарий: {order.comment or 'Нет комментария'}\n\n" \
                  f"Товары:\n"

        total_cost = 0

        for item in cart_items:
            logger.info(f"Обработка элемента корзины: {item.flower.name}, Количество: {item.quantity}, Цена: {item.flower.price}")
            message += f"- {item.flower.name} x {item.quantity} ({item.flower.price} руб.)\n"
            total_cost += item.total_price()

        message += f"\nОбщая стоимость: {total_cost} руб."

        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {"chat_id": settings.CHAT_ID, "text": message}
        response = requests.post(url, data=data)

        if response.status_code == 200:
            logger.info("Сообщение успешно отправлено в Telegram.")
        else:
            logger.error(f"Ошибка при отправке сообщения в Telegram: {response.text}")
    except Exception as ex:
        logger.error(f"Ошибка при отправке сообщения в Telegram: {ex}")

def send_order_status_update(order):
    try:
        message = f"Обновление статуса заказа №{order.id}\n" \
                  f"Новый статус: {order.get_status_display()}\n\n" \
                  f"Пользователь: {order.user.username}\n" \
                  f"Адрес доставки: {order.delivery_address}\n" \
                  f"Дата доставки: {order.delivery_date}\n" \
                  f"Время доставки: {order.delivery_time}\n" \
                  f"Комментарий: {order.comment or 'Нет комментария'}\n\n" \
                  f"Товары:\n"

        total_cost = 0

        for item in order.order_items.all():
            logger.info(f"Обработка элемента заказа: {item.flower.name}, Количество: {item.quantity}, Цена: {item.flower.price}")
            message += f"- {item.flower.name} x {item.quantity} ({item.flower.price} руб.)\n"
            total_cost += item.quantity * item.flower.price

        message += f"\nОбщая стоимость: {total_cost} руб."

        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {"chat_id": settings.CHAT_ID, "text": message}
        response = requests.post(url, data=data)

        if response.status_code == 200:
            logger.info(f"Сообщение об обновлении статуса заказа №{order.id} успешно отправлено в Telegram.")
        else:
            logger.error(f"Ошибка при отправке сообщения об обновлении статуса в Telegram: {response.text}")
    except Exception as ex:
        logger.error(f"Ошибка при отправке сообщения об обновлении статуса в Telegram: {ex}")