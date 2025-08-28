from django import template
from tlcc_auth.conf import get

register = template.Library()

@register.simple_tag
def tlcc_auth_enabled(name):
    return get(name)
