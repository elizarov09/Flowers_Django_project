from celery import shared_task
from .utils import update_daily_report

@shared_task
def update_daily_report_task():
    update_daily_report()
    return "Daily report updated successfully"