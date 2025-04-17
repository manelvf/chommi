from datetime import date
from celery import shared_task
from django.utils.translation import gettext_lazy as _

from .models import Gambler


@shared_task
def check_expired_subscriptions():
    """
    Check if any Gambler's subscription_date is earlier than the current date,
    and if so, change their status to "Expired".
    """
    today = date.today()
    
    # Get all active gamblers with subscription_date earlier than today
    expired_gamblers = Gambler.objects.filter(
        status="AC",  # Only check active gamblers
        subscription_date__lt=today  # subscription_date is less than today
    )
    
    # Update their status to "Expired"
    count = expired_gamblers.update(status="EX")
    
    return f"Updated {count} gamblers to Expired status"
