from django import template
import os

register = template.Library()

@register.filter(name='filebasename')
def filebasename(value):
    return os.path.basename(value)
