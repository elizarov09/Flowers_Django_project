from django.db.models import Sum, Avg
from django.utils import timezone
from catalog.models import Order
from .models import DailyReport

def update_daily_report():
    today = timezone.now().date()
    orders = Order.objects.filter(created_at__date=today)

    total_orders = orders.count()
    pending_orders = orders.filter(status='PENDING').count()
    processing_orders = orders.filter(status='PROCESSING').count()
    shipping_orders = orders.filter(status='SHIPPING').count()
    completed_orders = orders.filter(status='COMPLETED').count()

    total_revenue = orders.aggregate(Sum('order_items__flower__price'))['order_items__flower__price__sum'] or 0
    average_check = total_revenue / total_orders if total_orders > 0 else 0

    report, created = DailyReport.objects.update_or_create(
        date=today,
        defaults={
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'processing_orders': processing_orders,
            'shipping_orders': shipping_orders,
            'completed_orders': completed_orders,
            'total_revenue': total_revenue,
            'average_check': average_check,
        }
    )

    return report