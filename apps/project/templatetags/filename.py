import os

from django import template

register = template.Library()


@register.filter
def filename(full_path):
    return os.path.basename(full_path)
