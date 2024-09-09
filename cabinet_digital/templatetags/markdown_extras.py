from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
import markdown as md
import re

register = template.Library()

def add_image_class(html):
    pattern = r'<img(.*?)>'
    replacement = r'<img\1 class="img-fluid rounded" style="border-radius: 18px; width: 80%; height: auto; display: block; margin-left: auto; margin-right: auto;">'
    return re.sub(pattern, replacement, html)

@register.filter()
@stringfilter
def markdown(value):
    md_html = md.markdown(value, extensions=['fenced_code', 'tables', 'nl2br'])
    return mark_safe(add_image_class(md_html))