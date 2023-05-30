from django import template
from django.utils.timesince import timesince
from datetime import datetime
from django.utils import timezone

register = template.Library()

@register.filter
def hours_since(value):
    if timezone.is_aware(value):
        now = timezone.now()
    else:
        now = timezone.make_aware(timezone.now(), timezone.get_current_timezone())
    delta = now - value
    hours = delta.total_seconds() // 3600
    return int(hours)