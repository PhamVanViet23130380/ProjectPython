from django import template
from django.contrib.humanize.templatetags.humanize import intcomma

register = template.Library()


@register.filter
def intdot(value):
    """Format number with dot as thousands separator."""
    try:
        return intcomma(value).replace(',', '.')
    except Exception:
        return value
